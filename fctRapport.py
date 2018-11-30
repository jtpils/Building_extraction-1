# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Enundation.py
# Created on: 2018-09-14
# Author : Charles Tousignant
# Project : Enundation
# Description : backend of Enundation website
# ---------------------------------------------------------------------------
from rasterstats import zonal_stats
from shapely.geometry import shape, Point
import fiona
import json
import sys
import geocoder
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2 as cv
import numpy as np
from pyproj import Proj, transform
import arcpy
import math


def address2latlon(addr):
    """
    Return the coordinates of the corresponding address
    :param addr: (string) address
    :return (list) list of coordinates (float) [lat, lon]
    """
    key = "AjBnbJXTfnqbk1fgDACBIfrnhHs6SMQGGi6XGzaqCw2lyQ_RjtnCSQaCGrFlXS_L"
    g = geocoder.bing(addr, key=key)
    # g = geocoder.google(addr)
    gjson = g.json
    timeout = time.time() + 7
    while gjson is None:  # Redo until we have a response
        g = geocoder.bing(addr, key=key)
        # g = geocoder.google(addr)
        gjson = g.json
        if time.time() > timeout:  # if google can't find the address after a certain amount of time
            sys.exit("Google ne trouve pas cette adresse, veuillez réessayer")
    return g.latlng


def building_locator(adr, output_dir):
    """
    Main function. Create a shapefile of the building footprint for the address entered by the user.
    """
    # cwd = os.getcwd()
    # chromedriver_path = cwd + "\chromedriver"
    chromedriver_path = "Z:\GARI - Versions\V1.7.4\scripts\chromedriver"
    screenshot_path = output_dir + "\localize_building.png"
    localisation_path = output_dir + "\carte_loc.png"
    localisation_path2 = output_dir + "\carte_localisation.png"
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
    driver = webdriver.Chrome(chromedriver_path, chrome_options=options)
    driver.set_window_size(2000, 2000)
    feat = []
    url = "https://www.google.ca/maps/@%f,%f,21z?hl=en-US" % (lat, lon)
    driver.get(url)
    driver.save_screenshot(screenshot_path)

    driver.set_window_size(1400, 1400)
    url_loc = "https://www.google.ca/maps/@%f,%f,226m/data=!3m1!1e3" % (lat, lon)
    driver.get(url_loc)
    time.sleep(5)
    driver.save_screenshot(localisation_path)
    img = cv.imread(localisation_path, cv.IMREAD_COLOR)
    crop_img = img[400:1000, 400:1000]
    cv.circle(crop_img, (300, 300), 70, (0, 0, 255), 3)
    cv.imwrite(localisation_path2, crop_img)

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
    localized_building = output_dir + "\localized_building_0.shp"
    localized_building_proj = output_dir + "\localized_building.shp"
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
    os.remove(localisation_path)
    print("Building footprint extraction complete!")
    return localized_building_proj


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


def localize_point(lat, lon):
    """
    Return a Point feature at the corresponding lat/lon
    :param lat: (float) Latitude of the address
    :param lon: (float) Longitude of the address
    :return (PointGeometry) Point
    """
    return arcpy.PointGeometry(arcpy.Point(merc_x(lon), merc_y(lat)))


def inv_y(coord, img):
    """
    Invert Y coordonates of image
    :param coord: (list) List of Polygon points image coordinates
    :param img: (numpy.ndarray) image
    :return coord: (list) List of Polygon points coordinates
    """
    height, width = img.shape[:2]  # take height of image
    yc = np.int(height)
    for i in range(len(coord)):
        for j in range(len(coord[i])):
            coord[i][j][1] = yc - coord[i][j][1]  # invert Y coordinates of image
    return coord


def scale(coord):
    """
    Scale the Polygons coordinates.  Adjust scale depending on the zoom of the images.
    :param coord: (list) List of Polygon points coordinates
    :return coord: (list) List of Polygon points scaled coordinates
    """
    scl = 0.07465  # scale (for 21zoom use 0.07465)
    for i in range(len(coord)):
        for j in range(len(coord[i])):
            coord[i][j][0], coord[i][j][1] = coord[i][j][0] * scl, coord[i][j][1] * scl
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
            coord[i][j][0], coord[i][j][1] = coord[i][j][0] + tx, coord[i][j][1] + ty
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


def proj(x, y, inP, outP):
    epsg_in = 'epsg:' + str(inP)
    epsg_out = 'epsg:' + str(outP)
    inProj = Proj(init=epsg_in)
    outProj = Proj(init=epsg_out)
    xp, yp = transform(inProj, outProj, x, y)
    return xp, yp


def volumeTrapeze(h, sommet, base, profondeur):
    return (sommet + base) / 2 * h * profondeur


def baseTrapeze(h, angle, sommet):
    return math.tan(math.radians(angle)) * h * 2 + sommet


def digue(in_lines, in_raster):
    """
    Calculate quantities of sand and bags required for dike construction
    :param in_lines: (string) path of lines shapefile
    :param in_raster: (string) path of water height raster
    """
    # Parametre de configuration de la digue
    sommet = 0.61  # Largeur du sommet (must be at least 2' wide across the top of the dike)
    angle = 45  # angle des cotes
    freeboard = 0.61  # area of the dike between the highest floodwater level and the top of the dike (2')
    compaction = 1.05  # 5% of the required height of the dike to account for compaction due to wetting
    volumeSac = 0.02  # 32kg de sable  (20 litres)
    arcpy.env.workspace = arcpy.Describe(in_lines).path
    arcpy.env.overwriteOutput = True

    # Conversion du raster en polygone
    arcpy.CheckOutExtension('Spatial')
    rasBool = arcpy.sa.Int(arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, 1))
    filteredRaster = arcpy.sa.SetNull(rasBool, rasBool, "VALUE = 0")
    outPolygon = "zi_polygon.shp"
    arcpy.RasterToPolygon_conversion(filteredRaster, outPolygon, 'NO_SIMPLIFY')

    # Clip des lignes par le polygone
    outClip = "clip_lines.shp"
    arcpy.Clip_analysis(in_lines, outPolygon, outClip)

    # Multipart to single part + densify
    outMulti = "multi_lines.shp"
    arcpy.MultipartToSinglepart_management(outClip, outMulti)
    arcpy.Densify_edit(outMulti, 'DISTANCE', 0.2)
    allPts = "allPts.shp"
    arcpy.FeatureVerticesToPoints_management(outMulti, allPts, 'All')

    # Extractition des valeurs sur le raster pour chaque point
    allPtsZ = "allPtsZ.shp"
    arcpy.sa.ExtractValuesToPoints(allPts, in_raster, allPtsZ, 'INTERPOLATE')

    arcpy.AddField_management(outMulti, 'Volume', 'FLOAT')
    arcpy.AddField_management(outMulti, 'Nb_Sacs', 'INTEGER')
    arcpy.AddField_management(outMulti, 'Comments', 'TEXT')
    vol_sable, nb_sacs = 0, 0
    with arcpy.da.UpdateCursor(outMulti, ['SHAPE@', 'RIGHT_FID', 'Volume', 'Nb_Sacs', 'Comments']) as ucursor:
        for urow in ucursor:
            volumeTotal = 0
            with arcpy.da.SearchCursor(allPtsZ, ['RASTERVALU'], """"RIGHT_FID" = {0}""".format(urow[1])) as scursor:
                allDepth = []
                for srow in scursor:
                    allDepth.append(srow[0])
                for d in allDepth:
                    if d == -9999:
                        base = baseTrapeze(freeboard, angle, sommet)
                        volumeTotal += volumeTrapeze(freeboard * compaction, sommet, base, 0.2)
                    else:
                        base = baseTrapeze(d + freeboard, angle, sommet)
                        volumeTotal += volumeTrapeze((d + freeboard) * compaction, sommet, base, 0.2)

                urow[2] = volumeTotal
                urow[3] = volumeTotal / volumeSac
                vol_sable = volumeTotal
                nb_sacs = volumeTotal / volumeSac
            ucursor.updateRow(urow)

    outDigues = "out_digues.shp"
    arcpy.Dissolve_management(outMulti, outDigues, ['RIGHT_FID', 'Volume', 'Nb_Sacs'])

    arcpy.Delete_management(outPolygon)
    arcpy.Delete_management(outClip)
    arcpy.Delete_management(outMulti)
    arcpy.Delete_management(allPts)
    arcpy.Delete_management(allPtsZ)
    arcpy.Delete_management("lines.shp")
    return vol_sable, nb_sacs


def create_convex_hull(in_fc, grouping_field=None):
    """
    Generate convex hull features optionally grouping input features;
    if no grouping_field specified, a single Convex Hull will be generated
    for all input features. Used for grouped buildings.
    :param in_fc: (string) path of building shapefile
    :param grouping_field: (string) name of the grouping field if needed
    """

    tmp_dis = arcpy.Dissolve_management(in_features=in_fc,
                                        out_feature_class=r"in_memory\tempOutput",
                                        dissolve_field=grouping_field,
                                        multi_part=True)

    feats = [f[0].convexHull() for f in arcpy.da.SearchCursor(tmp_dis, "SHAPE@")]

    arcpy.env.workspace = arcpy.Describe(in_fc).path
    fc_type = arcpy.Describe(in_fc).baseName
    out_fc_name = "ConvexHull{0}".format(fc_type)
    if arcpy.Exists(out_fc_name):
        arcpy.Delete_management(out_fc_name)
    arcpy.CopyFeatures_management(feats, out_fc_name)


def line_creator(in_bat):
    """
    Create lines around selected buildings
    :param in_bat: (string) path of buildings shapefile
    """
    print("Creating lines...")
    arcpy.env.workspace = arcpy.Describe(in_bat).path
    arcpy.env.overwriteOutput = True
    dissolve_buf = "dissolve_buf.shp"
    CHdissolve_buf = "ConvexHulldissolve_buf.shp"

    tmp_buf = arcpy.Buffer_analysis(in_features=in_bat,
                                    out_feature_class=r"in_memory\tempOutput",
                                    buffer_distance_or_field="8 FEET",
                                    line_side="OUTSIDE_ONLY",
                                    line_end_type="ROUND",
                                    dissolve_option="NONE")

    tmp_dis = arcpy.Dissolve_management(in_features=tmp_buf,
                                        out_feature_class=r"in_memory\tempOutput1",
                                        multi_part=True)

    tmp_single = arcpy.MultipartToSinglepart_management(in_features=tmp_dis,
                                                        out_feature_class=dissolve_buf)

    tmp_field = arcpy.AddField_management(in_table=tmp_single,
                                          field_name="group",
                                          field_type="SHORT")

    with arcpy.da.UpdateCursor(tmp_field, "group") as cursor:
        i = 0
        for row in cursor:
            row[0] = i
            cursor.updateRow(row)
            i += 1

    create_convex_hull(tmp_field, grouping_field="group")
    arcpy.PolygonToLine_management(in_features=CHdissolve_buf,
                                   out_feature_class="lines")

    arcpy.Delete_management(dissolve_buf)
    arcpy.Delete_management(CHdissolve_buf)
    lines_shp = arcpy.env.workspace + "/lines.shp"
    return lines_shp


def sacs_sable(bat_shp, heau_tif):
    lines_shp = line_creator(bat_shp)
    vol_sable, nb_sacs = digue(lines_shp, heau_tif)

    arcpy.Delete_management(lines_shp)
    return vol_sable, nb_sacs


def get_risk(bat_shp, recurrence_tif):
    zs_min = 999
    risk_lvl = "faible"
    for batiment in fiona.open(bat_shp):
        poly = shape(batiment['geometry'])
        zs = zonal_stats(poly, recurrence_tif)
        zs_min = zs[0]['min']
        if zs_min <= 2.0:
            risk_lvl = "tres eleve"
        if 2.0 < zs_min <= 20.0:
            risk_lvl = "eleve"
        if 20.0 < zs_min <= 100.0:
            risk_lvl = "moyen"
    return zs_min, risk_lvl


def get_hauteur_eau(bat_shp, heau_tif):
    zs_max = 0
    for batiment in fiona.open(bat_shp):
        poly = shape(batiment['geometry'])
        zs = zonal_stats(poly, heau_tif)
        zs_max = zs[0]['max']
    return zs_max


def get_report(no_civ, rue, ville, province, in_recurrence, in_heau, in_riviere, in_dom_moy, in_heau_rec100,
               output_dir):
    recurrence_path = in_recurrence
    heau_path = in_heau
    riviere_path = in_riviere
    dom_moy_annuel_path = in_dom_moy
    heau_rec100_path = in_heau_rec100

    full_add = no_civ + " " + rue + ", " + ville + ", " + province
    bat_path = building_locator(full_add, output_dir)
    lat, lon = address2latlon(full_add)
    val_rec_exacte, risk_lvl = get_risk(bat_path, recurrence_path)  # valeur de récurrence et niveau de risque
    heau_rec100 = get_hauteur_eau(bat_path, heau_rec100_path)
    vol_sable, nb_sacs = sacs_sable(bat_path, heau_path)  # volume de sable et nombre de sacs requis
    bat_shp = fiona.open(bat_path)
    bat = shape(next(bat_shp)['geometry'])
    dist_riv = []
    riviere_shp = fiona.open(riviere_path)
    rivieres = iter(riviere_shp)
    for _ in range(len(riviere_shp)):
        riviere = shape(next(rivieres)['geometry'])
        dist_riv.append(bat.distance(riviere))
    riviere_shp.close()
    min_dist = min(dist_riv)  # distance entre le bâtiment et la rivière

    xp, yp = proj(merc_x(lon), merc_y(lat), 3857, 2950)  # WGS_1984_Web_Mercator_Auxiliary_Sphere to NAD_1983_CSRS_MTM_8
    pt = Point(xp, yp)
    dist_bat = []
    bat_dom_shp = fiona.open(dom_moy_annuel_path)
    bat_dom = iter(bat_dom_shp)
    for _ in range(len(bat_dom_shp)):
        bat_ = shape(next(bat_dom)['geometry'])
        dist_bat.append(bat_.distance(pt))
    bat_dom_shp.close()
    ind = dist_bat.index(min(dist_bat))
    dom_val = [[d.Risque_an, d.Valeur_bat] for d in arcpy.SearchCursor(dataset=dom_moy_annuel_path)]
    dom_val = dom_val[ind]  # dommages moyen annuel / valeur $
    dom_moy_annuel = dom_val[0]  # dommages moyen annuel $
    valeur = dom_val[1]  # valeur $
    pourcentage_val = dom_val[0] / dom_val[1]  # % de dommages

    data = {'Adresse': full_add, 'Dist_riviere': "%.0f" % min_dist, 'Recurrence': "%.1f" % val_rec_exacte,
            'Niv_risque': risk_lvl, 'hauteur_eau_recurrence_100ans': "%.2f" % heau_rec100,
            'Val_batiment': "%.0f" % valeur, 'Dom_moy_annuel': "%.0f" % dom_moy_annuel,
            'Pourcent_val': "%.2f" % (pourcentage_val * 100), 'Vol_sable': "%.1f" % vol_sable,
            'Nb_sacs': "%.0f" % nb_sacs}

    json_data = json.dumps(data)
    with open(output_dir + "\data.json", 'w') as outfile:
        json.dump(json_data, outfile)

    print
    print("Adresse: {}".format(full_add))
    print("Latitude: {}° ; Longitude: {}°".format(lat, lon))
    print("Le bâtiment se trouve à {:.0f}m de la rivière".format(min_dist))
    print("La valeur exacte de récurrence est de {:.1f} ans".format(val_rec_exacte))
    print("Le niveau de risque est {}".format(risk_lvl))
    print("La hauteur d'eau (récurrence 100 ans): {:.2f} m".format(heau_rec100))
    print("La valeur du bâtiment est de {:.0f}$".format(valeur))
    print("Le dommage annuel moyen est de {:.0f}$ et correspond à {:.2f}% de la valeur total du bâtiment.\n".format(
        dom_moy_annuel, pourcentage_val * 100))
    print("Selon la hauteur d'eau maximale prévue:")
    print("Le volume de sable requis pour construire la digue est de {:.1f} m3".format(vol_sable))
    print("Le nombre de sacs de sable requis pour construire la digue est de {:.0f}".format(nb_sacs))


def main():
    no_civ = arcpy.GetParameterAsText(0)
    rue = arcpy.GetParameterAsText(1)
    ville = arcpy.GetParameterAsText(2)
    province = arcpy.GetParameterAsText(3)
    in_recurrence = arcpy.GetParameterAsText(4)
    in_heau = arcpy.GetParameterAsText(5)
    in_riviere = arcpy.GetParameterAsText(6)
    in_dom_moy = arcpy.GetParameterAsText(7)
    in_heau_rec100 = arcpy.GetParameterAsText(8)
    output_dir = arcpy.GetParameterAsText(9)
    get_report(no_civ, rue, ville, province, in_recurrence, in_heau, in_riviere, in_dom_moy, in_heau_rec100, output_dir)


if __name__ == "__main__":
    main()
