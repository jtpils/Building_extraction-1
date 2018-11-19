# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Station_hydro.py
# Created on: 2018-06-14
# Author : Charles Tousignant
# Project : GARI
# Description : Récupérer automatiquement les débits d’une station hydrométrique (scheduled task every hours at :48)
# ---------------------------------------------------------------------------


def suivi_hydro(url):
    import unicodedata
    import urllib
    import lxml.html as parser
    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    data = urllib.urlopen(url, context=ctx).read()
    root = parser.fromstring(data)
    suivi_list = []
    i = 0
    for ele_table in root.getiterator(tag="table"):
        if i == 3:
            j = 0
            for ele_td in ele_table.getiterator(tag="td"):
                if 3 < j < 8:
                    info = unicodedata.normalize('NFKD', unicode(ele_td.text_content())).encode('ascii', 'ignore')
                    suivi_list.append(info)
                j += 1
        i += 1
    suivi_list[2] = float(suivi_list[2].replace(",", "."))
    suivi_list[3] = float(suivi_list[3].replace(",", "."))
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
