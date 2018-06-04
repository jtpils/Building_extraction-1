# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
import arcpy
import arcpy.cartography as ca
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# CREATE BOUNDING BOX HERE (starting south-west corner; ending north-east corner):
# Secteur de test (SJSR)
# CONST_lat_s = 45.282014  # starting latitude
# CONST_lon_s = -73.260003  # starting longitude
# CONST_lat_e = 45.288672  # ending latitude
# CONST_lon_e = -73.248399  # ending longitude

# Secteur avec autoroute (SJSR)
# CONST_lat_s = 45.301452  # starting latitude
# CONST_lon_s = -73.269366  # starting longitude
# CONST_lat_e = 45.304274  # ending latitude
# CONST_lon_e = -73.262891  # ending longitude

# Secteur de test zoom x21 (SJSR)
CONST_lat_s = 45.306074  # starting latitude
CONST_lon_s = -73.260668  # starting longitude
CONST_lat_e = 45.309966  # ending latitude
CONST_lon_e = -73.254757  # ending longitude

# Bassin versant de la rivière Richelieu
# CONST_lat_s = 44.987612  # starting latitude
# CONST_lon_s = -73.632196  # starting longitude
# CONST_lat_e = 46.085388  # ending latitude
# CONST_lon_e = -72.997301  # ending longitude

# Secteur St-Jean   15 500 photos
# CONST_lat_s = 45.266021  # starting latitude
# CONST_lon_s = -73.467910  # starting longitude
# CONST_lat_e = 45.653953  # ending latitude
# CONST_lon_e = -73.025775  # ending longitude

# Centre ville SJSR multiprocess test
# CONST_lat_s = 45.291382  # starting latitude
# CONST_lon_s = -73.271735  # starting longitude
# CONST_lat_e = 45.309895  # ending latitude       45.297242  2 process       45.309895  6 process
# CONST_lon_e = -73.248687  # ending longitude    -73.260324                 -73.248687

CONST_dlat = 0.002776  # latitude difference between screenshots (for 21zoom use 0.000273)
CONST_dlon = 0.003995  # longitude difference between screenshots (for 21zoom use 0.001056)


def building_image(img_google):
    """
    Create a binary image with detected buildings
    :param img_google: (RBG image) Screenshot image
    :return img_bat: (grayscale image) Image of buildings
    """
    img_gray = cv.cvtColor(img_google, cv.COLOR_BGR2GRAY)

    ret, thresh1 = cv.threshold(img_gray, 235, 255, cv.THRESH_BINARY)  # with residential buildings 236
    ret, thresh2 = cv.threshold(img_gray, 237, 255, cv.THRESH_BINARY)  # without residential buildings 237
    residentiel = thresh1 - thresh2  # residential buildings in white

    ret, thresh3 = cv.threshold(img_gray, 247, 255, cv.THRESH_BINARY)  # with commercial buildings
    ret, thresh4 = cv.threshold(img_gray, 248, 255, cv.THRESH_BINARY)  # without commercial buildings
    commercial = thresh3 - thresh4  # commercial buildings in white

    #  Erase white lines
    minThick = 5  # Define minimum thickness
    se = cv.getStructuringElement(cv.MORPH_ELLIPSE, (minThick, minThick))  # define a disk element
    img_bat = 255 * cv.morphologyEx(residentiel.astype('uint8'), cv.MORPH_OPEN, se)
    img_bat += 255 * cv.morphologyEx(commercial.astype('uint8'), cv.MORPH_OPEN, se)
    return img_bat


def tracer_contour(img_bat, img_google):
    """
    Show contours of detected buildings on the screenshot. (not needed, development tool just to have a visual)
    :param img_bat: (grayscale image) Image of buildings
    :param img_google: (RBG image) Screenshot image
    """
    im2, contours, hierarchy = cv.findContours(img_bat, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

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


def shapefile_creator(features):
    """
    Create a shapefile with a list of Polygon objects, aggregate overlaping buildings and project
    :param features: (list) List of Polygon objects
    """
    building_footprint_1 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_1.shp"
    building_footprint_2 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_2.shp"
    building_footprint_z21 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_z21.shp"  # final shapefile

    arcpy.CopyFeatures_management(features, building_footprint_1)

    #  Aggregate overlaping buildings
    #  AggregatePolygons(in_features, out_feature_class, aggregation_distance, {minimum_area}, {minimum_hole_size}, {orthogonality_option}, {barrier_features}, {out_table})
    ca.AggregatePolygons(building_footprint_1, building_footprint_2, 0.01, 2, 2, "ORTHOGONAL", "")
    arcpy.Delete_management(building_footprint_1)

    #  project
    sr = arcpy.SpatialReference(3857)  # WGS_1984_Web_Mercator_Auxiliary_Sphere
    arcpy.DefineProjection_management(building_footprint_2, sr)  # Define Projection
    sr2 = arcpy.SpatialReference(2950)  # NAD_1983_CSRS_MTM_8
    arcpy.Project_management(building_footprint_2, building_footprint_z21, sr2)  # Project
    arcpy.Delete_management(building_footprint_2)


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
    ty = merc_y(lat) - 222.72  # Y translation  39.86 no headless mode: 34.50
    tx = merc_x(lon) - 222.47  # X translation  61.80 no headless mode: 61.25
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
    r_minor = 6378137.0  # 6356752.3142
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


def main():
    """
    Main function. Takes all the screenshots necessary to cover the bounding box and creates the shapefile of building footprints
    """
    print("Taking screenshots...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome("E:/Charles_Tousignant/Python_workspace/Gari/chromedriver", chrome_options=options)
    #driver = webdriver.PhantomJS("C:/Users/bruntoca/AppData/Roaming/npm/node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs")
    driver.set_window_size(6000, 6000)  # 1696, 1096

    lat = CONST_lat_s
    counter_screenshots = 0  # for counting number of screenshots
    feat = []
    while lat < CONST_lat_e:
        lon = CONST_lon_s
        while lon < CONST_lon_e:
            url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon)
            driver.get(url)
            # screenshot_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot{}.png".format(counter_screenshots + 1)
            screenshot_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot.png"
            driver.save_screenshot(screenshot_path)
            image_google = cv.imread(screenshot_path)
            image_bat = building_image(image_google)
            print("Detecting and extracting building footprints from screenshot #{}...".format(counter_screenshots + 1))
            image2features(image_bat, feat, lat, lon)
            lon += CONST_dlon
            counter_screenshots += 1
        lat += CONST_dlat
    driver.quit()
    print("Creating shapefile...")
    shapefile_creator(feat)
    print("Building footprints were extracted from {} screenshots".format(counter_screenshots))
    print("Building footprints extraction complete!")


if __name__ == "__main__":
    start_time = time.time()

    main()

    end_time = time.time()
    print("{} minutes to complete".format((end_time - start_time) / 60))

