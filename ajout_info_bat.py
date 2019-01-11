# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ajout_info_bat.py
# Created on: 2019-01-10
# Author : Charles Tousignant
# Project : GARI
# Description : Ajouter de l'information à la couche de bâtiments (Matricule,
# Valeur_bat, Nb_etages, Pres_ss1, Zrc)
# ---------------------------------------------------------------------------

from utils import *
import pandas as pd
import openpyxl


def ajout_matricule(inBat, inMatrice):

    copie_batiments = create_ScratchGDB_name("copie_batiments")
    arcpy.CopyFeatures_management(inBat, copie_batiments)
    out_shp = create_ScratchGDB_name("out_shp")

    # arcpy.AddField_management(copie_batiments, "Matricule", "LONG")
    # arcpy.AddField_management(copie_batiments, "Valeur_bat", "LONG")
    # arcpy.AddField_management(copie_batiments, "Nb_etages", "SHORT")
    # arcpy.AddField_management(copie_batiments, "Pres_ss1", "SHORT")
    # arcpy.AddField_management(copie_batiments, "Zrc", "FLOAT")

    # Create FieldMappings object
    fms = arcpy.FieldMappings()
    fm_adresse = arcpy.FieldMap()
    fm_numciv = arcpy.FieldMap()
    fm_rue = arcpy.FieldMap()
    fm_ville = arcpy.FieldMap()
    fm_province = arcpy.FieldMap()
    fm_CP = arcpy.FieldMap()
    fm_pays = arcpy.FieldMap()
    fm_matricule = arcpy.FieldMap()
    fm_lot = arcpy.FieldMap()

    fm_adresse.addInputField(copie_batiments, "Adresse")
    fm_numciv.addInputField(copie_batiments, "Num_Civ")
    fm_rue.addInputField(copie_batiments, "Rue")
    fm_ville.addInputField(copie_batiments, "Ville")
    fm_province.addInputField(copie_batiments, "Province")
    fm_CP.addInputField(copie_batiments, "CP")
    fm_pays.addInputField(copie_batiments, "Pays")
    fm_matricule.addInputField(inMatrice, "SI0317C")
    fm_lot.addInputField(inMatrice, "SI0424J")

    matricule_name = fm_matricule.outputField
    matricule_name.name = 'Matricule'
    fm_matricule.outputField = matricule_name
    lot_name = fm_lot.outputField
    lot_name.name = 'Lot'
    fm_lot.outputField = lot_name

    fms.addFieldMap(fm_adresse)
    fms.addFieldMap(fm_numciv)
    fms.addFieldMap(fm_rue)
    fms.addFieldMap(fm_ville)
    fms.addFieldMap(fm_province)
    fms.addFieldMap(fm_CP)
    fms.addFieldMap(fm_pays)
    fms.addFieldMap(fm_matricule)
    fms.addFieldMap(fm_lot)

    # Spatial join for Matricule field
    arcpy.SpatialJoin_analysis(target_features=copie_batiments,
                               join_features=inMatrice,
                               out_feature_class=out_shp,
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping=fms,
                               match_option="HAVE_THEIR_CENTER_IN",
                               search_radius=0)

    return out_shp

def testt():
    import ogr
    # info = pd.read_excel('H:/shapefile/MATRICULES/56083-GARI.xls')
    #
    # matricule = info['Matricule']
    # aire_ss = info['Aire totale ss']
    # nb_etage = info['Nb etages']
    bat_shp = r"H:\shapefile\TEST\testt.shp"

    shapeData = ogr.Open(bat_shp, 1)
    layer = shapeData.GetLayer()  # get possible layers.
    layer_defn = layer.GetLayerDefn()  # get definitions of the layer

    # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in
    #                range(layer_defn.GetFieldCount())]  # store the field names as a list of strings
    # print len(field_names)  # so there should be just one at the moment called "FID"
    # print field_names  # will show you the current field names

    #new_field = ogr.FieldDefn('HOMETOWN', ogr.OFTString)  # we will create a new field called Hometown as String
    #layer.CreateField(new_field)  # self explaining
    new_field = ogr.FieldDefn('Nb_etages', ogr.OFTInteger)  # and a second field 'VISITS' stored as integer
    layer.CreateField(new_field)  # self explaining
    # field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    # print field_names

    new_field = ogr.FieldDefn('Pres_ss1', ogr.OFTInteger)  # and a second field 'VISITS' stored as integer
    layer.CreateField(new_field)  # self explaining

    info = pd.read_excel('H:/shapefile/MATRICULES/56083-GARI.xls')

    serie_mat = info['Matricule']
    serie_aire_ss = info['Aire totale ss']
    serie_etage = info['Nb etages']

    for i in range(len(layer)):
        feature = layer.GetFeature(i)  # lets get the first feature (FID=='0')
        matricule = feature['Matricule']
        print matricule
        if matricule is None:
            j = feature.GetFieldIndex("Nb_etages")  # so iterate along the field-names and store it in iIndex
            feature.SetField(j, 9999)  # exactly at this position I would like to write 'Chicago'
            layer.SetFeature(feature)  # now make the change permanent
            j = feature.GetFieldIndex("Pres_ss1")  # so iterate along the field-names and store it in iIndex
            feature.SetField(j, 9999)  # exactly at this position I would like to write 'Chicago'
            layer.SetFeature(feature)  # now make the change permanent
        else:
            matricule_format = matricule[0:4] + "-" + matricule[4:6] + "-" + matricule[6:10]
            nb_etage, pres_ss = search_xls(matricule_format, serie_mat, serie_aire_ss, serie_etage)
            j = feature.GetFieldIndex("Nb_etages")  # so iterate along the field-names and store it in iIndex
            feature.SetField(j, nb_etage)  # exactly at this position I would like to write 'Chicago'
            layer.SetFeature(feature)  # now make the change permanent
            j = feature.GetFieldIndex("Pres_ss1")  # so iterate along the field-names and store it in iIndex
            feature.SetField(j, pres_ss)  # exactly at this position I would like to write 'Chicago'
            layer.SetFeature(feature)  # now make the change permanent


    shapeData = None  # lets close the shape file again.

# def search_xls(mat):
#     info = pd.read_excel('H:/shapefile/MATRICULES/56083-GARI.xls')
#
#     matricule = info['Matricule']
#     aire_ss = info['Aire totale ss']
#     nb_etage = info['Nb etages']
#     if mat in list(matricule):
#         a = list(matricule).index(mat)
#         #a = [i for i, x in enumerate(list(matricule)) if x == mat]
#         nb_etage = nb_etage[a]
#         if aire_ss[a] > 0:
#             pres_ss = 1
#         else:
#             pres_ss = 0
#     else:
#         nb_etage = 9999
#         pres_ss = 9999
#     return nb_etage, pres_ss

def search_xls(mat, matricule, aire_ss, nb_etage):

    if mat in list(matricule):
        a = list(matricule).index(mat)
        #a = [i for i, x in enumerate(list(matricule)) if x == mat]
        etage = nb_etage[a]
        if aire_ss[a] > 0:
            pres_ss = 1
        else:
            pres_ss = 0
    else:
        etage = 9999
        pres_ss = 9999
    return etage, pres_ss


def main():
    """
    Main function.
    """
    inBat = "H:\shapefile\TEST\SJSR_bat_zone_inon_verif.shp"
    inMatrice = "H:\shapefile\TEST\SICADA_LLOT_S.shp"
    a = ajout_matricule(inBat, inMatrice)

    arcpy.FeatureClassToFeatureClass_conversion(a, "H:\shapefile\TEST", "testt")


if __name__ == "__main__":
    clean_scratch_dir()
    main()
    print("##############################")
    print("L'ajout est complété!")
    print(elapsed_time())
    print("##############################")
    testt()
    # b = search_xls('2720-60-0237')
    # print b
    print("##############################")
    print("L'ajout est complété!")
    print(elapsed_time())
    print("##############################")