# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# aire_diffusion.py
# Created on: 2019-01-29
# Author : Charles Tousignant
# Project : GARI
# Description : Ajouter de l'information à la couche des aires de diffusion
# Fichier requis:
#   -Aires de diffusion : https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-2016-fra.cfm
# ---------------------------------------------------------------------------
from __future__ import division
import urllib2
import pandas as pd
import ogr
from utils import *


def calc_taux(p_annee, p_aire_diffusion):
    url = "https://www12.statcan.gc.ca/census-recensement/{}/dp-pd/prof/details/" \
          "download-telecharger/current-actuelle.cfm?Lang=F&Geo1=DA&Code1={}&Geo2=" \
          "CSD&Code2=2456060&B1=All&FILETYPE=CSV".format(p_annee, p_aire_diffusion)
    # print url
    # url = "https://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/current-actuelle.cfm?Lang=F&Geo1=CSD&Code1=2480055&Geo2=PR&Code2=24&B1=All&type=0&FILETYPE=CSV"

    print url
    response = urllib2.urlopen(url)
    df = pd.read_csv(response)

    # T_demenage
    if math.isnan(float(df.index[2233][3])):
        mob_demenage = 0
    else:
        mob_demenage = int(df.index[2233][3])
    if math.isnan(float(df.index[2231][3])):
        T_demenage = 0
    else:
        mob_tot = int(df.index[2231][3])
        T_demenage = mob_demenage / mob_tot * 100
    print "Taux de personnes ayant déménagé: {} %".format(T_demenage)

    # T_locatair
    if math.isnan(float(df.index[1620][3])):
        locataire = 0
    else:
        locataire = int(df.index[1620][3])
    if math.isnan(float(df.index[1618][3])):
        T_locatair = 0
    else:
        menage_prive_tot = int(df.index[1618][3])
        T_locatair = locataire / menage_prive_tot * 100
    print "Taux de ménage occupé par un locataire: {} %".format(T_locatair)

    # T_ages
    if math.isnan(float(df.index[25][3])):
        pop_65plus = 0
    else:
        pop_65plus = int(df.index[25][3])
    if math.isnan(float(df.index[9][3])):
        T_ages = 0
    else:
        pop_tot = int(df.index[9][3])
        T_ages = pop_65plus / pop_tot * 100
    print "Taux de personnes agées: {} %".format(T_ages)

    # T_seules
    if math.isnan(float(df.index[53][3])):
        une_personne = 0
    else:
        une_personne = int(df.index[53][3])
    if math.isnan(float(df.index[52][3])):
        T_seules = 0
    else:
        menage_tot = int(df.index[52][3])
        T_seules = une_personne / menage_tot * 100
    print "Taux de personnes seules: {} %".format(T_seules)

    # T_faibleRe
    if math.isnan(float(df.index[868][3])):
        T_faibleRe = 0
    else:
        T_faibleRe = float(df.index[868][3])
    print "Taux de faible revenu: {} %".format(T_faibleRe)

    return T_demenage, T_locatair, T_ages, T_seules, T_faibleRe


def add_taux(in_shapefile):
    cwd = os.getcwd()
    idx1 = in_shapefile.find("AD_")
    idx2 = in_shapefile.find(".shp")
    munic = in_shapefile[idx1 + 3:idx2]
    AD_taux = cwd + r"\output\AD_avecTaux_{}.shp".format(munic)
    # make a copy of the input shapefile
    if os.path.exists(AD_taux):
        arcpy.Delete_management(AD_taux)
    arcpy.Copy_management(in_shapefile, AD_taux)

    shapeData = ogr.Open(AD_taux, 1)
    layer = shapeData.GetLayer()

    # create new fields
    new_field = ogr.FieldDefn('T_demenage', ogr.OFTReal)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('T_locatair', ogr.OFTReal)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('T_ages', ogr.OFTReal)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('T_seules', ogr.OFTReal)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('T_faibleRe', ogr.OFTReal)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('vul_dem', ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('vul_loc', ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('vul_ages', ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('vul_seules', ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('vul_fRe', ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field = ogr.FieldDefn('Tot_vul', ogr.OFTReal)
    layer.CreateField(new_field)

    T_demenage_list, T_locatair_list, T_ages_list = [], [], []
    T_seules_list, T_faibleRe_list = [], []

    for i in range(len(layer)):
        feature = layer.GetFeature(i)
        adidu = feature['ADIDU']
        print "Extraction de l'information pour l'aire de diffusion: {}".format(adidu)
        T_demenage, T_locatair, T_ages, T_seules, T_faibleRe = calc_taux(2016, adidu)

        T_demenage_list.append(T_demenage)
        T_locatair_list.append(T_locatair)
        T_ages_list.append(T_ages)
        T_seules_list.append(T_seules)
        T_faibleRe_list.append(T_faibleRe)

        j = feature.GetFieldIndex("T_demenage")
        feature.SetField(j, T_demenage)
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("T_locatair")
        feature.SetField(j, T_locatair)
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("T_ages")
        feature.SetField(j, T_ages)
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("T_seules")
        feature.SetField(j, T_seules)
        layer.SetFeature(feature)

        j = feature.GetFieldIndex("T_faibleRe")
        feature.SetField(j, T_faibleRe)
        layer.SetFeature(feature)

    T_demenage_stats = calc_quantile(T_demenage_list)
    T_locatair_stats = calc_quantile(T_locatair_list)
    T_ages_stats = calc_quantile(T_ages_list)
    T_seules_stats = calc_quantile(T_seules_list)
    T_faibleRe_stats = calc_quantile(T_faibleRe_list)

    for i in range(len(layer)):
        feature = layer.GetFeature(i)

        vul_dem = calc_vuln(feature['T_demenage'], T_demenage_stats)
        j = feature.GetFieldIndex("vul_dem")
        feature.SetField(j, vul_dem)

        vul_loc = calc_vuln(feature['T_locatair'], T_locatair_stats)
        j = feature.GetFieldIndex("vul_loc")
        feature.SetField(j, vul_loc)

        vul_ages = calc_vuln(feature['T_ages'], T_ages_stats)
        j = feature.GetFieldIndex("vul_ages")
        feature.SetField(j, vul_ages)

        vul_seules = calc_vuln(feature['T_seules'], T_seules_stats)
        j = feature.GetFieldIndex("vul_seules")
        feature.SetField(j, vul_seules)

        vul_fRe = calc_vuln(feature['T_faibleRe'], T_faibleRe_stats)
        j = feature.GetFieldIndex("vul_fRe")
        feature.SetField(j, vul_fRe)

        Tot_vul = 0.49*vul_dem + 0.26*vul_ages + 0.14*vul_loc + 0.08*vul_fRe + 0.03*vul_seules
        j = feature.GetFieldIndex("Tot_vul")
        feature.SetField(j, Tot_vul)

        layer.SetFeature(feature)


def calc_quantile(in_liste):
    median = np.quantile(in_liste, .50)
    quantile75 = np.quantile(in_liste, .75)
    quantile95 = np.quantile(in_liste, .95)
    quantile99 = np.quantile(in_liste, .99)
    return median, quantile75, quantile95, quantile99


def calc_vuln(valeur, stats):
    if valeur < stats[0]:
        vul_dem = 0
    elif stats[0] <= valeur < stats[1]:
        vul_dem = 1
    elif stats[1] <= valeur < stats[2]:
        vul_dem = 2
    elif stats[2] <= valeur < stats[3]:
        vul_dem = 3
    else:
        vul_dem = 4
    return vul_dem


if __name__ == "__main__":
    # Le shapefile en entrée doit contenir toutes les aires de diffusion pour une seule municipalité
    # Exporter les tous les polygones ayant le même SDRNOM à partir de la couche lad_000a16a_f.shp
    # (dans H:\shapefile\Aires_diffusion) sous un nouveau shapefile en conservant les champs de la
    # table attributaire. Faire chaque municipalité séparément pour ensuite faire un "merge" sur les
    # l'ensemble des shapefile résultants.

    in_shp = "H:\shapefile\Aires_diffusion\DuLievre\AD_ValDesMonts.shp"
    # in_shp = "Z:\Deux_montagnes\AD_SteMarthe.shp"
    add_taux(in_shp)

    print("##############################")
    print("La couche des aires de diffusion avec taux est complété!")
    print(elapsed_time())
    print("##############################")
