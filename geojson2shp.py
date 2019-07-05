# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# geojson2shp.py
# Created on: 2019-06-10
# Author : Charles Tousignant
# Project : GARI
# Description : Convert MicroSoft building footprint from geojson to shapefile format
# Works with Python 2.7
# ---------------------------------------------------------------------------
import ijson
from utils import *

feature_number = 0
feature_extracted_count = 0
feature_coord = []
feature_coord_list = []
all_features_coord_list = []
# Path to Microsoft building footprint geojson file
geojson_path = cwd + "\input\Quebec.geojson"
# Bounding box
bbox = [-76.07338, 45.430631, -74.949861, 46.728920]  # lat(SW), lon(SW), lat(NE), lon(NE)
# [-73.272820, 45.253776, -73.237197, 45.348230]  # Ville SJSR
# [-73.382347, 45.005880, -73.072251, 46.060711]  # BV Richelieu
# [-75.214771, 45.563755, -74.960552, 46.157250]  # BV Petite-Nation
# [-76.07338, 45.430631, -74.949861, 46.728920] #Gatineau + Le lièvre + Petite-nation


def add_coord(feat_coord):
    coord = []
    j = 0
    for _ in feat_coord:
        j += 1
        coord.append(_)
        if j % 2 == 0:
            # coords = (coord[0], coord[1])
            feature_coord_list.append((coord[0], coord[1]))
            coord = []
    all_features_coord_list.append(feature_coord_list)


for prefix, the_type, value in ijson.parse(open(geojson_path)):
    # print type(prefix), type(the_type), type(value)
    # print prefix, "####", the_type, "####", value, "####"

    if the_type == "number".encode():
        feature_coord.append(float(value))

    if value == "Feature".encode():
        feature_number += 1  # counting number of features
        if feature_coord:
            # Add coordinate if feature_coord is inside bbox
            if (bbox[0] < feature_coord[0] < bbox[2]) and (bbox[1] < feature_coord[1] < bbox[3]):
                add_coord(feature_coord)
                feature_extracted_count += 1  # counting number of extracted features
        feature_coord = []
        feature_coord_list = []
        if feature_number % 10000 == 0:
            print("{:.1f}% complete... {}".format(float(feature_number)/2535293*100, elapsed_time()))

# for last feature
if (bbox[0] < feature_coord[0] < bbox[2]) and (bbox[1] < feature_coord[1] < bbox[3]):
    add_coord(feature_coord)

# Create a feature class with a spatial reference of GCS WGS 1984
arcpy.env.overwriteOutput = True
result = arcpy.management.CreateFeatureclass(cwd, "\output\MS_buildings", "POLYGON", spatial_reference=4326)
feature_class = result[0]
# Write feature to new feature class
with arcpy.da.InsertCursor(feature_class, ['SHAPE@']) as cursor:
    for _ in range(len(all_features_coord_list)):
        cursor.insertRow([all_features_coord_list[_]])

MS_buildings = cwd + "\output\MS_buildings.shp"
MS_buildings_proj = cwd + "\output\MS_buildings_proj.shp"
# Change projection to Quebec Lambert
sr = arcpy.SpatialReference(32198)
arcpy.Project_management(MS_buildings, MS_buildings_proj, sr)  # Project
arcpy.Delete_management(MS_buildings)

print("{} features where extracted".format(feature_extracted_count))
print(elapsed_time())
