# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# match_adr.py
# Created on: 2019-03-27
# Author : Charles Tousignant
# Project : GARI
# Description : Create .xls file that match adresses and informations
# ---------------------------------------------------------------------------
import xlwt
import pandas as pd
from utils import *


def create_match_xls(reclamation_xls):
    """
    Crée un fichier .xls qui contient les adresses des batiments pour chaque municipalité
    :param reclamation_xls: (string) path du shapefile de batiments extraits avec Building_extractor.py et geocode.py
    """
    reclamation_xls = pd.ExcelFile(reclamation_xls)
    #reclamation_frame = reclamation_xls.parse(usecols=[3, 6, 20])
    reclamation_frame = reclamation_xls.parse(usecols=[3, 6, 8, 13, 20])

    book = xlwt.Workbook(encoding='UTF-8')
    entete = xlwt.easyxf("font: bold on; borders: bottom thick")
    sheet = book.add_sheet("Adresses")
    sheet.write(0, 0, "Adresses", style=entete)
    sheet.write(0, 1, "Adresses uni", style=entete)
    sheet.write(0, 2, "Acc_imm", style=entete)

    for i in range(len(reclamation_frame)):
        adr = str(reclamation_frame.loc[i][1].encode(encoding='UTF-8')) + ", " + str(reclamation_frame.loc[i][0].encode(encoding='UTF-8')) + ", Quebec"
        adr_uni = address_uniform(adr)
        type_cli = str(reclamation_frame.loc[i][2])
        reclamation_entreprise = str(reclamation_frame.loc[i][3])
        reclamation = str(reclamation_frame.loc[i][4])
        #reclamation = str(reclamation_frame.loc[i][2])

        sheet.write(i+1, 0, adr)
        sheet.write(i+1, 1, adr_uni)
        if type_cli == "E":
            sheet.write(i+1, 2, reclamation_entreprise)
        else:
            sheet.write(i + 1, 2, reclamation)
        print(adr)

    out_excel = os.getcwd() + r"\output\match_adr.xls"
    book.save(out_excel)


def address_uniform(addr):
    """
    Return the corresponding uniform address
    :param addr: (string) address
    :return (string) uniform address
    """
    # if addr == "":
    #     return ""
    # if "BEAULIEU" in addr:
    #     addr = addr + ", Saint-Jean-sur-Richelieu"
    # if "BEAUBIEN" in addr:
    #     addr = addr + ", Saint-Jean-sur-Richelieu"
    # if "SAINT-MAURICE" in addr:
    #     addr = addr + ", Saint-Jean-sur-Richelieu"
    # else:
    #     addr = addr + ", Saint-Jean-sur-Richelieu, Canada"

    key = "AjVyhHv7lq__hT5_XLZ8jU0WbQpUIEUhQ7_nlHDw9NlcID9jRJDYLSSkIQmuQJ82"  # quota de 125 000 requêtes/année
    # b = geocoder.bing([lat, lon], key=key)
    g = geocoder.bing(addr, key=key)
    #g = geocoder.google(addr)
    gjson = g.json
    timeout = time.time() + 15
    while gjson is None:  # Redo until we have a response
        g = geocoder.google(addr)
        gjson = g.json
        if time.time() > timeout:  # if google can't find the address after a certain amount of time
            #sys.exit("Google ne trouve pas cette adresse, veuillez réessayer")
            return " "
    #print g.address.encode(encoding='UTF-8')
    return str(g.address.encode(encoding='UTF-8'))


def join_reclamation_bat(rdc, match):

    rdc_xls = pd.ExcelFile(rdc)
    rdc_frame = rdc_xls.parse(usecols=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    match_xls = pd.ExcelFile(match)
    match_frame = match_xls.parse()
    match_list = [list(l) for l in zip(*match_frame.values)]
    adr_uni_list = [x.encode('UTF8') for x in match_list[1]]
    reclamation_list = match_list[2]

    book = xlwt.Workbook(encoding='UTF-8')
    sheet = book.add_sheet("test")
    count = 0
    for i in range(len(rdc_frame)):
        adr = str(rdc_frame.loc[i][0]) + " " + str(rdc_frame.loc[i][1].encode(encoding='UTF-8')) \
              + ", " + str(rdc_frame.loc[i][2].encode(encoding='UTF-8'))
        adr_uni = address_uniform(adr)

        if adr_uni in adr_uni_list:
            idx = adr_uni_list.index(adr_uni)
            sheet.write(i, 0, adr_uni)
            sheet.write(i, 1, reclamation_list[idx])
            count += 1
        else:
            sheet.write(i, 0, adr_uni)
            sheet.write(i, 1, "Non disponible")

    out_excel = os.getcwd() + r"\output\reclamation_match.xls"
    book.save(out_excel)


if __name__ == "__main__":
    # print address_uniform("4609 RUE DE L'ÎLE-SAINTE-MARIE, CANADA")
    reclamation_data = "H:\Donnees\donnees_SJSR_del.xlsx"
    create_match_xls(reclamation_data)

    # rdc_data = r'H:\Donnees\1er planchers\Donnees 1ers planchers part 3.xlsx'
    # match_adr = r'H:\Donnees\match_adr.xls'
    # join_reclamation_bat(rdc_data, match_adr)

    print("##############################")
    print("Excel file complete!")
    print(elapsed_time())
    print("##############################")