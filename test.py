# # -*- coding: utf-8 -*-

import arcpy


# file_path = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\copy.shp"
# file_path_out = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\copy_out.shp"
# #arcpy.AddField_management(file_path, "superficie", "FLOAT", 9)
# #arcpy.AddGeometryAttributes_management(file_path, "CENTROID;PERIMETER_LENGTH;AREA", "METERS", "SQUARE_METERS")
#
# arcpy.SelectLayerByAttribute_management(file_path, "NEW_SELECTION", '"POLY AREA" > 4.0')
# arcpy.Eliminate_management(file_path, file_path_out)








# import os
# file_path = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\building_footprin.shp"
#
# while os.path.exists(file_path):
#     try:
#         int(file_path[-5])
#     except ValueError:
#         file_path = file_path[0:-4] + "1.shp"
#     else:
#         number = str(int(file_path[-5]) + 1)
#         file_path = file_path[0:-5] + number + ".shp"
#
#
# print file_path














# import ogr
# import osr
#
#
# in_shape = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/zone_risque/zone_test_mtm8.shp"
# out_shape = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/zone_risque/test.shp"
#
# # arcpy.MinimumBoundingGeometry_management(in_shape, out_shape, geometry_type="ENVELOPE")
#
# #  project
# # sr = arcpy.SpatialReference(3857)  # WGS_1984_Web_Mercator_Auxiliary_Sphere
# # arcpy.DefineProjection_management(building_footprint_1, sr)  # Define Projection
# # sr2 = arcpy.SpatialReference(2950)  # NAD_1983_CSRS_MTM_8
# # arcpy.Project_management(building_footprint_1, building_footprint_2, sr2)  # Project
# # arcpy.Delete_management(building_footprint_1)
#
#
# shapefile = ogr.Open(in_shape)
# layer = shapefile.GetLayer(0)
# feature = layer.GetFeature(0)
# geom = feature.GetGeometryRef()
#
# target = osr.SpatialReference()
# target.ImportFromEPSG(4326)
# source = geom.GetSpatialReference()
# transform = osr.CoordinateTransformation(source, target)
# geom.Transform(transform)
#
# envelope = geom.GetEnvelope()
# print(envelope)






































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