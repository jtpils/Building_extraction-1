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
import pandas as pd


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


def train_building_locator(adr, nb):
    cwd = os.getcwd()

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
    driver = webdriver.Chrome(cwd + r"\chromedriver", chrome_options=options)
    driver.set_window_size(2000, 2000)
    feat = []
    url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon)
    driver.get(url)
    screenshot_path = cwd + r"\temp\localize_building.png"
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
        #sys.exit("Aucun bâtiment trouvé à cette adresse")
        return adr
    index = liste_d.index(min(liste_d))

    print("Creating shapefile...")
    localized_building = cwd + r"\temp\localized_building_0.shp"
    localized_building_proj = cwd + r"\temp\localized_building{}.shp".format(nb)
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
    os.remove(screenshot_path)
    print("Building footprint extraction complete!")
    return localized_building_proj


def train_building_extractor(in_xls):
    # """
    # Create a shapefile of training building footprint from excel file
    # """
    arcpy.env.overwriteOutput = True
    cwd = os.getcwd()
    train_xls = pd.ExcelFile(in_xls)
    train_frame = train_xls.parse()
    shape_list = []

    # Create one shapefile per address in Excel file
    for i in range(len(train_frame)):
        adr = str(train_frame.loc[i][2]) + " " + str(train_frame.loc[i][3].encode(encoding='UTF-8')) + ", " + \
              str(train_frame.loc[i][4].encode(encoding='UTF-8')) + ", Quebec"
        shape_list.append(train_building_locator(adr, i))  # Create list of the created shapefile paths

    # Merge buildings into one single shapefile
    arcpy.Merge_management(shape_list, cwd + r"\output\train_buildings.shp")

    add_data(in_xls)

    # Delete temp shapefiles
    for i in range(len(shape_list)):
        arcpy.Delete_management(shape_list[i])


def add_data(inXLS):
    import ogr
    cwd = os.getcwd()
    bat_shp = cwd + r"\output\train_buildings.shp"

    shapeData = ogr.Open(bat_shp, 1)
    layer = shapeData.GetLayer()  # get possible layers.

    new_field = ogr.FieldDefn('Nb_etages', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Pres_ss1', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Type_rdc', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Nb_log', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Classe_bat', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Code_util', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Valeur_ter', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Valeur_bat', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Valeur_imm', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Zrc', ogr.OFTReal)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Zbo', ogr.OFTReal)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('WL', ogr.OFTReal)
    layer.CreateField(new_field)

    info = pd.read_excel(inXLS)

    serie_nb_etage = info['NB_ETAG']
    serie_pres_ss = info['SOUS_SOL']
    serie_type_rdc = info['TYPE_RDC']
    serie_nb_log = info['NB_LOG']
    serie_classe_bat = info['CLASSE_BAT']
    serie_code_util = info['CODE_UTILP']
    serie_val_ter = info['VAL_TER']
    serie_val_bat = info['VAL_BAT']
    serie_val_imm = info['VAL_IMM']
    serie_zrc = info['H_RDC']
    serie_zbo = info['H_BO']
    serie_wl = info['WL']

    for i in range(len(layer)):
        feature = layer.GetFeature(i)

        j = feature.GetFieldIndex("Nb_etages")
        feature.SetField(j, int(serie_nb_etage[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Pres_ss1")
        feature.SetField(j, int(serie_pres_ss[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Type_rdc")
        feature.SetField(j, int(serie_type_rdc[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Nb_log")
        feature.SetField(j, int(serie_nb_log[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Classe_bat")
        feature.SetField(j, int(serie_classe_bat[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Code_util")
        feature.SetField(j, int(serie_code_util[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Valeur_ter")
        feature.SetField(j, int(serie_val_ter[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Valeur_bat")
        feature.SetField(j, int(serie_val_bat[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Valeur_imm")
        feature.SetField(j, int(serie_val_imm[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Zrc")
        feature.SetField(j, float(serie_zrc[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("Zbo")
        feature.SetField(j, float(serie_zbo[i]))
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("WL")
        feature.SetField(j, float(serie_wl[i]))
        layer.SetFeature(feature)


if __name__ == "__main__":
    xls = r"H:\shapefile\hauteur_RDC\train_building\Donnees 1ers planchers part 3.xlsx"
    #train_building_extractor(xls)
    add_data(xls)


    # address = raw_input(
    #     "Entrez l'adresse du bâtiment à extraire (par exemple: 165 rue de Liège, St-jean-sur-Richelieu, Québec)")
    # address = "3500 Avenue Oxford, Montreal"
    # building_locator(address)
    # a = '165 rue de Liege, St-jean-sur-Richelieu, Quebec'  # point pas dans le polygone
    # b = "116 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point dans le polygone
    # c = "107 rue de Liege, St-jean-sur-Richelieu, Quebec"  # point pas dans le polygone
