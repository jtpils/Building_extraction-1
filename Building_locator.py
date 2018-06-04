# -*- coding: utf-8 -*-
import sys
import time
import arcpy
import cv2 as cv
import geocoder
from selenium import webdriver
from Building_extractor_MP import merc_x, merc_y, building_image, image2features
from selenium.webdriver.chrome.options import Options


def address2latlon(addr):
    """
    Return the coordinates of the corresponding address
    :param addr: (string) address
    :return (list) list of coordinates (float) [lat, lon]
    """
    g = geocoder.google(addr)
    gjson = g.json
    timeout = time.time() + 7
    while gjson is None:  # Redo until we have a response
        g = geocoder.google(addr)
        gjson = g.json
        if time.time() > timeout:  # if google can't find the address after a certain amount of time
            sys.exit("Google ne trouve pas cette adresse, veuillez réessayer")
    return g.latlng


def localize_point(lat, lon):
    """
    Return a Point feature at the corresponding lat/lon
    :param lat: (float) Latitude of the address
    :param lon: (float) Longitude of the address
    :return (PointGeometry) Point
    """
    return arcpy.PointGeometry(arcpy.Point(merc_x(lon), merc_y(lat)))


def main():
    """
    Main function. Create a shapefile of the building footprint for the address entered by the user.
    """
    address = raw_input(
        "Entrez l'adresse du bâtiment à extraire (par exemple: 165 rue de Liège, St-jean-sur-Richelieu, Québec)")
    coord = address2latlon(address)
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
    driver = webdriver.Chrome("E:/Charles_Tousignant/Python_workspace/Gari/chromedriver", chrome_options=options)
    driver.set_window_size(2000, 2000)
    feat = []
    url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon)
    driver.get(url)
    screenshot_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/localize_building.png"
    driver.save_screenshot(screenshot_path)

    print("Detecting and extracting building footprints from screenshot...")
    image_google = cv.imread(screenshot_path)
    image_bat = building_image(image_google)
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
    localized_building = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building_0.shp"
    localized_building_proj = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/localized_building.shp"
    if arcpy.Exists(localized_building_proj):  # delete shapefile if it already exists
        arcpy.Delete_management(localized_building_proj)
    arcpy.CopyFeatures_management(feat[index], localized_building)
    sr = arcpy.SpatialReference(3857)  # WGS_1984_Web_Mercator_Auxiliary_Sphere
    arcpy.DefineProjection_management(localized_building, sr)  # Define Projection
    sr2 = arcpy.SpatialReference(2950)  # NAD_1983_CSRS_MTM_8
    arcpy.Project_management(localized_building, localized_building_proj, sr2)  # Project
    arcpy.Delete_management(localized_building)
    print("Building footprint extraction complete!")


if __name__ == "__main__":
    main()
    # a = '165 rue de Liege, St-jean-sur-Richelieu, Quebec'  # point pas dans le polygone
    # b = "116 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point dans le polygone
    # c = "107 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point pas dans le polygone
