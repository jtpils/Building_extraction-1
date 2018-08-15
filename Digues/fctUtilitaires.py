# -*- coding: utf-8 -*-

import bisect
import os
import pickle
import shelve
import shutil
import sys
import arcpy
import arcpy.sa
import numpy
import pandas
import scipy
from openpyxl import load_workbook


def save_variables(filename):
    my_shelf = open(filename, 'n')
    for key in dir():
        try:
            my_shelf[key] = globals()[key]
        except TypeError:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            print('ERROR shelving: {0}'.format(key))
    my_shelf.close()


def load_variables(lst, filename):
    f = open(filename, 'rb')
    for l in lst:
        pickle.dump(l, f)
    f.close()


def water_depth_max(in_ras_heau, in_bat_layer, in_line_bat, in_cent_layer):
    # Process: Extract by Mask
    extract_raster_line_tif = 'ExtractRaster_line'
    arcpy.gp.ExtractByMask_sa(in_ras_heau, in_line_bat, extract_raster_line_tif)

    # Process: Zonal Statistics (2)
    zonal_st_max_tif = 'ZonalSt_max'
    oid = arcpy.Describe(in_line_bat).OIDFieldName
    arcpy.gp.ZonalStatistics_sa(in_line_bat, oid, extract_raster_line_tif, zonal_st_max_tif, "MAXIMUM", "DATA")

    # TODO trouver pourquoi ca plante avec les rasters de hauteur d'eau de Khalid
    # Process: Zonal Statistics (5)
    zonal_st_max2_tif = 'ZonalSt_max2'
    oid = arcpy.Describe(in_bat_layer).OIDFieldName
    arcpy.gp.ZonalStatistics_sa(in_bat_layer, oid, zonal_st_max_tif, zonal_st_max2_tif, "MEAN", "DATA")

    # Process: Int
    zonal_st_integer_tif = 'ZonalSt_integer'
    arcpy.gp.Int_sa(zonal_st_max2_tif, zonal_st_integer_tif)

    # Process: Raster to Polygon
    raster_to_p_tif1_shp = 'RasterToP_tif1'
    arcpy.RasterToPolygon_conversion(zonal_st_integer_tif, raster_to_p_tif1_shp, "NO_SIMPLIFY", "VALUE")

    # Process: Select Layer By Location
    arcpy.SelectLayerByLocation_management(in_cent_layer, "INTERSECT", raster_to_p_tif1_shp, "", "NEW_SELECTION")

    # Process: Extract Values to Points (2)
    centroides_he_max = 'Centroides_HEmax'
    arcpy.gp.ExtractValuesToPoints_sa(in_cent_layer, zonal_st_max2_tif, centroides_he_max, "NONE", "VALUE_ONLY")

    return centroides_he_max


def supp_dossier_scratch():
    """
    Fonction qui supprime le dossier 'scratch' créé par ArcGIS lors
    de l'utilisation de arcpy.env.scratchFolder. Supprime le dossier
    seulement lorsqu'il est dans le dossier Temp de Windows.

    """
    tempdir = os.path.join(os.environ["TEMP"], "scratch")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)


def clean_scratch_dir():
    tempdir = os.path.join(os.environ["TEMP"], "ScratchGARI.gdb")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)


def get_scratch_dir():
    scratch_dir = arcpy.env.scratchWorkspace
    if not scratch_dir:
        if "TEMP" not in os.environ:
            arcpy.AddError("No temporary directory to write scratch data. Please set your scratch workspace")
            sys.exit(1)
        tempdir = os.environ["TEMP"]
        if not os.path.exists(os.path.join(tempdir, "ScratchGARI.gdb")):
            result = arcpy.CreateFileGDB_management(tempdir, "ScratchGARI")
            if result.status == 4:
                scratch_dir = os.path.join(tempdir, "ScratchGARI.gdb")
            else:
                scratch_dir = tempdir
        else:
            scratch_dir = os.path.join(tempdir, "ScratchGARI.gdb")
    return scratch_dir


def get_batiments_isoles(rr_dataset, centroides_batiments, point_depart, clip_rr_zi, id_field):
    # NETWORK ANALYST #######################################################################
    # Process: Make Closest Facility Layer
    out_na_layer = arcpy.MakeClosestFacilityLayer_na(rr_dataset, "Closest Facility 2", "Length", "TRAVEL_TO", "", "1", "", "ALLOW_UTURNS", "", "NO_HIERARCHY", "", "STRAIGHT_LINES", "", "NOT_USED")
    ########################
    # Get the layer object from the result object. The route layer can now be
    # referenced using the layer object.
    out_na_layer = out_na_layer.getOutput(0)
    ########################
    # Process: Add Locations
    arcpy.AddLocations_na(out_na_layer, "Incidents", centroides_batiments, "", "5000 Meters", "", "Reseau_routier_SJSR SHAPE;Reseau_SJSR_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
                          "Reseau_routier_SJSR #;Reseau_SJSR_ND_Junctions #")
    # Process: Add Locations (3)
    arcpy.AddLocations_na(out_na_layer, "Facilities", point_depart, "Name Name #", "5000 Meters", "", "Reseau_routier_SJSR SHAPE;Reseau_SJSR_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
                          "Reseau_routier_SJSR #;Reseau_SJSR_ND_Junctions #")
    # Process: Add Locations (4)
    arcpy.AddLocations_na(out_na_layer, "Line Barriers", clip_rr_zi, "", "5000 Meters", "", "Reseau_routier_SJSR SHAPE;Reseau_SJSR_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
                          "Reseau_routier_SJSR #;Reseau_SJSR_ND_Junctions #")
    # Process: Solve
    arcpy.Solve_na(out_na_layer, "SKIP", "TERMINATE", "")
    ########################
    # List sublayers in NALayer Group and export each
    for lyr in arcpy.mapping.ListLayers(out_na_layer):
        if lyr.isGroupLayer:
            continue
        if lyr.name == "Routes":
            arcpy.CopyFeatures_management(lyr, os.path.join(arcpy.env.workspace, lyr.name))
    ########################

    # GEOTRAITEMENTS #######################################################################
    # Conversion des vertex des trajets en points et selection inverse pour selectionner
    # les batiments inaccessibles par la route
    in_routes = os.path.join(arcpy.env.workspace, "Routes")
    r_vertex = 'RVertex'
    arcpy.FeatureVerticesToPoints_management(in_routes, r_vertex, "ALL")
    r_vertex_layer = 'RVertexLayer'
    cent_layer = 'CentLayer'
    arcpy.MakeFeatureLayer_management(r_vertex, r_vertex_layer)
    arcpy.MakeFeatureLayer_management(centroides_batiments, cent_layer)
    arcpy.SelectLayerByLocation_management(cent_layer, "INTERSECT", r_vertex_layer)
    arcpy.SelectLayerByAttribute_management(cent_layer, "SWITCH_SELECTION")

    # Listes des ID des batiments isoles + zone inondee (inaccessibles car segments de routes inondes)
    list_isole_zi = []
    rows = arcpy.da.SearchCursor(cent_layer, [id_field])
    for row in rows:
        list_isole_zi.append(row[0])
    del rows

    return list_isole_zi


def add_mapping(field_name, existing_mapping, new_mapping):
    mapping_index = existing_mapping.findFieldMapIndex(field_name)
    # required fields (OBJECTID, etc) will not be in existing mappings
    # they are added automatically
    if mapping_index != -1:
        field_map = existing_mapping.fieldMappings[mapping_index]
        new_mapping.addFieldMap(field_map)
    return new_mapping


def reorder_fields(table, out_table, field_order, add_missing=True):
    """
    Reorders fields in input featureclass/table
    :table:         input table (fc, table, layer, etc)
    :out_table:     output table (fc, table, layer, etc)
    :field_order:   order of fields (objectid, shape not necessary)
    :add_missing:   add missing fields to end if True (leave out if False)
    -> path to output table
    """
    existing_fields = arcpy.ListFields(table)
    existing_field_names = [field.name for field in existing_fields]

    existing_mapping = arcpy.FieldMappings()
    existing_mapping.addTable(table)

    new_mapping = arcpy.FieldMappings()

    # add user fields from field_order
    for field_name in field_order:
        if field_name not in existing_field_names:
            raise Exception("Field: {0} not in {1}".format(field_name, table))
        add_mapping(field_name, existing_mapping, new_mapping)

    # add missing fields at end
    if add_missing:
        missing_fields = [f for f in existing_field_names if f not in field_order]
        for field_name in missing_fields:
            add_mapping(field_name, existing_mapping, new_mapping)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(table, out_table, new_mapping)
    return out_table


def load_vul_struct_table(in_table, key_field):
    # Dictionnaire contenant une entree 'Classes' contenant une liste de titre des classes
    # et des entrees pour chaque type de proprietees contenant une liste des seuls de chaque classes

    vul_struct = {'Classes': []}  # Creation du dictionnaire
    for f in arcpy.ListFields(in_table, "Seuil*"):
        vul_struct['Classes'].append(f.name.replace('Seuil_', ''))

    for row in arcpy.SearchCursor(in_table):
        vul_struct[row.getValue(key_field)] = []
        for c in vul_struct['Classes']:
            vul_struct[row.getValue(key_field)].append(float(row.getValue('Seuil_' + c)) / 100)
    vul_struct['Classes'].insert(0, 'Normale')
    return vul_struct


def find_class(value, thres):
    i = bisect.bisect(thres, value)
    return i


def find_classname(value, thres, classname):
    i = bisect.bisect(thres, value)
    return classname[i]


def vulnerabilite_rr(in_rr_layer, in_ras, vul_infra_route, id_vul_infra_route):
    # Selection des segments touches par l'alea
    # inRRLayer = 'inRRLayer'
    # arcpy.MakeFeatureLayer_management(inRR, inRRLayer)
    # arcpy.SelectLayerByLocation_management(inRRLayer,"INTERSECT",maskZIl)

    # Copie des segments selectionnes du rr pour l'analyse de la fonctionnalite
    zi_rr2 = 'zi_rr3a'  # A modifier, Generer un nom automatiquement
    arcpy.CopyFeatures_management(in_rr_layer, zi_rr2)
    arcpy.Densify_edit(zi_rr2, "DISTANCE", "10")

    # Conversion des vertex en points
    arcpy.AddMessage('  Conversion des vertex en points')
    rr_pts = 'RRpts'  # A modifier, Generer un nom automatiquement
    arcpy.FeatureVerticesToPoints_management(zi_rr2, rr_pts, 'ALL')

    # Extraction de la profondeur de submersion aux points
    arcpy.AddMessage('  Extraction de la profondeur de submersion')
    rr_pts_extract = 'RRptsExtract'  # A modifier, Generer un nom automatiquement
    arcpy.sa.ExtractValuesToPoints(rr_pts, in_ras, rr_pts_extract)

    # Changement des valeurs NoData (-9999 ou moins) pour la valeur 0
    rows = arcpy.da.UpdateCursor(rr_pts_extract, ["RASTERVALU"])
    for row in rows:
        if row[0] <= -9999:
            row[0] = 0
        rows.updateRow(row)
    del rows

    arcpy.AddMessage('  Comparaison des profondeur de submersion avec les seuils')
    out_stats_table = 'stats'
    arcpy.Statistics_analysis(rr_pts_extract, out_stats_table, [["RASTERVALU", "MAX"]], [id_vul_infra_route, 'PRECISION'])  # MAX (hauteurs inondation positives) ou MIN (hauteurs negatives) # , 'CRCC_NO_SEQ'

    for f in arcpy.ListFields(out_stats_table):
        if 'max' in f.name.lower():  # min ou max
            maxfield = f.name
            break

    status_rr = {}

    rows = arcpy.da.SearchCursor(out_stats_table, [id_vul_infra_route, maxfield, "PRECISION"])
    for row in rows:
        # statusRR[identifiant_route] = niveau_de_fonctionnalite[hauteur eau, inonde/non-inonde]
        # print row.getValue(IDvulInfraRou)
        status_rr[row[0]] = [row[1], find_class(row[1], vul_infra_route[row[2]])]  # '-' en face du row de "findClass( ICI row.getValue (maxfield)" #[row.CRCC_NO_SEQ]
    del rows

    return status_rr


def eval_vul_intrinseque(in_vul_intrinseque, cur_vul_struct, in_cent_layer, id_field, id_vul_intrinseque, value_vul_intrinseque):
    for k, v in cur_vul_struct.iteritems():
        query = '"' + id_field + '" = ' + str(k)
        rows = arcpy.da.SearchCursor(in_cent_layer, [id_vul_intrinseque], query)
        for row in rows:
            query2 = '"' + id_vul_intrinseque + '" = \'' + row[0] + '\''
            rows2 = arcpy.da.SearchCursor(in_vul_intrinseque, [value_vul_intrinseque], query2)
            for row2 in rows2:
                if row2[0] + 1 > v['vulnerabilite']:
                    v['vulnerabilite'] += 1
                    v['Description'] = v['Description'] + '; Agravations socio-economiques'
            del rows2
        del rows


def write_batiments(in_bat, cur_vul_struct, c_vul_struct, id_field, out_batiment_name):
    in_bat_layer = 'inBatLayer'
    arcpy.MakeFeatureLayer_management(in_bat, in_bat_layer)
    if len(cur_vul_struct.keys()) > 0:
        arcpy.SelectLayerByAttribute_management(in_bat_layer, "CLEAR_SELECTION")
        for k in cur_vul_struct.keys():
            arcpy.SelectLayerByAttribute_management(in_bat_layer, "ADD_TO_SELECTION", id_field + ' = ' + str(k))

        # Copie des batiments touches dans un nouveau fichier
        arcpy.CopyFeatures_management(in_bat_layer, out_batiment_name)
    else:
        arcpy.CreateFeatureclass_management(arcpy.env.workspace, out_batiment_name, "POLYGON", in_bat, "#", "#", in_bat)

    arcpy.AddField_management(os.path.join(arcpy.env.workspace, out_batiment_name), 'STATUS', 'TEXT')
    arcpy.AddField_management(os.path.join(arcpy.env.workspace, out_batiment_name), 'Description', 'TEXT')

    if len(cur_vul_struct.keys()) > 0:
        # Mise a jour du fichier
        rows = arcpy.da.UpdateCursor(os.path.join(arcpy.env.workspace, out_batiment_name), [id_field, "STATUS", "Description"])
        for row in rows:
            # Vulnerabilite structurelle
            if cur_vul_struct[row[0]]['vulnerabilite'] >= len(c_vul_struct) - 1:
                row[1] = c_vul_struct[-1]
            else:
                row[1] = c_vul_struct[cur_vul_struct[row[0]]['vulnerabilite']]
            row[2] = cur_vul_struct[row[0]]['Description'].lstrip('; ')
            rows.updateRow(row)
        del rows


def write_rr(in_rr_iso, status_rr, id_vul_infra_route, c_vul_infra_route, zi_rr):
    rr_iso_layer = 'rr_isolated'
    arcpy.MakeFeatureLayer_management(in_rr_iso, rr_iso_layer, "CRCC_NO_SEQ <> 99")

    arcpy.SelectLayerByAttribute_management(rr_iso_layer, "CLEAR_SELECTION")
    for k, v in status_rr.iteritems():
        arcpy.SelectLayerByAttribute_management(rr_iso_layer, "ADD_TO_SELECTION", id_vul_infra_route + ' = ' + str(k))

    arcpy.CopyFeatures_management(rr_iso_layer, zi_rr)
    arcpy.AddField_management(os.path.join(arcpy.env.workspace, zi_rr), "STATUS", "TEXT")
    arcpy.AddField_management(os.path.join(arcpy.env.workspace, zi_rr), "MAX_PROF", "TEXT")  # MODIF de FLOAT en TEXT

    # Ecriture du status et de la profondeur maximale de submersion
    rows = arcpy.da.UpdateCursor(os.path.join(arcpy.env.workspace, zi_rr), [id_vul_infra_route, "MAX_PROF", "STATUS"])
    for row in rows:
        if status_rr[row[0]][0] == 1000:
            row[1] = '0'  # MODIF de 0 en '0'
            row[2] = 'Isolee'
        else:
            row[1] = status_rr[row[0]][0]  # MODIF
            row[2] = c_vul_infra_route[status_rr[row[0]][1]]
        rows.updateRow(row)
    del rows


def create_submersion_matrix(debit, a, b, dem, mask, in_mask, out_sr):
    hhh = numpy.exp(a) * float(debit) ** b  # hhh = (float(debit)/numpy.exp(b))**(1/a)

    pl = hhh < dem  # plaine inondable binaire

    # Lissage de la plaine inondable binaire
    pl = scipy.ndimage.binary_opening(pl, structure=numpy.ones((3, 3)), iterations=1).astype(numpy.int)
    pl = scipy.ndimage.binary_fill_holes(pl)  # .astype(int)

    # Conversion en polygon pour eliminer les zones ne touchant pas au lit de la riviere
    pl2 = arcpy.NumPyArrayToRaster(numpy.invert(pl).astype(int), out_sr[2], out_sr[1], out_sr[1])
    arcpy.DefineProjection_management(pl2, out_sr[0])
    pl2 = pl2 * in_mask
    polyg = arcpy.CreateScratchName("", "", "FeatureClass")
    polyg = arcpy.CreateUniqueName(polyg)
    arcpy.RasterToPolygon_conversion(pl2, polyg, "NO_SIMPLIFY")
    arcpy.MakeFeatureLayer_management(polyg, 'polyg_layer', 'GRIDCODE = 1')  # Pour les shapefile, le champ est GRIDCODE, sinon grid_code
    arcpy.SelectLayerByLocation_management('polyg_layer', "INTERSECT", mask, '', "NEW_SELECTION")
    new_mask = arcpy.CreateScratchName("", "", "RasterDataset")
    new_mask = arcpy.CreateUniqueName(new_mask)
    arcpy.PolygonToRaster_conversion('polyg_layer', 'GRIDCODE', new_mask, "CELL_CENTER", "NONE", out_sr[1])  # inDEM)

    # Calcul de la profondeur de submersion
    pl = numpy.invert(pl).astype(int) * (dem - hhh)

    # Nettoyage des valeurs indesirables
    pl[pl < -100] = 0
    pl[pl > 0] = -0.001  # les pixels dont la valeur est > 0 sont ceux issus du lissage de la plaine inondable binaire

    # Conversion en raster et definition de la projection
    rhhh = arcpy.NumPyArrayToRaster(pl, out_sr[2], out_sr[1], out_sr[1]) * new_mask
    arcpy.DefineProjection_management(rhhh, out_sr[0])

    return rhhh


def validate_fieldname_gn(gn):
    for f in arcpy.ListFields(gn):
        if f.name.lower() == 'enabled':
            break
    else:
        arcpy.AddError('Le champ Enabled est absent de la table du reseau routier')


def verif_vul_table(in_vul_bd, vul_table):
    arcpy.env.workspace = in_vul_bd
    lts = arcpy.ListTables('*')
    for t in lts:
        if t in vul_table:
            vul_table.pop(vul_table.index(t))
    if len(vul_table) > 0:
        # error
        for i in vul_table:
            arcpy.AddError('La table ' + i + ' est absente.')


def evaluate_vul_batiments(in_cent_layer, in_ras, id_field, vul_struct, id_vul_struct, vul_infra_essentiel, id_vul_infra):
    # Extraction des profondeurs de submersion
    arcpy.AddMessage('  Extraction des profondeurs de submersion')
    out_extract_pts = 'extract_pts'
    arcpy.sa.ExtractValuesToPoints(in_cent_layer, in_ras, out_extract_pts)

    # Comparaison des profondeur de submersion avec les seuils
    arcpy.AddMessage('  Comparaison des profondeur de submersion avec les seuils')
    cur_vul_struct = {}
    cur_vul_infra_essentiel = {}

    rows = arcpy.da.SearchCursor(out_extract_pts, [id_field, id_vul_struct, id_vul_infra, "RASTERVALU"])
    for row in rows:
        if row[1] != 0:  # Colonne ajoutee a la table des centroides indiquant le type de residence, pourrait etre fait OTF
            # Presence d'une residence
            # Vulnerabilite structurelle
            if row[0] not in cur_vul_struct.keys():
                cur_vul_struct[row[0]] = {}
                cur_vul_struct[row[0]]['vulnerabilite'] = 0
                cur_vul_struct[row[0]]['Description'] = ''
            cur_vul_struct[row[0]]['vulnerabilite'] = find_class(-row[3], vul_struct[row[1]])
            cur_vul_struct[row[0]]['Description'] = 'Vulnerabilite structurelle'

        elif row[2] in vul_infra_essentiel.keys():
            # Presence d'une infrastructure jugee essentielle
            # Vulnerabilite fonctionnelle
            if row[0] not in cur_vul_struct.keys():
                cur_vul_infra_essentiel[row[0]] = {}
                cur_vul_infra_essentiel[row[0]]['vulnerabilite'] = 0
                cur_vul_infra_essentiel[row[0]]['Description'] = ''
            cur_vul_infra_essentiel[row[0]]['vulnerabilite'] = find_class(-row[3], vul_infra_essentiel[row[2]])
            cur_vul_infra_essentiel[row[0]]['Description'] = 'Vulnerabilite fonctionnelle'
    del rows

    return cur_vul_struct, cur_vul_infra_essentiel


def check_vulnerabilite_part1(in_ras, in_cent, in_bat, in_rr, in_vul_intrinseque, in_vul_bd, out_var_file):
    results = []
    arcpy.env.overwriteOutput = True

    # Validation de la presence d'un champ Enabled dans la table du reseau routier
    validate_fieldname_gn(in_rr)

    # Pourraient etre specifie dans un fichier texte ou en parametre
    id_field, id_vul_intrinseque = 'ID_bat', 'ADIDU'
    id_vul_struct, id_vul_infra, id_typevul_infra_rou = 'Type', 'CUBF_PRINC', 'Numero_classification_routiere_CC'
    id_vul_infra_route = 'NO_SEQ'
    value_vul_intrinseque = 'Tot_vul'
    vul_table = ['Vul_Infra_Essentielles', 'Vul_Infra_Routiere', 'Vul_structurelle']

    # Verification de la presence de toutes les tables necessaires a l'evaluation
    # de la vulnerabilite
    verif_vul_table(in_vul_bd, vul_table)

    # Chargement des tables dans des dictionnaires
    arcpy.AddMessage('Chargement des tables de vulnerabilite')
    vul_struct = load_vul_struct_table(os.path.join(in_vul_bd, 'vul_structurelle'), id_vul_struct)
    c_vul_struct = vul_struct['Classes']
    # cVulStruct.insert(0,'Normal')
    vul_infra_ess = load_vul_struct_table(os.path.join(in_vul_bd, 'Vul_Infra_Essentielles'), id_vul_infra)
    c_vul_infra_essentiel = vul_infra_ess['Classes']
    # cVulInfraEss.insert(0,'Normal')
    vul_infra_route = load_vul_struct_table(os.path.join(in_vul_bd, 'Vul_Infra_Routiere'), id_typevul_infra_rou)
    c_vul_infra_route = vul_infra_route['Classes']
    # cVulInfraRoute.insert(0,'Normal')

    arcpy.env.workspace = get_scratch_dir()

    # Creation d'un masque a partir du raster de prodondeur de submersion
    arcpy.AddMessage('Creation du polygone de la zone inondee')
    arcpy.CheckOutExtension('Spatial')
    if isinstance(in_ras, basestring):
        in_ras = arcpy.Raster(in_ras)
    mask_zi_r = in_ras > -10000
    mask_zi_s = 'Zone_inondee'  # la conversion en feature layer ne fonctionne pas avec juste la geometrie
    arcpy.RasterToPolygon_conversion(mask_zi_r, mask_zi_s)
    results.append(mask_zi_s)

    # Traitement des batiments ###################################
    arcpy.AddMessage('Traitement des batiments')
    # Creation de feature layer pour le masque, les centroides et les batiments
    mask_zi_l = 'maskZIl'
    arcpy.MakeFeatureLayer_management(os.path.join(arcpy.env.workspace, mask_zi_s), mask_zi_l)
    in_cent_layer = 'inCentLayer'
    arcpy.MakeFeatureLayer_management(in_cent, in_cent_layer)
    arcpy.SelectLayerByLocation_management(in_cent_layer, "INTERSECT", mask_zi_l)
    in_bat_layer = 'inBatLayer'
    arcpy.MakeFeatureLayer_management(in_bat, in_bat_layer)

    if arcpy.Describe(in_cent_layer).FIDset != '':
        cur_vul_struct, cur_vul_infra_essentiel = evaluate_vul_batiments(in_cent_layer, in_ras, id_field, vul_struct, id_vul_struct, vul_infra_ess, id_vul_infra)
    else:
        cur_vul_struct, cur_vul_infra_essentiel = {}, {}
    #################################################################

    # Traitement du reseau routier #################################
    arcpy.AddMessage('Traitement du reseau routier')

    # Selection des segments touches par l'alea
    in_rr_layer = 'inRRLayer'
    arcpy.MakeFeatureLayer_management(in_rr, in_rr_layer)
    arcpy.SelectLayerByLocation_management(in_rr_layer, "INTERSECT", mask_zi_l)

    # Verification de la vulnerabilite fonctionnelle du reseau routier
    if arcpy.Describe(in_rr_layer).FIDset != '':
        status_rr = vulnerabilite_rr(in_rr, in_ras, vul_infra_route, id_vul_infra_route)
    else:
        status_rr = {}
    ##################################################################

    # Mise a jour de la vulnerabilite structurelle en fct de la vulnerabilite de la route
    arcpy.AddMessage('  Mise a jour de la vulnerabilite structurelle en fct de la vulnerabilite de la route')
    # Selection des batiments dont l'adresse donne sur une rue non fonctionnelle
    arcpy.SelectLayerByAttribute_management(in_cent_layer, "CLEAR_SELECTION")
    need_part2 = False

    rows = arcpy.da.SearchCursor(in_rr_layer, [id_vul_infra_route, "GENERIQUE", "LIAISON", "SPECIFIQUE", "NO_CIV_DROITE_DE",
                                               "NO_CIV_DROITE_A", "NO_CIV_GAUCHE_DE", "NO_CIV_GAUCHE_A"])
    for row in rows:
        if status_rr[row[0]][1] == 2:  # 'non_fonctionnelle':
            sql_fct_p1 = ''
            sql_fct = '"TYPE_RUE" = \'' + row[1]
            if row[2]:
                sql_fct = sql_fct + " " + row[2].replace("'", "''") + "'"
            else:
                sql_fct = sql_fct + "\'"
            sql_fct = sql_fct + '  AND "NOM_RUE" = \'' + row[3].replace("'", "''") + '\''

            if row[4] or row[5]:
                sql_fct_p1 = ' AND ("CIVIQ_A2" >= ' + str(row[4]) + ' AND "CIVIQ_A2" <= ' + str(row[5]) + ')'

            if row[6] or row[7]:
                if sql_fct_p1 != '':
                    sql_fct_p1 = sql_fct_p1.replace("(", "((")
                    sql_fct_p1 = sql_fct_p1.replace(')', ') OR ("CIVIQ_A2" >= ' + str(row[6]) + ' AND "CIVIQ_A2" <= ' + str(row[7]) + '))')
                else:
                    sql_fct_p1 = ' AND "CIVIQ_A2" >= ' + str(row[6]) + ' AND "CIVIQ_A2" <= ' + str(row[7])

            if sql_fct_p1 != '':
                arcpy.SelectLayerByAttribute_management(in_cent_layer, "ADD_TO_SELECTION", sql_fct + sql_fct_p1)

            need_part2 = True

    # Mise a jour du status des batiments residentiels
    if arcpy.Describe(in_cent_layer).FIDset != '':
        rows = arcpy.da.SearchCursor(in_cent_layer, [id_field, id_vul_struct])
        for row in rows:
            if row[1] != 0:  # Colonne ajoutee a la table des centroides indiquant le type de residence, pourrait etre fait OTF
                # Presence d'une residence
                # Vulnerabilite structurelle
                if row[0] not in cur_vul_struct.keys():
                    cur_vul_struct[row[0]] = {}
                    cur_vul_struct[row[0]]['vulnerabilite'] = 0
                    cur_vul_struct[row[0]]['Description'] = ''
                cur_vul_struct[row[0]]['vulnerabilite'] = cur_vul_struct[row[0]]['vulnerabilite'] + 1
                cur_vul_struct[row[0]]['Description'] = cur_vul_struct[row[0]]['Description'] + '; Route fermee'
        del rows

    ####################################################################

    if need_part2:  # des routes non-fonctionnelles sont presentes

        # Preparation des fichiers pour l'analyse de vulnerabilite indirecte
        arcpy.AddMessage('Preparation des fichiers pour l\'analyse de vulnerabilite indirecte')

        # Mise a jour de l'etat du reseau routier pour l'analyse reseau
        rows = arcpy.da.UpdateCursor(in_rr, [id_vul_infra_route])  # os.path.join(arcpy.env.workspace,rr_ar))
        for row in rows:
            row.Enabled = 1
            if row[0] in status_rr:
                if status_rr[row[0]][1] == 2:
                    row.Enabled = 0
            rows.updateRow(row)
        del rows

        # Sauvegarde des variables
        arcpy.AddMessage('Sauvegarde des variables')
        # del row
        lst = ['IDField', 'inRR', 'inVulIntrin', 'IDvulIntrinseque', 'vulStruct',
               'inCent', 'curVulInfraEss', 'IDTypevulInfraRou', 'inVulBD', 'inBat',
               'inBatLayer', 'valueVulIntr', 'IDvulInfraRou', 'vulTable', 'IDvulInfra',
               'cVulStruct', 'inRRLayer', 'IDvulStruct', 'statusRR', 'cVulInfraEss',
               'vulInfraRoute', 'vulInfraEss', 'maskZIl', 'curVulStruct', 'inCentLayer',
               'maskZIs', 'cVulInfraRoute']
        my_shelf = shelve.open(out_var_file, 'n')
        for l in lst:
            my_shelf[l] = locals()[l]
        my_shelf.close()

        # arcpy.SetParameterAsText(8,inRR)#rr_ar)
        results.append(in_rr)
        arcpy.AddMessage('*** Passez a la partie manuelle ***')

    else:  # On finit l'analyse ici
        arcpy.AddMessage('*** Partie manuelle inutile ***')

        # Mise a jour de la vulnerabilite structurelle en fct de la vulnerabilite intrinseque
        arcpy.AddMessage('Mise a jour de la vulnerabilite structurelle en fonction de la vulnerabilite intrinseque')

        eval_vul_intrinseque(in_vul_intrinseque, cur_vul_struct, in_cent_layer, id_field, id_vul_intrinseque, value_vul_intrinseque)

        ####################################################################

        # Ecriture des fichiers de sortie #################################
        arcpy.AddMessage('Ecriture des fichiers de sortie')
        # Ecriture du status pour les batiments (residences et infrastructures essentielles)

        # Selection des batiments residentiels touches
        arcpy.AddMessage('  Batiments residentiels')
        out_bat_res = 'Etat_batiments_residentiels'
        write_batiments(in_bat, cur_vul_struct, c_vul_struct, id_field, out_bat_res)

        # Selection des infrastructures essentielles touchees
        arcpy.AddMessage('  Infrastructures essentielles')
        out_bat_ess = 'Etat_infrastructures_essentielles'
        write_batiments(in_bat, cur_vul_infra_essentiel, c_vul_infra_essentiel, id_field, out_bat_ess)

        # Reseau routier
        # Copie des segments selectionnes du rr pour le fichier de sortie
        arcpy.AddMessage('  Reseau routier')
        zi_rr = 'Etat_du_reseau_routier'
        write_rr(in_rr_layer, status_rr, id_vul_infra_route, c_vul_infra_route, zi_rr)

        # arcpy.SetParameterAsText(8,zi_rr)
        # arcpy.SetParameterAsText(9,outBatEss)
        # arcpy.SetParameterAsText(10,outBatRes)
        results.append(zi_rr)
        results.append(out_bat_res)
        results.append(out_bat_ess)
        arcpy.AddMessage('**Fin des traitements**')

        #######################################################################

    return need_part2, results


def DommagesVersExcel(in_debits, in_shapefile_dommages_batiments, out_filename):

    arcpy.env.workspace = get_scratch_dir()
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = "Default"

    matricules = []
    dommages = []

    with arcpy.da.SearchCursor(in_shapefile_dommages_batiments,['Matricule','Dmg_pc','Dmg_dollar']) as batimentsCursor:

        for batiment in batimentsCursor:

            matricules.append(batiment[0])
            dommages.append((batiment[1], batiment[2]))

    df1 = pandas.DataFrame(columns=matricules, index=in_debits)
    df2 = pandas.DataFrame(columns=matricules, index=in_debits)

    for index in in_debits:

        for matricule, dommage in zip(matricules, dommages):

            df1[matricule][index] = dommage[0]
            df2[matricule][index] = dommage[1]

    if os.path.exists(out_filename):

        book = load_workbook(out_filename)
        writer = pandas.ExcelWriter(out_filename, engine='openpyxl')
        writer.book = book

        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        df1.to_excel(excel_writer=writer,
                     sheet_name='Pourcentages')
        df2.to_excel(excel_writer=writer,
                     sheet_name='Montants')

        writer.save()

    else:


        writer = pandas.ExcelWriter(out_filename, engine='openpyxl')

        df1.to_excel(excel_writer=writer,
                     sheet_name='Pourcentages')
        df2.to_excel(excel_writer=writer,
                     sheet_name='Montants')

        writer.save()
