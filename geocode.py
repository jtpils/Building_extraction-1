# -*- coding: utf-8 -*-
import sys
import geocoder
import ogr
import osr
from Utils_MP import *


def latlon2address(lat, lon):
    b = geocoder.bing([lat, lon], method="reverse", key="AigfUkIm24vYk0sWgbUwgBv5klsfc5tAwFArERnDcr39MnTbPS5WE9ZRko8WiMgc")
    timeout = time.time() + 7
    while b.city is None:
        b = geocoder.bing([lat, lon], method="reverse", key="AigfUkIm24vYk0sWgbUwgBv5klsfc5tAwFArERnDcr39MnTbPS5WE9ZRko8WiMgc")
        if b.city is None and time.time() > timeout:  # if google can't find the address after a certain amount of time
            sys.exit("Bing ne trouve pas d'adresse, veuillez réessayer")
    #return b.address, b.housenumber, b.street, b.city, b.state, b.postal, b.country
    return b. address, b.street, b.city, b.state, b.postal, b.country


def geocode_shapefile(in_shapefile, out_shapefile):

    # make a copy of the input shapefile
    if arcpy.Exists(out_shapefile):
        arcpy.Delete_management(out_shapefile)
    arcpy.Copy_management(in_shapefile, out_shapefile)

    # create additionnal fields
    arcpy.AddField_management(out_shapefile, "Adresse", "TEXT", field_length=150)
    # arcpy.AddField_management(outShapefile, "Num_Civ", "LONG", 9)
    arcpy.AddField_management(out_shapefile, "Rue", "TEXT", field_length=80)
    arcpy.AddField_management(out_shapefile, "Ville", "TEXT", field_length=80)
    arcpy.AddField_management(out_shapefile, "Province", "TEXT", field_length=30)
    arcpy.AddField_management(out_shapefile, "CP", "TEXT", field_length=10)
    arcpy.AddField_management(out_shapefile, "Pays", "TEXT", field_length=20)

    # convert shapefile to NumPy Array of centroid
    np_array = arcpy.da.FeatureClassToNumPyArray(out_shapefile, "SHAPE@XY")
    centroid = []  # list of NumPy Array
    for x in np.nditer(np_array):
        var = np.array(x).tolist()
        centroid.append(var[0])

    # prepare coordinates transform to WGS 84
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(2950)  # NAD_1983_CSRS_MTM_8
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)  # WGS 84
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # add address information to output shapefile
    # fields = ["Adresse", "Num_Civ", "Rue", "Ville", "Province", "CP", "Pays"]
    fields = ["Adresse", "Rue", "Ville", "Province", "CP", "Pays"]
    point = ogr.Geometry(ogr.wkbPoint)
    with arcpy.da.UpdateCursor(out_shapefile, fields) as cursor:
        i = 0
        for row in cursor:
            point.AddPoint(centroid[i][0], centroid[i][1])
            point.Transform(coordTransform)
            info = latlon2address(point.GetY(), point.GetX())
            for j in range(len(fields)):
                row[j] = info[j]
                if row[j] is None:  # when we get no info
                    row[j] = "no info"
            cursor.updateRow(row)
            i += 1
            print("{} buildings geolocalized.       {}".format(i, elapsed_time()))


if __name__ == "__main__":
    inShapefile = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/BV_Richelieu.shp"
    outShapefile = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/BV_Richelieu_geocode.shp"

    geocode_shapefile(inShapefile, outShapefile)
