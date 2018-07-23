# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Utils_MP.py
# Created on: 2018-05-25
# Author : Charles Tousignant
# Project : GARI
# Description : Fonctions utilitaires
# ---------------------------------------------------------------------------
import numpy as np
import cv2 as cv
import arcpy
#import arcpy.cartography as ca
import math
import time
import datetime
import os


start_time = time.time()  # start timer


def elapsed_time():
    temps = str(datetime.timedelta(seconds=time.time() - start_time))
    return "Elapsed time: {}".format(temps)


def new_shp_name(file_path):
    while os.path.exists(file_path):
        try:
            int(file_path[-5])
        except ValueError:
            file_path = file_path[0:-4] + "1.shp"
        else:
            number = str(int(file_path[-5]) + 1)
            file_path = file_path[0:-5] + number + ".shp"
    return file_path


def building_image(img_google):
    """
    Create a binary image with detected buildings
    :param img_google: (RBG image) Screenshot image
    :return img_bat: (grayscale image) Image of buildings
    """
    img = cv.imread(img_google)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, thresh1 = cv.threshold(img_gray, 234, 255, cv.THRESH_BINARY)  # 234 # with residential buildings 236
    ret, thresh2 = cv.threshold(img_gray, 237, 255, cv.THRESH_BINARY)  # 237 without residential buildings 237
    residentiel = thresh1 - thresh2  # residential buildings in white

    ret, thresh3 = cv.threshold(img_gray, 247, 255, cv.THRESH_BINARY)  # with commercial buildings
    ret, thresh4 = cv.threshold(img_gray, 248, 255, cv.THRESH_BINARY)  # without commercial buildings
    commercial = thresh3 - thresh4  # commercial buildings in white
    #  TODO 3D cause nouveaux problèmes
    ret, thresh5 = cv.threshold(img_gray, 238, 255, cv.THRESH_BINARY)  # with 3D buildings 239
    ret, thresh6 = cv.threshold(img_gray, 240, 255, cv.THRESH_BINARY)  # without 3D buildings 240
    building_3d = thresh5 - thresh6  # 3D buildings in white

    #  Erase white lines
    minThick = 15  # Define minimum thickness
    se = cv.getStructuringElement(cv.MORPH_ELLIPSE, (minThick, minThick))  # define a disk element
    img_bat = 255 * cv.morphologyEx(residentiel.astype('uint8'), cv.MORPH_OPEN, se)
    img_bat += 255 * cv.morphologyEx(commercial.astype('uint8'), cv.MORPH_OPEN, se)
    img_bat += 255 * cv.morphologyEx(building_3d.astype('uint8'), cv.MORPH_OPEN, se)
    return img_bat


def tracer_contour(img_bat, img_google):
    """
    Show contours of detected buildings on the screenshot. (not needed, development tool just to have a visual)
    :param img_bat: (grayscale image) Image of buildings
    :param img_google: (RBG image) Screenshot image
    """
    im2, contours, hierarchy = cv.findContours(img_bat, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # approx = []
    # for c in contours:
    #     epsilon = 0.01 * cv.arcLength(c, True)
    #     approx.append(cv.approxPolyDP(c, epsilon, True))
    # Tracer les contours
    cv.drawContours(img_google, contours, -1, (0, 255, 0), 3)
    # Tracer individuellement
    # cnt = contours[245]
    # cv.drawContours(img_originale, [cnt], 0, (0, 255, 0), 3)

    cv.imshow('Image Google', img_google)
    cv.waitKey(0)
    cv.destroyAllWindows()


def image2features(img_bat, features, lat, lon):
    """
    Create a list of features
    :param img_bat: (grayscale image) Image of buildings
    :param features: (list) List of Polygon objects
    :param lat: (float) Latitude of the screenshot URL
    :param lon: (float) Longitude of the screenshot URL
    """
    #  create contours
    im2, contours, hierarchy = cv.findContours(img_bat, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # create array of points
    polygones = [[] for _ in contours]
    points = []
    list_coord_poly = []
    for i in range(len(contours)):
        for j in range(len(contours[i])):
            var = np.array(contours[i][j]).tolist()
            points.append(var[0])
        polygones[i].append(points[:])
        points = []
        list_coord_poly.append(polygones[i][0])

    # project points from geographic coordinates(Google Maps) to WGS_1984_Web_Mercator_Auxiliary_Sphere EPSG:3857
    list_coord_poly = inv_y(list_coord_poly, img_bat)
    list_coord_poly = scale(list_coord_poly)
    list_coord_poly = translation(list_coord_poly, lat, lon)

    # list of Polygon objects
    # features = []
    for polygone in list_coord_poly:
        # Create a Polygon object based on the array of points
        # Append to the list of Polygon objects
        features.append(
            arcpy.Polygon(
                arcpy.Array([arcpy.Point(*coords) for coords in polygone])))


def shapefile_creator(features, n, wkid):
    """
    Create a shapefile with a list of Polygon objects, aggregate overlaping buildings and project
    :param n: (int) number of shapefiles to create
    :param features: (list) List of Polygon objects
    :param wkid: (int) MTM zone wkid
    :return (string) path of shapefile
    """
    arcpy.env.overwriteOutput = True
    building_footprint_1 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_1_{}.shp".format(n)
    building_footprint_2 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_2_{}.shp".format(n)
    building_footprint_z21 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_z21_{}.shp".format(n)  # final shapefile
    arcpy.CopyFeatures_management(features, building_footprint_1)

    #  project
    sr = arcpy.SpatialReference(3857)  # WGS_1984_Web_Mercator_Auxiliary_Sphere
    arcpy.DefineProjection_management(building_footprint_1, sr)  # Define Projection
    sr2 = arcpy.SpatialReference(wkid)
    arcpy.Project_management(building_footprint_1, building_footprint_2, sr2)  # Project
    arcpy.Delete_management(building_footprint_1)

    #  Dissolve overlaping buildings
    arcpy.Dissolve_management(building_footprint_2, building_footprint_z21, multi_part="SINGLE_PART")
    #ca.AggregatePolygons(building_footprint_2, building_footprint_z21, 0.01, 3, 3, "ORTHOGONAL", "")

    arcpy.Delete_management(building_footprint_2)
    return building_footprint_z21


def inv_y(coord, img):
    """
    Invert Y coordonates of image
    :param coord: (list) List of Polygon points image coordinates
    :param img: (numpy.ndarray) image
    :return coord: (list) List of Polygon points coordinates
    """
    height, width = img.shape[:2]  # take height of image
    yc = np.int(height) / 2
    for i in range(len(coord)):
        for j in range(len(coord[i])):
            coord[i][j][1] = 2 * yc - coord[i][j][1]  # invert Y coordinates of image
    return coord


def scale(coord):
    """
    Scale the Polygons coordinates.  Adjust X and Y scale depending on the zoom of the images.
    :param coord: (list) List of Polygon points coordinates
    :return coord: (list) List of Polygon points scaled coordinates
    """
    y_scale = 0.07465  # Y scale (for 21zoom use 0.07465)
    x_scale = 0.07465  # X scale (for 21zoom use 0.07465)
    for i in range(len(coord)):
        for j in range(len(coord[i])):
            coord[i][j][1] = coord[i][j][1] * y_scale
            coord[i][j][0] = coord[i][j][0] * x_scale
    return coord


def translation(coord, lat, lon):
    """
    Translate the Polygons coordinates.
    :param coord: (list) List of Polygon points coordinates
    :param lat: (float) Latitude of the screenshot URL
    :param lon: (float) Longitude of the screenshot URL
    :return coord: (list) List of Polygon points translated coordinates
    """
    ty = merc_y(lat) - 73.43  # Y translation
    tx = merc_x(lon) - 57.55  # X translation
    for i in range(len(coord)):
        for j in range(len(coord[i])):
            coord[i][j][1] = coord[i][j][1] + ty
            coord[i][j][0] = coord[i][j][0] + tx
    return coord


def merc_x(lon):
    """
    Transform longitude to X coordinate in Mercator (sphere)
    :param lon: (float) Longitude
    :return x: (float) X coordinate in Mercator (sphere)
    """
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    return x


def merc_y(lat):
    """
    Transform longitude to X coordinate in Mercator (sphere)
    :param lat: (float) Latitude
    :return y: (float) Y coordinate in Mercator (sphere)
    """
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5
    r_major = 6378137.0
    r_minor = 6378137.0  # 6356752.3142 if ellipse
    temp = r_minor / r_major
    eccent = math.sqrt(1 - temp ** 2)
    phi = math.radians(lat)
    sinphi = math.sin(phi)
    con = eccent * sinphi
    com = eccent / 2
    con = ((1.0 - con) / (1.0 + con)) ** com
    ts = math.tan((math.pi / 2 - phi) / 2) / con
    y = 0 - r_major * math.log(ts)
    return y


def RemovePolygonHoles_management(in_fc, threshold=0.0):
    """
    Removes holes from a polygon feature class.
    If threshold is given, only the holes smaller than the threshold will be removed.
    If no threshold is given, it removes all holes.
    :param in_fc: is a polygon feature class.
    :param threshold: is numeric.
    """
    desc = arcpy.Describe(in_fc)
    if desc.dataType != "FeatureClass" and desc.dataType != "ShapeFile":
        print("Invalid data type. The input is supposed to be a Polygon FeatureClass or Shapefile.")
        return
    else:
        if desc.shapeType != "Polygon":
            print("The input is supposed to be a Polygon FeatureClass or Shapefile.")
            return
    if threshold < 0.0:
        threshold = 0.0
    with arcpy.da.UpdateCursor(in_fc, ["SHAPE@"]) as updateCursor:
        for updateRow in updateCursor:
            shape = updateRow[0]
            new_shape = arcpy.Array()
            for part in shape:
                new_part = arcpy.Array()
                if threshold > 0:
                    # find None point in shape part
                    # in arcpy module, a None point is used to seperate exterior and interior vertices
                    null_point_index = []
                    for i in range(len(part)):
                        if part[i] is None:
                            null_point_index.append(i)
                    # if interior vertices exist, create polygons and compare polygon shape area to given threshold
                    # if larger, keep vertices, else, dismiss them
                    if len(null_point_index) > 0:
                        for k in range(0, null_point_index[0]):
                            new_part.add(part[k])
                        for i in range(len(null_point_index)):
                            pointArray = arcpy.Array()
                            # determine if the None point is the last one
                            if i+1 < len(null_point_index):
                                for j in range(null_point_index[i] + 1, null_point_index[i+1]):
                                    pointArray.add(part[j])
                            else:
                                for j in range(null_point_index[i] + 1, len(part)):
                                    pointArray.add(part[j])
                            # create a polygon to check shape area against the given threshold
                            inner_poly = arcpy.Polygon(pointArray)
                            # if larger than threshold, then add to the new part Array
                            if inner_poly.area > threshold:
                                if i+1 < len(null_point_index):
                                    for k in range(null_point_index[i], null_point_index[i+1]):
                                        new_part.add(part[k])
                                else:
                                    for k in range(null_point_index[i], len(part)):
                                        new_part.add(part[k])
                        new_shape.add(new_part)
                    # if interior does not exist, add the whole part
                    else:
                        new_shape.add(part)
                else:
                    # get the first None point index
                    first_null_point_index = 0
                    for i in range(len(part)):
                        if part[i] is None:
                            first_null_point_index = i
                            break
                    if first_null_point_index == 0:
                        new_shape.add(part)
                    else:
                        for j in range(first_null_point_index):
                            new_part.add(part[j])
                        new_shape.add(new_part)
            if len(new_shape) > 0:
                new_poly = arcpy.Polygon(new_shape)
                updateRow[0] = new_poly
                updateCursor.updateRow(updateRow)