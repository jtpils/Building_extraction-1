# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# split_building.py
# Created on: 2019-06-20
# Author : Charles Tousignant
# Project : GARI
# Description : Split buildings according to property limits
# ---------------------------------------------------------------------------
from utils import *
import operator
arcpy.env.overwriteOutput = True

# set paths test
# bat_path = cwd + r"\input\bat_test_small.shp"
# cadastre_path = cwd + r"\input\cadastre_test_small.shp"
# output_path = cwd + r"\output\split_building.shp"

# set paths
bat_path = cwd + r"\input\MS_Gatineau.shp"  # Microsoft building shapefile path
cadastre_path = cwd + r"\input\cadastre_Gatineau.shp"  # property limits shapefile path
output_path = cwd + r"\output\split_building.shp"  # output shapefile path

# Intersecting buildings with property limits
arcpy.Intersect_analysis([bat_path, cadastre_path], "in_memory/bat_intersect", join_attributes="ONLY_FID")

# Run the Copy Features tool, setting the output to the geometry object.
# geometries is returned as a list of geometry objects.
bat_intersect_geom = arcpy.CopyFeatures_management("in_memory/bat_intersect", arcpy.Geometry())
bat_geom = arcpy.CopyFeatures_management(bat_path, arcpy.Geometry())
cadastre_geom = arcpy.CopyFeatures_management(cadastre_path, arcpy.Geometry())


output_geom_list = []
# Add buildings that are outside of the property limits shapefile
i=0
for bat in bat_geom:
    i+=1
    print i
    disjoint = True
    for lot in cadastre_geom:
        if not bat.disjoint(lot):
            disjoint = False
    if disjoint:
        output_geom_list.append(bat)

# Walk through each building geometry
for bat in bat_intersect_geom:
    geom_list, area_list, length_list = [], [], []
    for lot in cadastre_geom:
        # If lot contains building, append the geometry, area and length to a list
        if lot.contains(bat):
            # Spliting multipart to single part polygons if needed
            if bat.isMultipart:
                arcpy.MultipartToSinglepart_management(bat, "in_memory/singlepart")
                temp_geom = arcpy.CopyFeatures_management("in_memory/singlepart", arcpy.Geometry())
                for temp_bat in temp_geom:
                    geom_list.append(temp_bat)
                    area_list.append(temp_bat.area)
                    length_list.append(temp_bat.length)
            else:
                geom_list.append(bat)
                area_list.append(bat.area)
                length_list.append(bat.length)
    print("area")
    print(area_list)
    print("length")
    print(length_list)
    print("---------------------------")
    # Add the biggest building of the lot
    if area_list:
        index, value = max(enumerate(area_list), key=operator.itemgetter(1))
        if value > 1.5*length_list[index]:
            output_geom_list.append(geom_list[index])

# Create final output
arcpy.CopyFeatures_management(output_geom_list, output_path)











# # Walk through each cadastre geometry
# output_geom_list = []
# for lot in cadastre_geom:
#     geom_list, area_list, length_list = [], [], []
#     # Walk through each building geometry
#     for bat in bat_geom:
#         # If lot contains building, append the geometry, area and length to a list
#         if lot.contains(bat):
#             # Spliting multipart to single part polygons if needed
#             if bat.isMultipart:
#                 arcpy.MultipartToSinglepart_management(bat, temp_single_path)
#                 temp_geom = arcpy.CopyFeatures_management(temp_single_path, arcpy.Geometry())
#                 for temp_bat in temp_geom:
#                     geom_list.append(temp_bat)
#                     area_list.append(temp_bat.area)
#                     length_list.append(temp_bat.length)
#             else:
#                 geom_list.append(bat)
#                 area_list.append(bat.area)
#                 length_list.append(bat.length)
#     print("area")
#     print(area_list)
#     print("length")
#     print(length_list)
#     print("---------------------------")
#     if area_list:
#         index, value = max(enumerate(area_list), key=operator.itemgetter(1))
#         if value > 1.5*length_list[index]:
#             output_geom_list.append(geom_list[index])
#
# arcpy.Delete_management(temp_single_path)
# # Create final output
# arcpy.CopyFeatures_management(output_geom_list, output_path)
