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
    backlash = r"\'"
    file_name = in_bat.split(backlash[0])[-1].split(".")[0]
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


if __name__ == "__main__":
    print("Extraction des adresses...")
    in_bat = "H:\shapefile\Zones_extraction\SJSR\MRC_Vallee_du_Richelieu.shp"
    create_csv(in_bat)
    print("##############################")
    print("Excel file complete!")
    print(elapsed_time())
    print("##############################")
