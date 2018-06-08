# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      poulinji
#
# Created:     26-03-2018
# Copyright:   (c) poulinji 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import arcpy
import os
import fctUtilitaires
import math
import datetime
from Utils_MP import elapsed_time


def volumeTrapeze(h, sommet, base, profondeur):
    return (sommet + base) / 2 * h * profondeur


def baseTrapeze(h, angle, sommet):
    return math.tan(math.radians(angle)) * h * 2 + sommet


def digue(in_lines, in_raster):
    # Parametre de configuration de la digue
    sommet = 0.3  # Largeur du sommet
    angle = 45  # angle des cotes
    surete = 0.3  # valeur a ajouter a la profondeur par precaution
    volumeSac = 0.03  # 1/3pied cube            #### 0.03m3 = 1 pied3

    arcpy.env.workspace = fctUtilitaires.get_scratch_dir()
    arcpy.env.overwriteOutput = True

    # Conversion du raster en polygone
    arcpy.CheckOutExtension('Spatial')
    ##    boolRaster = arcpy.sa.LessThan(in_raster, 0)
    ##    filteredRaster = arcpy.sa.SetNull(boolRaster, boolRaster, "VALUE = 0")
    rasBool = arcpy.sa.Int(arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, 1))
    filteredRaster = arcpy.sa.SetNull(rasBool, rasBool, "VALUE = 0")
    # outPolygon = os.path.join('in_memory', 'zi')
    outPolygon = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\zi_polygon.shp"
    arcpy.RasterToPolygon_conversion(filteredRaster, outPolygon, 'NO_SIMPLIFY')

    # Clip des lignes par le polygone
    outClip = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\clip_lines.shp"
    arcpy.Clip_analysis(in_lines, outPolygon, outClip)

    # Multipart to single part
    outMulti = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\multi_lines.shp"
    arcpy.MultipartToSinglepart_management(outClip, outMulti)

    # Verification que les extremites des lignes sont a l'exterieur de la zone couverte par le raster
    # ou que les lignes soient fermees (1er point et dernier point identique)
    in_lines_copy = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\copy_lines.shp"
    # arcpy.Copy_management(in_lines, in_lines_copy)
    arcpy.Copy_management(outClip, in_lines_copy)

    # arcpy.ExtendLine_edit(outMulti, "15 Feet") ###

    # Densification des lignes satisfaisant les criteres
    # arcpy.Densify_edit(outMulti, 'DISTANCE', 0.2)
    arcpy.Densify_edit(in_lines_copy, 'DISTANCE', 0.2)

    start = datetime.datetime.now()
    allPts = os.path.join('in_memory', 'allPts')
    # arcpy.FeatureVerticesToPoints_management(outMulti, allPts, 'All')
    arcpy.FeatureVerticesToPoints_management(in_lines_copy, allPts, 'All')

    # Extractition des valeurs sur le raster pour chaque point
    ##    allPtsZ = os.path.join('in_memory','allPtsZ')
    allPtsZ = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\allPtsZ.shp"
    arcpy.sa.ExtractValuesToPoints(allPts, in_raster, allPtsZ, 'INTERPOLATE')
    print datetime.datetime.now() - start
    print elapsed_time()

    print elapsed_time()
    OIDname_in_lines_copy = arcpy.Describe(in_lines_copy).OIDFieldname

    arcpy.AddField_management(in_lines_copy, 'Volume', 'FLOAT')
    arcpy.AddField_management(in_lines_copy, 'Nb_Sacs', 'INTEGER')
    arcpy.AddField_management(in_lines_copy, 'Comments', 'TEXT')
    print elapsed_time()
    with arcpy.da.UpdateCursor(in_lines_copy,
                               ['SHAPE@', OIDname_in_lines_copy, 'Volume', 'Nb_Sacs', 'Comments']) as ucursor:
        for urow in ucursor:
            volumeTotal = 0
            if urow[0].firstPoint.X == urow[0].lastPoint.X and \
                    urow[0].firstPoint.Y == urow[0].lastPoint.Y:
                ferme = True
            else:
                ferme = False

            with arcpy.da.SearchCursor(allPtsZ, ['RASTERVALU'], """"ORIG_FID" = {0}""".format(urow[1])) as scursor:
                allDepth = []
                for srow in scursor:
                    allDepth.append(srow[0])

            if not ferme and (allDepth[0] != -9999 or allDepth[-1] != -9999):
                urow[4] = 'Digue non etanche'
            else:
                for d in allDepth:
                    if d != -9999:
                        base = baseTrapeze(d + surete, angle, sommet)
                        volumeTotal += volumeTrapeze(d + surete, sommet, base, 0.2)

                urow[2] = volumeTotal
                urow[3] = volumeTotal / volumeSac
            ucursor.updateRow(urow)


def create_convex_hull(in_fc, grouping_field=None):
    """
    generate convex hull features optionally grouping input features;
    if no grouping_field specified, a single Convex Hull will be generated
    for all input features
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
    arcpy.env.workspace = arcpy.Describe(in_bat).path
    arcpy.env.overwriteOutput = True
    dissolve_buf = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\dissolve_buf.shp"
    CHdissolve_buf = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\ConvexHulldissolve_buf.shp"

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


def main():
    inRas = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_hauteur_eau_debit_1369.tif"
    inLines = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_digues.shp"
    inFusion = 'True'
    outFile = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\out_digues.shp"

    arcpy.env.overwriteOutput = True

    desc = arcpy.Describe(inLines)

    if desc.shapeType == "Polygon":
        if inFusion in ['true', 'True']:
            dissolve = 'ALL'
        else:
            dissolve = 'NONE'

        arcpy.Buffer_analysis(inLines, outFile, "8 FEET", "FULL", "ROUND", dissolve)
        inLines = outFile

    digue(inLines, inRas)


if __name__ == '__main__':
    # main()

    Bat = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\Digues\_batiments.shp"
    # where_clause = '"FID" = 3 OR "FID" = 5 OR "FID" = 16 OR "FID" = 17 OR "FID" = 22'
    # # where_clause = '"CP" = \'J3B 4N6\''
    # arcpy.Select_analysis(inBat, batSelect, where_clause)
    line_creator(Bat)
    print(elapsed_time())
