# # -*- coding: utf-8 -*-
import ogr
import sys
import geopandas as gpd
from shapely.geometry import MultiPolygon, JOIN_STYLE
import itertools
import osr

import arcpy
import arcpy.cartography as ca

import sys
# sys.path.extend([r"C:\Program Files\QGIS Valmiera\apps", r"C:\Program Files\QGIS Valmiera\apps\qgis\bin", r"C:\Program Files\QGIS Valmiera\apps\Python27"])
sys.path.extend([r"C:\OSGeo4W64\apps\qgis", r"C:\Program Files\QGIS 3.0\apps\Python36"])
import qgis.core

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
# import shapely
# from shapely.geometry import Polygon
# filled_shape = Polygon(shape_with_holes.exterior)


from shapely.geometry import mapping, Polygon
import fiona



from qgis.core import *






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

#################################TEST OPENCV #########################
# import cv2 as cv
# import Utils_MP
#
# image = cv.imread("E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot5.png")
# gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # grayscale
# _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)  # threshold
# kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))
# dilated = cv.dilate(thresh, kernel, iterations=10)  # dilate
# #_, contours, hierarchy = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)  # get contours
#
# #dst1 = cv.inpaint(image, dilated, 3, cv.INPAINT_TELEA)
# dst2 = cv.inpaint(image, dilated, 3, cv.INPAINT_NS)
# gray2 = cv.cvtColor(dst2, cv.COLOR_BGR2GRAY)  # grayscale
#
#
# ret, thresh1 = cv.threshold(gray2, 234, 255, cv.THRESH_BINARY)  # 234 # with residential buildings 236
# # cv.imshow('Image thresh1', thresh1)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh2 = cv.threshold(gray2, 237, 255, cv.THRESH_BINARY)  # 237 without residential buildings 237
# # cv.imshow('Image thresh2', thresh2)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# residentiel = thresh1 - thresh2  # residential buildings in white
# # cv.imshow('Image residentiel', residentiel)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh3 = cv.threshold(gray2, 247, 255, cv.THRESH_BINARY)  # with commercial buildings
# # cv.imshow('Image thresh3', thresh3)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh4 = cv.threshold(gray2, 248, 255, cv.THRESH_BINARY)  # without commercial buildings
# # cv.imshow('Image thresh4', thresh4)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# commercial = thresh3 - thresh4  # commercial buildings in white
# cv.imshow('Image commercial', commercial)
# cv.waitKey(0)
# cv.destroyAllWindows()
# kernel = cv.getStructuringElement(cv.MORPH_RECT, (20, 20))
# closing = cv.morphologyEx(commercial, cv.MORPH_CLOSE, kernel)
# cv.imshow('Image closing', closing)
# cv.waitKey(0)
# cv.destroyAllWindows()
# ret, thresh5 = cv.threshold(gray2, 238, 255, cv.THRESH_BINARY)  # with 3D buildings 239
# ret, thresh6 = cv.threshold(gray2, 240, 255, cv.THRESH_BINARY)  # without 3D buildings 240
# building_3d = thresh5 - thresh6  # 3D buildings in white
# #  Erase white lines
# minThick = 15  # Define minimum thickness
# se = cv.getStructuringElement(cv.MORPH_ELLIPSE, (minThick, minThick))  # define a disk element
# img_bat = 255 * cv.morphologyEx(residentiel.astype('uint8'), cv.MORPH_OPEN, se)
# img_bat += 255 * cv.morphologyEx(commercial.astype('uint8'), cv.MORPH_OPEN, se)
# img_bat += 255 * cv.morphologyEx(building_3d.astype('uint8'), cv.MORPH_OPEN, se)





# Utils_MP.tracer_contour(img_bat, image)
# features = []
# Utils_MP.image2features(img_bat, features, 45.45, -73.25)
# print features

# cv.imshow('Image Google', thresh)
# cv.imshow('Image Google', kernel)
# cv.imshow('Image Google', dilated)
# cv.imshow('Image Google', dst1)
# cv.waitKey(0)
# cv.imshow('Image Google', img_bat)
# cv.waitKey(0)
# cv.destroyAllWindows()



# for each contour found, draw a rectangle around it on original image
# for contour in contours:
#     # get rectangle bounding contour
#     [x, y, w, h] = cv.boundingRect(contour)
#
#     # discard areas that are too large
#     # if h > 300 and w > 300:
#     #     continue
#     #
#     # # discard areas that are too small
#     # if h < 40 or w < 40:
#     #     continue
#
#     # draw rectangle around contour on original image
#     cv.rectangle(image, (x, y), (x+w, y+h), (255, 0, 255), 2)

# write original image with added contours to disk
#cv.imwrite("contoured.jpg", image)