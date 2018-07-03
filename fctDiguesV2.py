# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        fctDiguesV2.py
# Purpose:     Calculer la quantité de sable et le nombre de sac requis pour construire
#              les digues autour des bâtiments à risque d'inondation
#
# Author:      poulinji et Charles Tousignant
#
# Created:     26-03-2018
# Copyright:   (c) poulinji 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import arcpy
import math
from Utils_MP import elapsed_time
import Building_locator


def volumeTrapeze(h, sommet, base, profondeur):
    return (sommet + base) / 2 * h * profondeur


def baseTrapeze(h, angle, sommet):
    return math.tan(math.radians(angle)) * h * 2 + sommet


def digue(in_lines, in_raster):
    """
    Calculate quantities of sand and bags required for dike construction
    :param in_lines: (string) path of lines shapefile
    :param in_raster: (string) path of water height raster
    """
    # Parametre de configuration de la digue
    sommet = 0.61  # Largeur du sommet (must be at least 2' wide across the top of the dike)
    angle = 45  # angle des cotes
    freeboard = 0.61  # area of the dike between the highest floodwater level and the top of the dike (2')
    compaction = 1.05  # 5% of the required height of the dike to account for compaction due to wetting
    volumeSac = 0.02  # 32kg de sable  (20 litres)
    arcpy.env.workspace = arcpy.Describe(in_lines).path
    arcpy.env.overwriteOutput = True

    # Conversion du raster en polygone
    arcpy.CheckOutExtension('Spatial')
    rasBool = arcpy.sa.Int(arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, 1))
    filteredRaster = arcpy.sa.SetNull(rasBool, rasBool, "VALUE = 0")
    outPolygon = "zi_polygon.shp"
    arcpy.RasterToPolygon_conversion(filteredRaster, outPolygon, 'NO_SIMPLIFY')

    # Clip des lignes par le polygone
    outClip = "clip_lines.shp"
    arcpy.Clip_analysis(in_lines, outPolygon, outClip)

    # Multipart to single part + densify
    outMulti = "multi_lines.shp"
    arcpy.MultipartToSinglepart_management(outClip, outMulti)
    arcpy.Densify_edit(outMulti, 'DISTANCE', 0.2)
    allPts = "allPts.shp"
    arcpy.FeatureVerticesToPoints_management(outMulti, allPts, 'All')

    # Extractition des valeurs sur le raster pour chaque point
    allPtsZ = "allPtsZ.shp"
    arcpy.sa.ExtractValuesToPoints(allPts, in_raster, allPtsZ, 'INTERPOLATE')

    arcpy.AddField_management(outMulti, 'Volume', 'FLOAT')
    arcpy.AddField_management(outMulti, 'Nb_Sacs', 'INTEGER')
    arcpy.AddField_management(outMulti, 'Comments', 'TEXT')

    with arcpy.da.UpdateCursor(outMulti, ['SHAPE@', 'RIGHT_FID', 'Volume', 'Nb_Sacs', 'Comments']) as ucursor:
        for urow in ucursor:
            volumeTotal = 0
            with arcpy.da.SearchCursor(allPtsZ, ['RASTERVALU'], """"RIGHT_FID" = {0}""".format(urow[1])) as scursor:
                allDepth = []
                for srow in scursor:
                    allDepth.append(srow[0])
                for d in allDepth:
                    if d == -9999:
                        base = baseTrapeze(freeboard, angle, sommet)
                        volumeTotal += volumeTrapeze(freeboard*compaction, sommet, base, 0.2)
                    else:
                        base = baseTrapeze(d + freeboard, angle, sommet)
                        volumeTotal += volumeTrapeze((d+freeboard)*compaction, sommet, base, 0.2)

                urow[2] = volumeTotal
                urow[3] = volumeTotal / volumeSac
            ucursor.updateRow(urow)

    outDigues = "out_digues.shp"
    arcpy.Dissolve_management(outMulti, outDigues, ['RIGHT_FID', 'Volume', 'Nb_Sacs'])

    arcpy.Delete_management(outPolygon)
    arcpy.Delete_management(outClip)
    arcpy.Delete_management(outMulti)
    arcpy.Delete_management(allPts)
    arcpy.Delete_management(allPtsZ)
    arcpy.Delete_management("lines.shp")


def create_convex_hull(in_fc, grouping_field=None):
    """
    Generate convex hull features optionally grouping input features;
    if no grouping_field specified, a single Convex Hull will be generated
    for all input features. Used for grouped buildings.
    :param in_fc: (string) path of building shapefile
    :param grouping_field: (string) name of the grouping field if needed
    """

    tmp_dis = arcpy.Dissolve_management(in_features=in_fc,
                                        out_feature_class=r"in_memory\tempOutput",
                                        dissolve_field=grouping_field,
                                        multi_part=True)

    feats = [f[0].convexHull() for f in arcpy.da.SearchCursor(tmp_dis, "SHAPE@")]

    arcpy.env.workspace = arcpy.Describe(in_fc).path
    fc_type = arcpy.Describe(in_fc).baseName
    out_fc_name = "ConvexHull{0}".format(fc_type)
    if arcpy.Exists(out_fc_name):
        arcpy.Delete_management(out_fc_name)
    arcpy.CopyFeatures_management(feats, out_fc_name)


def line_creator(in_bat):
    """
    Create lines around selected buildings
    :param in_bat: (string) path of buildings shapefile
    """
    print("Creating lines...")
    arcpy.env.workspace = arcpy.Describe(in_bat).path
    arcpy.env.overwriteOutput = True
    dissolve_buf = "dissolve_buf.shp"
    CHdissolve_buf = "ConvexHulldissolve_buf.shp"

    tmp_buf = arcpy.Buffer_analysis(in_features=in_bat,
                                    out_feature_class=r"in_memory\tempOutput",
                                    buffer_distance_or_field="8 FEET",
                                    line_side="OUTSIDE_ONLY",
                                    line_end_type="ROUND",
                                    dissolve_option="NONE")

    tmp_dis = arcpy.Dissolve_management(in_features=tmp_buf,
                                        out_feature_class=r"in_memory\tempOutput1",
                                        multi_part=True)

    tmp_single = arcpy.MultipartToSinglepart_management(in_features=tmp_dis,
                                                        out_feature_class=dissolve_buf)

    tmp_field = arcpy.AddField_management(in_table=tmp_single,
                                          field_name="group",
                                          field_type="SHORT")

    with arcpy.da.UpdateCursor(tmp_field, "group") as cursor:
        i = 0
        for row in cursor:
            row[0] = i
            cursor.updateRow(row)
            i += 1

    create_convex_hull(tmp_field, grouping_field="group")
    arcpy.PolygonToLine_management(in_features=CHdissolve_buf,
                                   out_feature_class="lines")

    arcpy.Delete_management(dissolve_buf)
    arcpy.Delete_management(CHdissolve_buf)


def line_creator2(in_adr):
    """
    Create lines around selected buildings
    :param in_adr: (string) addresses separated by semicolon (;)
    """
    print("Extracting buildings and creating lines...")
    arcpy.env.workspace = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Digues"
    arcpy.env.overwriteOutput = True
    dissolve_buf = "dissolve_buf.shp"
    CHdissolve_buf = "ConvexHulldissolve_buf.shp"
    localized_building_proj = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building.shp"
    localized_building_proj2 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building2.shp"
    localized_buildings_final = "out_digue_bat.shp"

    # create shapefiles
    for i in range(len(in_adr)):
        localized_building_proj3 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building_{}.shp".format(i)
        if arcpy.Exists(localized_building_proj):
            arcpy.CopyFeatures_management(localized_building_proj, localized_building_proj2)
            arcpy.Delete_management(localized_building_proj)
            Building_locator.main(in_adr[i])
            arcpy.Merge_management([localized_building_proj, localized_building_proj2], localized_building_proj3)
            arcpy.Delete_management(localized_building_proj2)
        else:
            Building_locator.main(in_adr[i])

    # merge
    building_list = []
    for j in range(len(in_adr)-1):
        shape_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building_{}.shp".format(j+1)
        building_list.append(shape_path)
    arcpy.Merge_management(building_list, localized_buildings_final)

    # clean
    arcpy.Delete_management(localized_building_proj)
    for k in range(len(in_adr)-1):
        arcpy.Delete_management("E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building_{}.shp".format(k+1))

    tmp_buf = arcpy.Buffer_analysis(in_features=localized_buildings_final,
                                    out_feature_class=r"in_memory\tempOutput",
                                    buffer_distance_or_field="8 FEET",
                                    line_side="OUTSIDE_ONLY",
                                    line_end_type="ROUND",
                                    dissolve_option="NONE")

    tmp_dis = arcpy.Dissolve_management(in_features=tmp_buf,
                                        out_feature_class=r"in_memory\tempOutput1",
                                        multi_part=True)

    tmp_single = arcpy.MultipartToSinglepart_management(in_features=tmp_dis,
                                                        out_feature_class=dissolve_buf)

    tmp_field = arcpy.AddField_management(in_table=tmp_single,
                                          field_name="group",
                                          field_type="SHORT")

    with arcpy.da.UpdateCursor(tmp_field, "group") as cursor:
        i = 0
        for row in cursor:
            row[0] = i
            cursor.updateRow(row)
            i += 1

    create_convex_hull(tmp_field, grouping_field="group")
    arcpy.PolygonToLine_management(in_features=CHdissolve_buf,
                                   out_feature_class="lines")

    arcpy.Delete_management(dissolve_buf)
    arcpy.Delete_management(CHdissolve_buf)


def main():
    """
    Main function. Ask for a list of addresses or type 'ALL' to calculate for all buildings in the shapefile.
    Change the path of inBat and inRas for the desired building shapefile and water height raster.
    """
    inBat = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_batiments.shp"
    # inRas = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_hauteur_eau_debit_1369.tif"
    # inBat = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Zones_extraction\BV_Richelieu_geocode.shp"
    inRas = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_hauteur_eau_debit_1369_full.tif"
    inLines = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\lines.shp"

    r_input = raw_input("Entrez une liste d'adresses séparée par des points-virgules (;) ou 'ALL' pour toutes les adresses affectées")
    if r_input == 'ALL':
        line_creator(inBat)
        digue(inLines, inRas)
    else:
        # inAdr = ["239 rue Beaubien, St-Jean", "38 rue Verdi, St-Jean", "17 rue Verdi, St-Jean"]
        # inAdr = 239 rue Beaubien, St-Jean ; 38 rue Verdi, St-Jean ; 17 rue Verdi, St-Jean ; 77 rue Roman, St-Jean
        # inAdr = 55 rue de l'Oasis, St-Jean ; 37 Baraby, St Jean ; 41 rue Barby, Saint-Jean; 354 rue Charles Preston, St-Jean;1414 rue de Foucault, St-Jean
        line_creator2(r_input.split(";"))
        digue(inLines, inRas)
    arcpy.Delete_management(inLines)


if __name__ == '__main__':
    main()
    print("##############################")
    print("Dike calculation complete!")
    print(elapsed_time())
    print("##############################")
