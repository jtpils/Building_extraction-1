# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# geocode.py
# Created on: 2018-05-25
# Author : Charles Tousignant
# Project : GARI
# Description : Reverse geocoding of buildings in the shapefile.
# Create and fill new fields related to the address in the attribute table.
# ---------------------------------------------------------------------------
import re
import geocoder
import ogr
import osr
from utils import *


def latlon2address(lat, lon):
    """
    Reverse geocoding from coordinates to addresses
    :param lat: (float) latitude
    :param lon: (float) longitude
    :return n: (tuple) address of coordinate (address, street, city, state, postal, country)
    """
    key = "AjBnbJXTfnqbk1fgDACBIfrnhHs6SMQGGi6XGzaqCw2lyQ_RjtnCSQaCGrFlXS_L"  # quota de 125 000 requêtes/année
    b = geocoder.bing([lat, lon], method="reverse", key=key)
    timeout = time.time() + 10
    while b.city is None:
        b = geocoder.bing([lat, lon], method="reverse", key=key)
        if b.city is None and time.time() > timeout:  # if google can't find the address after a certain amount of time
            return "no info", "0", "no info", "no info", "no info", "no info", "no info"
            # sys.exit("Bing ne trouve pas d'adresse, veuillez réessayer")
    no_st = b.street
    print(no_st)  # for bug detection
    # no info
    if b.street is None:
        no, st = "0", "no info"
    # no house number
    elif not no_st[0].isnumeric():
        no = "0"
        st = no_st
    # no house number and street name starting with a number (ex: 4th street)
    elif (no_st[0].isnumeric() and no_st[1].isalpha()) or \
            (no_st[0].isnumeric() and no_st[1].isnumeric() and no_st[2].isalpha()) or \
            (no_st[0].isnumeric() and no_st[1].isnumeric() and no_st[2].isnumeric() and no_st[3].isalpha()):
        no = "0"
        st = no_st
    else:
        match = re.match(r'(\d+)(?:-\d+(?=\s))?\s(.*)', no_st).groups()
        no = match[0]
        st = match[1]
    st_mod = modif_nom_rue(st)
    adresse_im = no + " " + st_mod
    #return b.address, no, st, b.city, b.state, b.postal, b.country
    return adresse_im, no, st, b.city, b.state, b.postal, b.country


def geocode_shapefile(in_shapefile, out_shapefile):
    """
    create and calculate attributary table fields for buildings addresses
    :param in_shapefile: (string) input building shapefile
    :param out_shapefile: (string) output building shapefile
    """
    # make a copy of the input shapefile
    if os.path.exists(out_shapefile):
        arcpy.Delete_management(out_shapefile)
    arcpy.Copy_management(in_shapefile, out_shapefile)

    # create additionnal fields
    arcpy.AddField_management(out_shapefile, "ID_bat", "LONG", 9)

    arcpy.AddField_management(out_shapefile, "Adresse_im", "TEXT", field_length=150)
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

    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(in_shapefile)
    layer = dataset.GetLayer()
    inSpatialRef = layer.GetSpatialRef()

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)  # WGS 84
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # add address information to output shapefile
    fields = ["ID_bat", "Adresse_im", "Num_Civ", "Rue", "Ville", "Province", "CP", "Pays"]
    point = ogr.Geometry(ogr.wkbPoint)
    with arcpy.da.UpdateCursor(out_shapefile, fields) as cursor:
        i = 0
        for row in cursor:
            point.AddPoint(centroid[i][0], centroid[i][1])
            point.Transform(coordTransform)
            info = latlon2address(point.GetY(), point.GetX())
            for j in range(len(fields)):
                if j == 0:
                    row[j] = i
                else:
                    row[j] = info[j-1]
                    if row[j] is None:  # when we get no info
                        row[j] = "no info"
            cursor.updateRow(row)
            i += 1
            print("{} buildings geolocalized.       {}".format(i, elapsed_time()))


def modif_nom_rue(nom_rue):
    # Modifications générales
    if nom_rue[-1] == "N":
        nom_rue = nom_rue + "ord"
    if nom_rue[-1] == "S":
        nom_rue = nom_rue + "ud"
    if nom_rue[-1] == "E":
        nom_rue = nom_rue + "st"
    if nom_rue[-1] == "O":
        nom_rue = nom_rue + "est"
    if nom_rue.find("St-") != -1:
        i = nom_rue.find("St-")
        nom_rue = nom_rue[0:i] + "Saint-" + nom_rue[i+3:]
    if nom_rue.find("Ste-") != -1:
        i = nom_rue.find("Ste-")
        nom_rue = nom_rue[0:i] + "Sainte-" + nom_rue[i + 4:]
    if nom_rue[0:4] == "1er ":
        nom_rue = nom_rue[4:] + " 1e"
    if nom_rue[0].isdigit():
        index_e = nom_rue.find("e")
        nom_rue = nom_rue[index_e + 2:] + " " + nom_rue[0:index_e + 1]

    # Exceptions SJSR
    if nom_rue == "Chemin des Patriotes Est":
        nom_rue = "Route 133"

    return nom_rue


def main():
    # cwd = os.getcwd()
    # inShapefile = cwd + r"\output\building_footprint.shp"
    # outShapefile = cwd + r"\output\building_footprint_geocode.shp"

    # inShapefile = r"H:\shapefile\TEST\bat_TEST.shp"
    # outShapefile = r"H:\shapefile\TEST\bat_TEST_RESULT.shp"

    inShapefile = r"H:\shapefile\Zones_extraction\SJSR\SJSR_Sabrevois_zone_risk_verif.shp"
    outShapefile = r"H:\shapefile\TEST\SJSR_SabrevoisBAT.shp"

    geocode_shapefile(inShapefile, outShapefile)

    print("##############################")
    print("Building shapefile reverse geocode complete!")
    print(elapsed_time())
    print("##############################")


if __name__ == "__main__":
    main()
    # print(modif_nom_rue("1er Avenue"))