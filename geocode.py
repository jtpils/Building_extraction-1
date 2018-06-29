# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# geocode.py
# Created on: 2018-05-25
# Author : Charles Tousignant
# Project : GARI
# Description : Géocode automatique des addresses de tout les bâtiments d'un
# shapefile. Entre les addresses dans différents champs de la table attributaire
# ---------------------------------------------------------------------------
import sys
import geocoder
import ogr
import osr
import re
from Utils_MP import *


def latlon2address(lat, lon):
    """
    Reverse geocoding from coordinates to addresses
    :param lat: (float) latitude
    :param lon: (float) longitude
    :return n: (tuple) address of coordinate (address, street, city, state, postal, country)
    """
    b = geocoder.bing([lat, lon], method="reverse", key="AjVyhHv7lq__hT5_XLZ8jU0WbQpUIEUhQ7_nlHDw9NlcID9jRJDYLSSkIQmuQJ82")  # quota de 125 000 requêtes/année
    timeout = time.time() + 7
    while b.city is None:
        b = geocoder.bing([lat, lon], method="reverse", key="AjVyhHv7lq__hT5_XLZ8jU0WbQpUIEUhQ7_nlHDw9NlcID9jRJDYLSSkIQmuQJ82")
        if b.city is None and time.time() > timeout:  # if google can't find the address after a certain amount of time
            sys.exit("Bing ne trouve pas d'adresse, veuillez réessayer")
    no_st = b.street
    print no_st  # for bug detection
    if b.street is None:
        no, st = "0", "no info"
    elif not no_st[0].isnumeric():
        no = "0"
        st = no_st
    else:
        match = re.match(r'(\d+)(?:-\d+(?=\s))?\s(.*)', no_st).groups()
        no = match[0]
        st = match[1]

    return b.address, no, st, b.city, b.state, b.postal, b.country


def geocode_shapefile(in_shapefile, out_shapefile):
    """
    create and calculate attributary table fields for buildings addresses
    :param in_shapefile: (string) input building shapefile
    :param out_shapefile: (string) output building shapefile
    """
    # make a copy of the input shapefile
    # if arcpy.Exists(out_shapefile):
    #     arcpy.Delete_management(out_shapefile)
    # arcpy.Copy_management(in_shapefile, out_shapefile)
    if os.path.exists(out_shapefile):
        arcpy.Delete_management(out_shapefile)
    arcpy.Copy_management(in_shapefile, out_shapefile)

    # create additionnal fields
    arcpy.AddField_management(out_shapefile, "Adresse", "TEXT", field_length=150)
    arcpy.AddField_management(out_shapefile, "Num_Civ", "LONG", 9)
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
    fields = ["Adresse", "Num_Civ", "Rue", "Ville", "Province", "CP", "Pays"]
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


def main():
    """
    Main function.
    Change the path of inShapefile and outShapefile for the desired building shapefile to geocode.
    """
    inShapefile = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint.shp"
    outShapefile = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_geocode.shp"
    geocode_shapefile(inShapefile, outShapefile)


if __name__ == "__main__":
    main()
    print("##############################")
    print("Building shapefile reverse geocode complete!")
    print(elapsed_time())
    print("##############################")
