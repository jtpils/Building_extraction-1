# # -*- coding: utf-8 -*-
import ogr
import sys
import geopandas as gpd
from shapely.geometry import MultiPolygon, JOIN_STYLE
import itertools
import osr

import arcpy
import arcpy.cartography as ca
# building_footprint0 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_del.shp"
# building_footprint = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_del_dis.shp"
#
# arcpy.Dissolve_management(building_footprint0, building_footprint, multi_part="SINGLE_PART")

# file_path = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\building_footprint_del_dis.shp"
# file_path_out = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\copy_out.shp"
# # arcpy.AddField_management(file_path, "superficie", "FLOAT", 9)
# # arcpy.AddGeometryAttributes_management(file_path, "CENTROID;PERIMETER_LENGTH;AREA", "METERS", "SQUARE_METERS")
# table = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\table_out"

# arcpy.MakeTableView_management(file_path, table)
# arcpy.SelectLayerByAttribute_management(table, "NEW_SELECTION", '"POLY_AREA" > 4.0')
# arcpy.Eliminate_management(file_path, file_path_out)
































###############################fonctionne mais pas de proj. alternative a aggragate polygons###########
import geopandas as gpd
# eps=5 # width for dilating and eroding (buffer)
# dist = 2  # threshold distance
# # read the original shapefile
# df = gpd.read_file("E:/Charles_Tousignant/Python_workspace/Gari/shapefile/extr.shp")
# crs = df.crs
# print type(crs)
# # create new result shapefile
# col = ['geometry']
# res = gpd.GeoDataFrame(columns=col)
# # iterate over pairs of polygons in the GeoDataFrame
# for i, j in list(itertools.combinations(df.index, 2)):
#  distance = df.geometry.ix[i].distance( df.geometry.ix[j]) # distance between polygons i and j in the shapefile
#  print distance
#  if distance < dist:
#      e = MultiPolygon([ df.geometry.ix[i],df.geometry.ix[j]])
#      fx = e.buffer(eps, 1, join_style=JOIN_STYLE.mitre).buffer(-eps, 1, join_style=JOIN_STYLE.mitre)
#      res = res.append({'geometry':fx}, ignore_index=True)
#      print type(res)
#
# # save the resulting shapefile
# #res = res.to_crs(epsg=2950)
# res.to_file("E:/Charles_Tousignant/Python_workspace/Gari/shapefile/aggregates.shp")
#########################################################################################################










###########  TEST couleur#########################
# import Utils_MP
# import cv2 as cv
#
# im_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/test3.png"
# img_google = cv.imread(im_path)
# img_gray = cv.cvtColor(img_google, cv.COLOR_BGR2GRAY)
#
# image_bat = Utils_MP.building_image(img_google)
# #Utils_MP.tracer_contour(image_bat, img_google)
#
# ret, thresh1 = cv.threshold(img_gray, 234, 255, cv.THRESH_BINARY)  # with 3D buildings 239
# ret, thresh2 = cv.threshold(img_gray, 237, 255, cv.THRESH_BINARY)  # without 3D buildings 240
# residentiel = thresh1 - thresh2  #3D buildings in white
#
# Utils_MP.tracer_contour(residentiel, img_google)

# cv.imshow("T1", thresh1)
# cv.imshow("T2", thresh2)
# cv.imshow("res", residentiel)
# cv.imshow("gray", img_gray)
# cv.waitKey(0)
#image2features(image_bat, feat, lat, lon_s)