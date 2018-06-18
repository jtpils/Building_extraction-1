# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Building_extractor_MP.py
# Created on: 2018-05-22
# Author : Charles Tousignant
# Project : GARI
# Description : Extraction des empreintes de bâtiments automatisée sur
# Google Maps (version Multiprocess)
# ---------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import multiprocessing
from Utils_MP import *
from Bounding_box import *
import fiona
from shapely.geometry import Point
from shapely.geometry import shape

CONST_dlat = 0.000882  # latitude difference between screenshots
CONST_dlon = 0.001280  # longitude difference between screenshots
shapefile_list = []


def final_shapefile(n):
    """
    Create the final shapefile by merging and aggregating all the shapefiles previously created with shapefile_creator()
    :param n: (int) number of shapefiles to merge and aggregate
    """
    global shapefile_list
    shapefile_list = filter(None, shapefile_list)  # remove None values from list
    building_footprint0 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint0.shp"
    building_footprint = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint.shp"  # final shapefile

    print("Creating final shapefile...")
    print("Merging all previously created shapefiles...")
    arcpy.Merge_management(shapefile_list, building_footprint0)
    for i in range(n):
        arcpy.Delete_management("E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_z21_{}.shp".format(i+1))
    print("Merging complete.                                                                       {}".format(elapsed_time()))

    print("Aggregating polygons...")
    arcpy.env.overwriteOutput = True
    #  AggregatePolygons(in_features, out_feature_class, aggregation_distance, {minimum_area}, {minimum_hole_size}, {orthogonality_option}, {barrier_features}, {out_table})
    ca.AggregatePolygons(building_footprint0, building_footprint, 0.01, 2, 2, "ORTHOGONAL", "")
    arcpy.Delete_management(building_footprint0)
    print("Final shapefile complete.                                                               {}".format(elapsed_time()))


def scan(lat, lon_s, lon_e, n, contour_buffer):
    """
    Scan a region at a given latitude and create a shapefile if building footprints were detected
    :param lat: (float) Latitude
    :param lon_s: (float) starting longitude
    :param lon_e: (float) ending longitude
    :param n: (int) number of the process
    :param contour_buffer: (string) path of contour buffer shapefile (must be projected in GCS_WGS_1984)
    """
    print("Process {}: Taking screenshots...".format(n))
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome("E:/Charles_Tousignant/Python_workspace/Gari/chromedriver", chrome_options=options)
    driver.set_window_size(2000, 2000)

    counter_screenshots = 0  # for counting number of screenshots
    feat = []

    zone = fiona.open(contour_buffer)
    polygon = zone.next()
    zone.close()
    shp_geom = shape(polygon['geometry'])
    while lon_s < lon_e:
        point = Point(lon_s, lat)
        if point.within(shp_geom):
            url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon_s)
            driver.get(url)
            screenshot_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot{}.png".format(counter_screenshots + 1 + n*1000000) # Pour enregistrer toutes les images
            #screenshot_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot.png"
            driver.save_screenshot(screenshot_path)
            image_google = cv.imread(screenshot_path)
            image_bat = building_image(image_google)
            print("Process {}: Detecting and extracting building footprints from screenshot #{}...           {}".format(n, counter_screenshots + 1, elapsed_time()))
            image2features(image_bat, feat, lat, lon_s)
            counter_screenshots += 1
        lon_s += CONST_dlon
    driver.quit()

    lenfeat = len(feat)
    if lenfeat != 0:  # create shapefile if at least one building is detected
        print("Process {}: Creating shapefile #{}...                                                     {}".format(n, n, elapsed_time()))
        shapefile_name = shapefile_creator(feat, n)
        print("Process {}: For shapefile #{}, building footprints were extracted from {} screenshots.     {}".format(n, n, counter_screenshots, elapsed_time()))
        return shapefile_name
    else:
        print("Process {}: No building were detected. No shapefile will be created for this process".format(n))


def start_process(lat_s, lon_s, lat_e, lon_e, contour):
    """
    Divide the bounding box in different regions and start one process for each region
    :param lat_s: (float) starting Latitude
    :param lon_s: (float) starting longitude
    :param lat_e: (float) ending latitude
    :param lon_e: (float) ending longitude
    :param contour: (string) path of contour shapefile (must be projected in GCS_WGS_1984)
    :return n: (int) number of total processes
    """
    global shapefile_list
    delta_lat = lat_e - lat_s
    n = int(delta_lat/CONST_dlat)
    print("Multiprocessing building extraction. Task will be split in {} different processes.".format(n))

    arcpy.env.workspace = arcpy.Describe(contour).path
    contour_name = arcpy.Describe(contour).baseName
    contour_buffer = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Bassin_versant/{0}_buffer.shp".format(contour_name)

    if not arcpy.Exists(contour_buffer):  # create buffer shapefile if it does not exists
        arcpy.Buffer_analysis(contour, contour_buffer, "100 meters")

    bbox = []
    for i in range(n):
        bbox.append(lat_s + i*CONST_dlat)

    core_number = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(core_number)  # use all available cores, otherwise specify the number you want as an argument
    results = [pool.apply_async(scan, args=(bbox[i], lon_s, lon_e, i+1, contour_buffer)) for i in range(0, n)]
    shapefile_list = [p.get() for p in results]

    pool.close()
    pool.join()
    arcpy.Delete_management(contour_buffer)
    return n


def main(lat_s, lon_s, lat_e, lon_e, contour):
    """
    Main function. Scan the bounding box and creates a shapefile containing all the detected building footprints
    """
    num = start_process(lat_s, lon_s, lat_e, lon_e, contour)
    final_shapefile(num)


if __name__ == "__main__":
    shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Bassin_versant/Bassin_versant_SJSR.shp"  # (must be projected in GCS_WGS_1984)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Bassin_versant/Bassin_versant_PN.shp"  # (must be projected in GCS_WGS_1984)
    main(CONST_lat_s6, CONST_lon_s6, CONST_lat_e6, CONST_lon_e6, shapefile_contour_path)

