# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Building_locator.py
# Created on: 2018-05-26
# Author : Charles Tousignant
# Project : GARI
# Description : Extraction building footprint according to the address
# ---------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import *


def localize_point(lat, lon):
    """
    Return a Point feature at the corresponding lat/lon
    :param lat: (float) Latitude of the address
    :param lon: (float) Longitude of the address
    :return (PointGeometry) Point
    """
    return arcpy.PointGeometry(arcpy.Point(merc_x(lon), merc_y(lat)))


def building_locator(adr):
    """
    Main function. Create a shapefile of the building footprint for the address entered by the user.
    """
    coord = address2latlon(adr)
    lat = coord[0]
    lon = coord[1]

    print("Taking screenshot...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(r"C:\Users\bruntoca\Documents\GitHub\Building_extraction\chromedriver", chrome_options=options)
    driver.set_window_size(2000, 2000)
    feat = []
    url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon)
    driver.get(url)
    screenshot_path = r"C:\Users\bruntoca\Documents\GitHub\Building_extraction\temp\localize_building.png"
    driver.save_screenshot(screenshot_path)

    print("Detecting and extracting building footprints from screenshot...")
    image_bat = building_image(screenshot_path)
    image2features(image_bat, feat, lat, lon)
    driver.quit()
    point = localize_point(lat, lon)
    liste_d = []
    for i in range(len(feat)):
        liste_d.append(point.distanceTo(feat[i]))
    if not liste_d:  # verify if list is empty
        sys.exit("Aucun bâtiment trouvé à cette adresse")
    index = liste_d.index(min(liste_d))

    print("Creating shapefile...")
    localized_building = r"C:\Users\bruntoca\Documents\GitHub\Building_extraction\temp\localized_building_0.shp"
    localized_building_proj = r"C:\Users\bruntoca\Documents\GitHub\Building_extraction\temp\localized_building.shp"
    if arcpy.Exists(localized_building_proj):  # delete shapefile if it already exists
        arcpy.Delete_management(localized_building_proj)
    arcpy.CopyFeatures_management(feat[index], localized_building)
    sr = arcpy.SpatialReference(3857)  # WGS_1984_Web_Mercator_Auxiliary_Sphere
    arcpy.DefineProjection_management(localized_building, sr)  # Define Projection
    wkid = 2950
    if -69 < lon < -66:  # NAD_1983_CSRS_MTM_6
        wkid = 2948
    if -72 < lon < -69:  # NAD_1983_CSRS_MTM_7
        wkid = 2949
    if -75 < lon < -72:  # NAD_1983_CSRS_MTM_8
        wkid = 2950
    if -78 < lon < -75:  # NAD_1983_CSRS_MTM_9
        wkid = 2951
    sr2 = arcpy.SpatialReference(wkid)
    arcpy.Project_management(localized_building, localized_building_proj, sr2)  # Project
    arcpy.Delete_management(localized_building)
    print("Building footprint extraction complete!")
    return screenshot_path, localized_building_proj


if __name__ == "__main__":
    # address = raw_input(
    #     "Entrez l'adresse du bâtiment à extraire (par exemple: 165 rue de Liège, St-jean-sur-Richelieu, Québec)")
    address = "3500 Avenue Oxford, Montreal"
    building_locator(address)
    # a = '165 rue de Liege, St-jean-sur-Richelieu, Quebec'  # point pas dans le polygone
    # b = "116 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point dans le polygone
    # c = "107 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point pas dans le polygone
