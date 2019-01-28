# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ajout_info_bat.py
# Created on: 2019-01-10
# Author : Charles Tousignant
# Project : GARI
# Description : Ajouter de l'information à la couche de bâtiments (Matricule,
# Valeur_bat, Nb_etages, Pres_ss1, Zrc)
# ---------------------------------------------------------------------------

from utils import *
import pandas as pd



def add_matricule(inBat, inMatrice):

    copie_batiments = create_ScratchGDB_name("copie_batiments")
    arcpy.CopyFeatures_management(inBat, copie_batiments)
    out_shp = create_ScratchGDB_name("out_shp")

    # arcpy.AddField_management(copie_batiments, "Matricule", "LONG")
    # arcpy.AddField_management(copie_batiments, "Valeur_bat", "LONG")
    # arcpy.AddField_management(copie_batiments, "Nb_etages", "SHORT")
    # arcpy.AddField_management(copie_batiments, "Pres_ss1", "SHORT")
    # arcpy.AddField_management(copie_batiments, "Zrc", "FLOAT")

    # Create FieldMappings object
    fm_id = arcpy.FieldMap()
    fms = arcpy.FieldMappings()
    fm_adresse = arcpy.FieldMap()
    fm_numciv = arcpy.FieldMap()
    fm_rue = arcpy.FieldMap()
    fm_ville = arcpy.FieldMap()
    fm_province = arcpy.FieldMap()
    fm_CP = arcpy.FieldMap()
    fm_pays = arcpy.FieldMap()
    fm_matricule = arcpy.FieldMap()
    fm_lot = arcpy.FieldMap()

    fm_id.addInputField(copie_batiments, "ID_bat")
    fm_adresse.addInputField(copie_batiments, "Adresse_im")
    fm_numciv.addInputField(copie_batiments, "Num_Civ")
    fm_rue.addInputField(copie_batiments, "Rue")
    fm_ville.addInputField(copie_batiments, "Ville")
    fm_province.addInputField(copie_batiments, "Province")
    fm_CP.addInputField(copie_batiments, "CP")
    fm_pays.addInputField(copie_batiments, "Pays")
    fm_matricule.addInputField(inMatrice, "SI0317C")
    fm_lot.addInputField(inMatrice, "SI0424J")

    matricule_name = fm_matricule.outputField
    matricule_name.name = 'Matricule'
    fm_matricule.outputField = matricule_name
    lot_name = fm_lot.outputField
    lot_name.name = 'Lot'
    fm_lot.outputField = lot_name

    fms.addFieldMap(fm_id)
    fms.addFieldMap(fm_adresse)
    fms.addFieldMap(fm_numciv)
    fms.addFieldMap(fm_rue)
    fms.addFieldMap(fm_ville)
    fms.addFieldMap(fm_province)
    fms.addFieldMap(fm_CP)
    fms.addFieldMap(fm_pays)
    fms.addFieldMap(fm_matricule)
    fms.addFieldMap(fm_lot)

    # Spatial join for Matricule field
    arcpy.SpatialJoin_analysis(target_features=copie_batiments,
                               join_features=inMatrice,
                               out_feature_class=out_shp,
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping=fms,
                               match_option="HAVE_THEIR_CENTER_IN",
                               search_radius=0)
    return out_shp


def add_data(inMNT):
    import ogr
    from rasterstats import zonal_stats
    cwd = os.getcwd()
    bat_shp = cwd + r"\output\Batiments.shp"

    shapeData = ogr.Open(bat_shp, 1)
    layer = shapeData.GetLayer()  # get possible layers.
    layer_defn = layer.GetLayerDefn()  # get definitions of the layer

    # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in
    #                range(layer_defn.GetFieldCount())]  # store the field names as a list of strings
    # print len(field_names)  # so there should be just one at the moment called "FID"
    # print field_names  # will show you the current field names

    new_field = ogr.FieldDefn('Nb_etages', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Pres_ss1', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Valeur_bat', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Zrc', ogr.OFTReal)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Type_util', ogr.OFTString)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('ADIDU', ogr.OFTString)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Tot_vul', ogr.OFTReal)
    layer.CreateField(new_field)

    info = pd.read_excel('H:/shapefile/MATRICULES/56083-GARI.xls')

    serie_mat = info['Matricule']
    serie_aire_ss = info['Aire totale ss']
    serie_etage = info['Nb etages']
    serie_util = info['Type util']

    zs = zonal_stats(bat_shp, inMNT)

    for i in range(len(layer)):
        feature = layer.GetFeature(i)
        matricule = feature['Matricule']
        print "Les informations du bâtiment ayant le matricule {} ont été ajoutés".format(matricule)
        if matricule is None:
            j = feature.GetFieldIndex("Nb_etages")
            feature.SetField(j, 9999)
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Pres_ss1")
            feature.SetField(j, 9999)
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Matricule")
            feature.SetField(j, "no_data")
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Lot")
            feature.SetField(j, "no_data")
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Type_util")
            feature.SetField(j, "no_data")
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("ADIDU")
            feature.SetField(j, "no_data")
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Tot_vul")
            feature.SetField(j, 0)
            layer.SetFeature(feature)
        else:
            matricule_format = matricule[0:4] + "-" + matricule[4:6] + "-" + matricule[6:10]
            nb_etage, pres_ss, util = search_xls(matricule_format, serie_mat, serie_aire_ss, serie_etage, serie_util)
            j = feature.GetFieldIndex("Nb_etages")
            feature.SetField(j, nb_etage)
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Pres_ss1")
            feature.SetField(j, pres_ss)
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Valeur_bat")
            feature.SetField(j, 123456)  # Ajouter les vraies valeurs
            layer.SetFeature(feature)

            if pres_ss == 1:
                j = feature.GetFieldIndex("Zrc")
                feature.SetField(j, zs[i]['max'] + 0.64)  # Méthode selon le MNT développé dans le quartier de test
                layer.SetFeature(feature)
            else:
                j = feature.GetFieldIndex("Zrc")
                feature.SetField(j, zs[i]['max'] + 0.27)
                layer.SetFeature(feature)

            j = feature.GetFieldIndex("Type_util")
            feature.SetField(j, util)
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("ADIDU")
            feature.SetField(j, "24560338")  # Ajouter les vraies valeurs
            layer.SetFeature(feature)
            j = feature.GetFieldIndex("Tot_vul")
            feature.SetField(j, 0.5)  # Ajouter les vraies valeurs
            layer.SetFeature(feature)
    shapeData = None


def search_xls(mat, matricule, aire_ss, nb_etage, type_util):

    if mat in list(matricule):
        a = list(matricule).index(mat)
        etage = nb_etage[a]
        if aire_ss[a] > 0:
            pres_ss = 1
        else:
            pres_ss = 0
        util = str(type_util[a])
    else:
        etage = 9999
        pres_ss = 9999
        util = "9999"
    return etage, pres_ss, util


def main():
    clean_scratch_dir()
    cwd = os.getcwd()
    inBat = cwd + r"\output\building_footprint_geocode.shp"
    inMatrice = "H:\shapefile\MATRICULES\MATRICE\SICADA_LLOT_S.shp"
    inMNT = "H:\shapefile\inputs\Modele Numerique de Terrain\mnt_grand.tif"
    outBat = cwd + "\output\Batiments.shp"
    outCen = cwd + "\output\Centroides.shp"

    # inBat = r"H:\shapefile\SJSR_complet\Batiments\SJSR_bat_zone_risk_verif.shp"
    # inMNT = "H:\shapefile\SJSR_complet\MNT\mnt_sjsr.tif"

    bat_mat = add_matricule(inBat, inMatrice)
    arcpy.FeatureClassToFeatureClass_conversion(bat_mat, cwd + "\output", "Batiments")
    add_data(inMNT)
    arcpy.FeatureToPoint_management(outBat, outCen, point_location="INSIDE")
    print("##############################")
    print("L'ajout est complété!")
    print(elapsed_time())
    print("##############################")


if __name__ == "__main__":
    arcpy.env.overwriteOutput = True
    main()


    # import ogr
    # from rasterstats import zonal_stats
    # cwd = os.getcwd()
    # bat_shp = cwd + r"\output\building_footprint_geocode.shp"
    # MNT = "H:\shapefile\inputs\Modele Numerique de Terrain\mnt_grand.tif"
    #
    # shapeData = ogr.Open(bat_shp, 1)
    # layer = shapeData.GetLayer()  # get possible layers.
    #
    #
    # zs = zonal_stats(bat_shp, MNT)
    # print zs[0]
    #
    # for i, feature in enumerate(layer):
    #     geom = feature.GetGeometryRef()
    #     print zs[i]['max']


    # for batiment in fiona.open(bat_train):
    #     if pt.within(shape(batiment['geometry'])):
    #         point_list_train.append(pt)
    #
    #         toit_std = np.std(xyz[:, 2])
    #         toit_mean = np.mean(xyz[:, 2])
    #         toit_min = np.min(xyz[:, 2])
    #         toit_max = np.max(xyz[:, 2])
    #         toit_std_list_train.append(toit_std)
    #         toit_mean_list_train.append(toit_mean)
    #         toit_min_list_train.append(toit_min)
    #         toit_max_list_train.append(toit_max)
    #
    #         poly = shape(batiment['geometry'])
    #         zs = zonal_stats(poly, MNT)
    #         zs_mean = zs[0]['mean']
    #         zs_min = zs[0]['min']
    #         zs_max = zs[0]['max']
    #



    # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in
    #                range(layer_defn.GetFieldCount())]  # store the field names as a list of strings
    # print len(field_names)  # so there should be just one at the moment called "FID"
    # print field_names  # will show you the current field names

    # new_field = ogr.FieldDefn('Nb_etages', ogr.OFTInteger)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('Pres_ss1', ogr.OFTInteger)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('Valeur_bat', ogr.OFTInteger)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('Zrc', ogr.OFTReal)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('Type_util', ogr.OFTString)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('ADIDU', ogr.OFTString)
    # layer.CreateField(new_field)
    #
    # new_field = ogr.FieldDefn('Tot_vul', ogr.OFTReal)
    # layer.CreateField(new_field)
    #
    # info = pd.read_excel('H:/shapefile/MATRICULES/56083-GARI.xls')
    #
    # serie_mat = info['Matricule']
    # serie_aire_ss = info['Aire totale ss']
    # serie_etage = info['Nb etages']
    #
    # for i in range(len(layer)):
    #     feature = layer.GetFeature(i)
    #     matricule = feature['Matricule']
    #     print matricule
    #     if matricule is None:
    #         j = feature.GetFieldIndex("Nb_etages")
    #         feature.SetField(j, 9999)
    #         layer.SetFeature(feature)
    #         j = feature.GetFieldIndex("Pre