# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# address_extractor.py
# Created on: 2019-01-16
# Author : Charles Tousignant
# Project : GARI
# Description : Create .xls file that contains all the addresses of the input building shapefile
# ---------------------------------------------------------------------------
from utils import *
import xlwt
import ogr


def create_csv(in_bat_shp):
    """
    Crée un fichier .xls qui contient les adresses des batiments pour chaque municipalité
    :param in_bat_shp: (string) path du shapefile de batiments extraits avec Building_extractor.py et geocode.py
    """
    backlash = r"\'"
    file_name = in_bat_shp.split(backlash[0])[-1].split(".")[0]
    ville_list = []
    book = xlwt.Workbook()
    entete = xlwt.easyxf("font: bold on; borders: bottom thick")
    shapeData = ogr.Open(in_bat_shp, 1)
    layer = shapeData.GetLayer()

    for i in range(len(layer)):
        feature = layer.GetFeature(i)
        ville = (feature['Ville'])
        if ville not in ville_list:
            ville_list.append(ville)
            sheet = book.add_sheet(ville.decode(encoding='UTF-8'))
            sheet.write(0, 0, "Adresses", style=entete)
            sheet.write(0, 1, "Matricule", style=entete)
            sheet.write(0, 2, "Nb_etages", style=entete)
            sheet.write(0, 3, "Aire_totale_ss", style=entete)
            sheet.write(0, 4, "Type_util", style=entete)
            sheet.write(0, 5, "Valeur_batiment", style=entete)
            sheet.write(0, 6, "Hauteur_rdc", style=entete)
            n = 1
            adresse_list = []
            for j in range(len(layer)):
                feature = layer.GetFeature(j)
                adresse = feature['Adresse_im']
                if adresse not in adresse_list and ville == feature['Ville']:
                    print(adresse)
                    adresse_list.append(adresse)
                    sheet.write(n, 0, adresse.decode(encoding='UTF-8'))
                    n += 1

    out_excel = os.getcwd() + r"\output\Adresses_" + file_name + ".xls"
    book.save(out_excel)


def join_valeur_bat(principal, valeur_bat):
    """
    Crée un fichier .xls resultant d'une jointure entre le champ Matricule
    :param principal: (string) path du fichier principal .xlsx contenant les info sauf la valeur du batiment
    :param valeur_bat: (string) path du fichier .xlsx a joindre contenant la valeur du batiment et le matricule
    """
    import pandas as pd

    princ_xls = pd.ExcelFile(principal)
    princ_frame = princ_xls.parse(usecols=[3, 15, 20, 22])
    join_xls = pd.ExcelFile(valeur_bat)
    join_frame = join_xls.parse()

    liste_matricule, liste_valeur = [], []
    for i in range(len(join_frame)):
        liste_matricule.append(str(join_frame.loc[i][0])[0:12])
        liste_valeur.append(join_frame.loc[i][1])

    matricule, aire_ss, nb_etage, type_util, val_bat = [], [], [], [], []

    for i in range(len(princ_frame)):
        mat = princ_frame.loc[i][0]
        if mat in liste_matricule:
            index = liste_matricule.index(mat)
            val = liste_valeur[index]
        else:
            val = 0
        matricule.append(mat)
        aire_ss.append(princ_frame.loc[i][1])
        nb_etage.append(princ_frame.loc[i][2])
        type_util.append(princ_frame.loc[i][3])
        val_bat.append(val)
        if not i % 1000:
            print "{} entrées ont été jointes".format(i)

    d = {'Matricule': matricule, 'Aire_totale_ss': aire_ss, 'Nb_etages': nb_etage, 'Type_util': type_util, 'Valeur_bat': val_bat}
    df = pd.DataFrame(data=d)
    #print df
    df.to_excel(os.getcwd() + "\output\join_valeur_bat.xlsx", index=False)


if __name__ == "__main__":
    # fichier_principal = r"H:\shapefile\MATRICULES\56083-GARIx.xlsx"
    # fichier_valeur_bat = r"H:\Donnees\ValeursBatiments - SJSR.xlsx"
    #
    # join_valeur_bat(fichier_principal, fichier_valeur_bat)

    #################################################################

    print("Extraction des adresses...")
    in_bat = "H:\shapefile\Zones_extraction\SJSR\MRC_Vallee_du_Richelieu.shp"
    create_csv(in_bat)

    print("##############################")
    print("Excel file complete!")
    print(elapsed_time())
    print("##############################")
