# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Station_hydro_EC.py
# Created on: 2018-11-19
# Author : Charles Tousignant
# Project : GARI
# Description : Récupérer automatiquement les débits d’une station hydrométrique de Environnement Canada
# ---------------------------------------------------------------------------


def suivi_hydro_EC(province, station):
    """
    Return date and water level of last mesure at a given station
    :param province: (string) Province abreviation. Ex.: Enter "QC" for Quebec.
    :param station: (string) Station code. Ex.: Enter "020J016" for Marina SJSR.
    :return date: (string) Date/time of last measure taken at station.
    :return niveau: (float) Water level of last measure.
    """
    import urllib2
    import pandas as pd
    url = "http://dd.weather.gc.ca/hydrometric/csv/{0}/hourly/{0}_{1}_hourly_hydrometric.csv".format(province, station)
    response = urllib2.urlopen(url)
    df = pd.read_csv(response)
    nb_row = len(df)
    date = df.loc[nb_row-1, "Date"]
    niveau = float(df.loc[nb_row-1, "Water Level / Niveau d'eau (m)"])
    return date, niveau


def main():
    #url = "https://eau.ec.gc.ca/report/real_time_f.html?stn=02OJ016&type=realTime&mode=Table"
    province = "QC"
    station = "02OJ007"
    date, niveau = suivi_hydro_EC(province, station)
    print date
    print niveau


if __name__ == "__main__":
    main()


