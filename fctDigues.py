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


def volumeTrapeze(h, sommet, base, profondeur):
    return (sommet + base) / 2 * h * profondeur


def baseTrapeze(h, angle, sommet):
    return math.tan(math.radians(angle)) * h * 2 + sommet


def digue(in_lines, in_raster):
    # Parametre de configuration de la digue
    sommet = 0.3  # Largeur du sommet
    angle = 45  # angle des cotes
    surete = 0.3  # valeur a ajouter a la profondeur par precaution
    volumeSac = 0.03  # 1/3pied cube

    arcpy.env.workspace = fctUtilitaires.get_scratch_dir()
    arcpy.env.overwriteOutput = True

    # Conversion du raster en polygone
    arcpy.CheckOutExtension('Spatial')
    ##    boolRaster = arcpy.sa.LessThan(in_raster, 0)
    ##    filteredRaster = arcpy.sa.SetNull(boolRaster, boolRaster, "VALUE = 0")
    rasBool = arcpy.sa.Int(arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, 1))
    filteredRaster = arcpy.sa.SetNull(rasBool, rasBool, "VALUE = 0")
    outPolygon = os.path.join('in_memory', 'zi')
    outPolygon = r'E:\Jimmy\Projets\GARI\Test_GARI_2018\Toolbox 2018\outputs\jim\zi_polygon.shp'
    arcpy.RasterToPolygon_conversion(filteredRaster, outPolygon, 'NO_SIMPLIFY')

    # Clip des lignes par le polygone
    outClip = r'E:\Jimmy\Projets\GARI\Test_GARI_2018\Toolbox 2018\outputs\jim\clip_lines.shp'
    arcpy.Clip_analysis(in_lines, outPolygon, outClip)

    # Multipart to single part
    outMulti = r'E:\Jimmy\Projets\GARI\Test_GARI_2018\Toolbox 2018\outputs\jim\multi_lines.shp'
    arcpy.MultipartToSinglepart_management(outClip, outMulti)

    ##    #Verification que les extremites des lignes sont a l'exterieur de la zone couverte par le raster
    ##    #ou que les lignes soient fermees (1er point et dernier point identique)
    ##    in_lines_copy = r'E:\Jimmy\Projets\GARI\Test_GARI_2018\Toolbox 2018\outputs\jim\copy_lines.shp'
    ##    arcpy.Copy_management(in_lines,in_lines_copy)

    # Densification des lignes satisfaisant les criteres
    arcpy.Densify_edit(outMulti, 'DISTANCE', 0.2)

    start = datetime.datetime.now()
    allPts = os.path.join('in_memory', 'allPts')
    arcpy.FeatureVerticesToPoints_management(outMulti, allPts, 'All')

    # Extractition des valeurs sur le raster pour chaque point
    ##    allPtsZ = os.path.join('in_memory','allPtsZ')
    allPtsZ = r'E:\Jimmy\Projets\GARI\Test_GARI_2018\Toolbox 2018\outputs\jim\allPtsZ.shp'
    arcpy.sa.ExtractValuesToPoints(allPts, in_raster, allPtsZ, 'INTERPOLATE')
    print datetime.datetime.now() - start

    raw_input()
    OIDname_in_lines_copy = arcpy.Describe(in_lines_copy).OIDFieldname
    arcpy.AddField_management(in_lines_copy, 'Volume', 'FLOAT')
    arcpy.AddField_management(in_lines_copy, 'Nb_Sacs', 'INTEGER')
    arcpy.AddField_management(in_lines_copy, 'Comments', 'TEXT')
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


def main():
    inRas = r"Z:\GARI\GARI - Versions\V1.6.1\inputs\Exemple raster de hauteurs d'eau\hauteur_eau_debit_1369.tif"
    inLines = r'E:\Jimmy\Projets\GARI\test_digues.shp'
    inFusion = 'True'
    outFile = r'E:\Jimmy\Projets\GARI\out_test_digues.shp'

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

    if dissolve == 'ALL':
        pass


if __name__ == '__main__':
    main()
