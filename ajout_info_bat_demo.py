# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ajout_info_bat.py
# Created on: 2019-04-23
# Author : Charles Tousignant
# Project : GARI
# Description : Ajouter de l'information à la couche de bâtiments (Valeur_bat, Nb_etages, Pres_ss1, Zrc) au hasard pour demo
# ---------------------------------------------------------------------------
from utils import *
import geopandas as gpd
import random


def random_values():
    etage = random.randint(1, 2)
    ss = random.randint(0, 1)
    utl = 1000
    valeur = random.randint(150, 1000)*1000

    return etage, ss, utl, valeur


def get_vulnerabilite(in_bat, in_AD):
    bat = gpd.read_file(in_bat)
    AD = gpd.read_file(in_AD)
    crs = bat.crs
    AD = AD.to_crs(crs)
    centroids = bat.centroid
    # print bat.values[0][5]
    polygons = AD.geometry
    ADIDU_liste, Tot_vul_liste = [], []
    for centroid in centroids:
        for i, polygon in enumerate(polygons):
            if polygon.contains(centroid):
                ADIDU_liste.append(str(AD.loc[i, "ADIDU"]))
                #Tot_vul_liste.append(AD.loc[i, "TOT_VUL"])
                Tot_vul_liste.append(AD.loc[i, "Tot_vul"])
    return ADIDU_liste, Tot_vul_liste


def add_data(inMNT, inAD):
    import ogr
    from rasterstats import zonal_stats
    cwd = os.getcwd()
    bat_shp = cwd + r"\output\Batiments.shp"

    shapeData = ogr.Open(bat_shp, 1)
    layer = shapeData.GetLayer()  # get possible layers.
    layer_defn = layer.GetLayerDefn()  # get definitions of the layer

    # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in
    #                range(layer_defn.GetFieldCount())]  # store the field names as a list of strings
    # print len(field_names)  # so there should be just one at the moment called "FID"
    # print field_names  # will show you the current field names

    new_field = ogr.FieldDefn('Nb_etages', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Pres_ss1', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Valeur_bat', ogr.OFTInteger)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Zrc', ogr.OFTReal)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Type_util', ogr.OFTString)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('ADIDU', ogr.OFTString)
    layer.CreateField(new_field)

    new_field = ogr.FieldDefn('Tot_vul', ogr.OFTReal)
    layer.CreateField(new_field)

    # info = pd.read_excel(inXLS)
    #
    # serie_mat = info['Matricule']
    # serie_aire_ss = info['Aire_totale_ss']
    # serie_etage = info['Nb_etages']
    # serie_util = info['Type_util']
    # serie_valeur_bat = info['Valeur_bat']

    zs = zonal_stats(bat_shp, inMNT)
    # print(zs)
    # print(len(zs))
    ADIDU, Tot_vul = get_vulnerabilite(bat_shp, inAD)
    for i in range(len(layer)):
        feature = layer.GetFeature(i)

        nb_etage, pres_ss, util, valeur_bat = random_values()
        j = feature.GetFieldIndex("Nb_etages")
        feature.SetField(j, nb_etage)
        layer.SetFeature(feature)
        j = feature.GetFieldIndex("Pres_ss1")
        feature.SetField(j, pres_ss)
        layer.SetFeature(feature)
        j = feature.GetFieldIndex("Valeur_bat")
        feature.SetField(j, valeur_bat)  # Ajouter les vraies valeurs
        layer.SetFeature(feature)
        if pres_ss == 1:
            j = feature.GetFieldIndex("Zrc")
            feature.SetField(j, zs[i]['max'] + 0.64)  # Méthode selon le MNT développé dans le quartier de test
            layer.SetFeature(feature)
        else:
            j = feature.GetFieldIndex("Zrc")
            feature.SetField(j, zs[i]['max'] + 0.27)
            layer.SetFeature(feature)
        j = feature.GetFieldIndex("Type_util")
        feature.SetField(j, util)
        layer.SetFeature(feature)
        j = feature.GetFieldIndex("ADIDU")
        feature.SetField(j, ADIDU[i])
        layer.SetFeature(feature)
        j = feature.GetFieldIndex("Tot_vul")
        feature.SetField(j, Tot_vul[i])
        layer.SetFeature(feature)


def main():
    clean_scratch_dir()
    cwd = os.getcwd()

    # inAD = r"Z:\Deux_montagnes\AD_avecTaux_Hudson.shp"
    # inMNT = r"Z:\Deux_montagnes\MNT.tif"
    # inBat = r"Z:\Deux_montagnes\DeuxMontagnes_bat_geocode_TEST.shp"
    # inAD = r"Z:\Deux_montagnes\AD_avecTaux_SteMarthe.shp"
    # inMNT = r"Z:\Deux_montagnes\MNT_reproj.tif"
    # inBat = r"Z:\Deux_montagnes\DeuxMontagnes_bat_geocode_Marthe.shp"

    inAD = r"Z:\Outaouais\DuLievre\SHP\AD_avecTaux_DuLievre.shp"
    inMNT = r"Z:\Outaouais\DuLievre\MNT\MNT_DuLievre.tif"
    inBat = r"Z:\Outaouais\DuLievre\SHP\MS_Google_DuLievre_geocode.shp"

    # inAD = r"Z:\Outaouais\PetiteNation\SHP\AD_avecTaux_PetiteNation.shp"
    # inMNT = r"Z:\Outaouais\PetiteNation\MNT\MNT_PetiteNation.tif"
    # inBat = r"Z:\Outaouais\PetiteNation\SHP\MS_Google_PetiteNation_split_geocode.shp"

    outBat = cwd + "\output\Batiments.shp"
    outCen = cwd + "\output\Centroides.shp"

    arcpy.FeatureClassToFeatureClass_conversion(inBat, cwd + "\output", "Batiments")
    arcpy.AddSpatialIndex_management(outBat)
    add_data(inMNT, inAD)
    arcpy.FeatureToPoint_management(outBat, outCen, point_location="INSIDE")
    print("##############################")
    print("L'ajout est complété!")
    print(elapsed_time())
    print("##############################")


if __name__ == "__main__":
    arcpy.env.overwriteOutput = True
    main()
