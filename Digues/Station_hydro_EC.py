# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Station_hydro_EC.py
# Created on: 2018-11-19
# Author : Charles Tousignant
# Project : GARI
# Description : Récupérer automatiquement les débits d’une station hydrométrique de Environnement Canada
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
    #print data
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
    print i
    return suivi_list


def main():
    url = "https://www.cehq.gouv.qc.ca/suivihydro/tableau.asp?NoStation=030302&Zone=&Secteur=nulle"
    #url = "https://eau.ec.gc.ca/report/real_time_f.html?stn=02OJ016&type=realTime&mode=Table"
    suivi_list = suivi_hydro(url)
    print(suivi_list[0])
    print(suivi_list[1])
    print(suivi_list[2])
    print(suivi_list[3])


if __name__ == "__main__":
    main()
