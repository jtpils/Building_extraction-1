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
    #import pandas as pd

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.urlopen(url, context=ctx).read()

    # tables = pd.read_html(html)
    # date = unicodedata.normalize('NFKD', unicode(tables[2][0][1])).encode('ascii', 'ignore')
    # heure = unicodedata.normalize('NFKD', unicode(tables[2][1][1])).encode('ascii', 'ignore')
    # niveau = unicodedata.normalize('NFKD', unicode(tables[2][2][1])).encode('ascii', 'ignore')
    # niveau = float(niveau.replace("*", "").replace(",", "."))
    # debit = unicodedata.normalize('NFKD', unicode(tables[2][3][1])).encode('ascii', 'ignore')
    # debit = float(debit.replace("*", "").replace(",", "."))

    ##########Autre méthode (sans pandas)############
    root = parser.fromstring(html)
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
    date = suivi_list[0]
    heure = suivi_list[1]
    niveau = float(suivi_list[2].replace("*", "").replace(",", "."))
    debit = float(suivi_list[3].replace("*", "").replace(",", "."))
    ##################################
    return date, heure, niveau, debit


def main():
    url = "https://www.cehq.gouv.qc.ca/suivihydro/tableau.asp?NoStation=030302&Zone=&Secteur=nulle"
    date, heure, niveau, debit = suivi_hydro(url)
    print("date : {}".format(date))
    print("heure : {}".format(heure))
    print("niveau : {}".format(niveau))
    print("debit : {}".format(debit))


if __name__ == "__main__":
    main()
