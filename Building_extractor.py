# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Building_extractor.py
# Created on: 2018-05-22
# Author : Charles Tousignant
# Project : GARI
# Description : Extraction of building footprints from Google Maps
# ---------------------------------------------------------------------------
import multiprocessing
from io import BytesIO
import fiona
import ogr
import osr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shapely.geometry import Point, shape
from utils import *
#import arcpy.cartography as ca

#CONST_dlat = 0.000910  # latitude difference between screenshots (Sud: SJSR, Drummondville, Sherbrooke, etc)
CONST_dlat = 0.000840  # (nord: Chicoutimi)
CONST_dlon = 0.001320  # 0.001280  # longitude difference between screenshots
shapefile_list = []


def final_shapefile(n):
    """
    Create the final shapefile by merging and aggregating all the shapefiles previously created with shapefile_creator()
    :param n: (int) number of shapefiles to merge and aggregate
    """
    global shapefile_list
    shapefile_list = filter(None, shapefile_list)  # remove None values from list
    arcpy.env.overwriteOutput = True
    building_footprint0 = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_del.shp"
    building_footprint = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint.shp"  # final shapefile

    print("Creating final shapefile...                                                             {}".format(elapsed_time()))
    print("Merging all previously created shapefiles...")
    arcpy.Merge_management(shapefile_list, building_footprint0)
    for i in range(n):
        arcpy.Delete_management("E:/Charles_Tousignant/Python_workspace/Gari/shapefile/building_footprint_z21_{}.shp".format(i+1))
    print("Merge complete.                                                                         {}".format(elapsed_time()))

    print("Dissolving polygons...")
    building_footprint = new_shp_name(building_footprint)  # new file name if file already exists
    arcpy.Dissolve_management(building_footprint0, building_footprint, multi_part="SINGLE_PART")
    #ca.AggregatePolygons(building_footprint0, building_footprint, 0.01, 3, 3, "ORTHOGONAL", "")
    print("Dissolve complete.                                                                      {}".format(elapsed_time()))

    print("Removing small polygons...")
    ds = ogr.Open(building_footprint, update=1)
    lyr = ds.GetLayer()
    lyr.ResetReading()
    field_defn = ogr.FieldDefn("Area", ogr.OFTReal)
    lyr.CreateField(field_defn)
    j = 0
    for i in lyr:
        feat = lyr.GetFeature(j)
        geom = i.GetGeometryRef()
        area = geom.GetArea()
        i.SetField("Area", area)
        lyr.SetFeature(i)
        if area < 4.0:  # smaller than
            lyr.DeleteFeature(feat.GetFID())
        j += 1
    print("Small polygons removed.                                                                 {}".format(elapsed_time()))
    arcpy.Delete_management(building_footprint0)
    # RemovePolygonHoles_management(building_footprint)  # bugged (faire après en 2e temps)
    print("Final shapefile complete.                                                               {}".format(elapsed_time()))


def scan(lat, lon_s, lon_e, n, contour_buffer, wkid):
    """
    Scan a region at a given latitude and create a shapefile if building footprints were detected
    :param lat: (float) Latitude
    :param lon_s: (float) starting longitude
    :param lon_e: (float) ending longitude
    :param n: (int) number of the process
    :param contour_buffer: (string) path of contour buffer shapefile
    :param wkid: (int) MTM zone wkid
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
    driver.set_window_size(2418, 2000)

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
            png = driver.get_screenshot_as_png()
            im = Image.open(BytesIO(png))  # uses PIL library to open image in memory
            im = im.crop((418, 0, 2418, 2000))  # get rid of the left panel
            im_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot{}.png".format(counter_screenshots + 1 + n*1000000)
            im.save(im_path)
            image_bat = building_image(im_path)
            print("Process {}: Detecting and extracting building footprints from screenshot #{}...           {}".format(n, counter_screenshots + 1, elapsed_time()))
            image2features(image_bat, feat, lat, lon_s)
            os.remove(im_path)  # delete PNG
            counter_screenshots += 1
        lon_s += CONST_dlon
    driver.quit()

    lenfeat = len(feat)
    if lenfeat != 0:  # create shapefile if at least one building is detected
        print("Process {}: Creating shapefile #{}...                                                     {}".format(n, n, elapsed_time()))
        shapefile_path = shapefile_creator(feat, n, wkid)
        print("Process {}: For shapefile #{}, building footprints were extracted from {} screenshots.     {}".format(n, n, counter_screenshots, elapsed_time()))
        return shapefile_path
    else:
        print("Process {}: No building were detected. No shapefile will be created for this process".format(n))


def start_process(lat_s, lon_s, lat_e, lon_e, shape_path):
    """
    Divide the bounding box in different regions and start one process for each region
    :param lat_s: (float) starting Latitude
    :param lon_s: (float) starting longitude
    :param lat_e: (float) ending latitude
    :param lon_e: (float) ending longitude
    :param shape_path: (string) path of contour shapefile
    :return n: (int) number of total processes
    """
    global shapefile_list
    delta_lat = lat_e - lat_s
    n = int(delta_lat/CONST_dlat) + 1
    print("Multiprocessing building extraction. Task will be split in {} different processes.".format(n))
    arcpy.env.workspace = arcpy.env.scratchGDB
    arcpy.env.overwriteOutput = True
    buffer_ = "buffer"
    buffer_p = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/temp_buffer_proj.shp"
    arcpy.Buffer_analysis(shape_path, buffer_, "200 meters")
    sr = arcpy.SpatialReference(4326)  # WGS84
    arcpy.Project_management(buffer_, buffer_p, sr)  # Project

    # get MTM zone wkid
    zone = fiona.open(shape_path)
    polygon = zone.next()
    zone.close()
    shp_geom = shape(polygon['geometry'])
    centroidX = shp_geom.centroid.x
    wkid = 2950
    if -69 < centroidX < -66:  # NAD_1983_CSRS_MTM_6
        wkid = 2948
    if -72 < centroidX < -69:  # NAD_1983_CSRS_MTM_7
        wkid = 2949
    if -75 < centroidX < -72:  # NAD_1983_CSRS_MTM_8
        wkid = 2950
    if -78 < centroidX < -75:  # NAD_1983_CSRS_MTM_9
        wkid = 2951

    # create a list of the latitude for every row
    lat_list = []
    for i in range(n):
        lat_list.append(lat_s + i*CONST_dlat)

    # use all available cores, otherwise specify the number you want as an argument
    core_number = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(core_number)

    # start processes
    results = [pool.apply_async(scan, args=(lat_list[i], lon_s, lon_e, i+1, buffer_p, wkid)) for i in range(0, n)]
    shapefile_list = [p.get() for p in results]  # list of shapefiles path created during all processes
    pool.close()
    pool.join()
    arcpy.Delete_management(buffer_)
    arcpy.Delete_management(buffer_p)
    return n


def main(shape_path):
    """
    Main function. Scan the shapefile envelope and creates a shapefile containing all the detected building footprints
    :param shape_path: (string) path of contour shapefile
    """
    out_shape_path = shape_path
    # get geometry of shapefile
    shapefile = ogr.Open(shape_path)
    layer = shapefile.GetLayer(0)
    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()

    # project geometry in WGS84
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    source = geom.GetSpatialReference()
    transform = osr.CoordinateTransformation(source, target)
    geom.Transform(transform)

    # get envelope of geometry
    envelope = geom.GetEnvelope()

    # start processes using envelope
    num = start_process(envelope[2]-0.0007, envelope[0]-0.0007, envelope[3]+0.0007, envelope[1]+0.0007, out_shape_path)
    final_shapefile(num)


if __name__ == "__main__":
    # shapefile_bat = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/StHyacinthe_bat.shp"
    # RemovePolygonHoles_management(shapefile_bat)

    shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/hauteur_RDC/Quebec_2017/St_sauveur.shp"
    main(shapefile_contour_path)

    # img= cv.imread(r"C:\Users\bruntoca\Desktop\Capture1.PNG")
    # im = building_image(r"C:\Users\bruntoca\Desktop\Capture1.PNG")
    # print type(img)
    # print type(im)
    # tracer_contour(im, img)

















    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/zone_risque/zone_test_chicout.shp"
    # main(shapefile_contour_path)

    ##################### Autres
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/Drummondville_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/StHyacinthe_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/Sherbrooke_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/Quebec_riv_St_Charles.shp"  # DONE
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/Autres/Saguenay_munic.shp"  # refaire (ligne verticale)
    # main(shapefile_contour_path)


    ##################### SJSR
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/Beloeil_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/Chambly_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/Lacolle_munic.shp"  # DONE OK geocode
    # # main(shapefile_contour_path)
    # # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/Sabrevois_munic.shp"  # DONE OK geocode
    # # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/Sorel_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/StMarc_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/SJSR/SJSR_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)

    ##################### PetiteNation
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/PetiteNation/Duhamel_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/PetiteNation/LacSimon_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/PetiteNation/Papineauville_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/PetiteNation/Plaisance_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)
    # shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Zones_extraction/PetiteNation/StAndre_munic.shp"  # DONE OK geocode
    # main(shapefile_contour_path)


