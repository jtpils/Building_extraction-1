# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Station_hydro.py
# Created on: 2018-06-14
# Author : Charles Tousignant
# Project : GARI
# Description : Récupérer automatiquement les débits d’une station hydrométrique
# ---------------------------------------------------------------------------
import lxml.html as PARSER
import urllib


def suivi_hydro(url):

    data = urllib.urlopen(url).read()
    root = PARSER.fromstring(data)
    suivi_list = []
    i = 0
    for ele_table in root.getiterator(tag="table"):
        if i == 3:
            j = 0
            for ele_td in ele_table.getiterator(tag="td"):
                if 3 < j < 8:
                    suivi_list.append(ele_td.text_content())
                j += 1
        i += 1
    return suivi_list


def main():
    url = "https://www.cehq.gouv.qc.ca/suivihydro/tableau.asp?NoStation=030302&Zone=&Secteur=nulle"
    suivi_list = suivi_hydro(url)
    print(suivi_list[0])
    print(suivi_list[1])
    print(suivi_list[2])
    print(suivi_list[3])



if __name__ == "__main__":
    main()
