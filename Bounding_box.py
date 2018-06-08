# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Bounding_box.py
# Created on: 2018-05-25
# Author : Charles Tousignant
# Project : GARI
# Description : Fichier de création des secteurs à extraire pour Building_extractor_MP.py
# ---------------------------------------------------------------------------

# CREATE BOUNDING BOX HERE (starting south-west corner; ending north-east corner):

####################
# SECTEURS DE TEST #
####################

# Secteur de test (SJSR)
CONST_lat_s = 45.282014  # starting latitude
CONST_lon_s = -73.260003  # starting longitude
CONST_lat_e = 45.288672  # ending latitude
CONST_lon_e = -73.248399  # ending longitude

# Secteur avec autoroute (SJSR)
CONST_lat_s2 = 45.301452  # starting latitude
CONST_lon_s2 = -73.269366  # starting longitude
CONST_lat_e2 = 45.304274  # ending latitude
CONST_lon_e2 = -73.262891  # ending longitude

# Secteur de test zoom x21 (SJSR)
CONST_lat_s3 = 45.306074  # starting latitude
CONST_lon_s3 = -73.260668  # starting longitude
CONST_lat_e3 = 45.309966  # ending latitude
CONST_lon_e3 = -73.254757  # ending longitude

# Centre ville SJSR multiprocess test
CONST_lat_s4 = 45.291382  # starting latitude
CONST_lon_s4 = -73.271735  # starting longitude
CONST_lat_e4 = 45.309895  # ending latitude       45.297242  2 process       45.309895  6 process
CONST_lon_e4 = -73.248687  # ending longitude    -73.260324                 -73.248687

# Bassin versant de la rivière Richelieu
CONST_lat_s5 = 44.987612  # starting latitude
CONST_lon_s5 = -73.632196  # starting longitude
CONST_lat_e5 = 46.085388  # ending latitude
CONST_lon_e5 = -72.997301  # ending longitude

# Secteur test Sorel
CONST_lat_s6 = 46.041671  # starting latitude
CONST_lon_s6 = -73.132354  # starting longitude
CONST_lat_e6 = 46.044132  # ending latitude
CONST_lon_e6 = -73.125611  # ending longitude

# Secteur test no building
CONST_lat_s7 = 46.006956  # starting latitude
CONST_lon_s7 = -73.124723  # starting longitude
CONST_lat_e7 = 46.009650  # ending latitude
CONST_lon_e7 = -73.118092  # ending longitude

#######################################################
# PRODUCTION : BASSIN VERSANT DE LA RIVIÈRE RICHELIEU #
#######################################################

# Secteur Sorel                                   FAIT 56min MP + contour
CONST_lat_s11 = 45.912017  # starting latitude
CONST_lon_s11 = -73.186986  # starting longitude
CONST_lat_e11 = 46.051917  # ending latitude
CONST_lon_e11 = -73.084758  # ending longitude

# Secteur St Antoine MP buffer  49 200 images     FAIT 5h40 MP + contour
CONST_lat_s12 = 45.653300  # starting latitude
CONST_lon_s12 = -73.339431  # starting longitude
CONST_lat_e12 = 45.912539  # ending latitude
CONST_lon_e12 = -73.015094  # ending longitude

# Secteur St-Jean   15 500 photos (6000x6000)     FAIT 3.6 jours NO MP
CONST_lat_s13 = 45.266021  # starting latitude
CONST_lon_s13 = -73.467910  # starting longitude
CONST_lat_e13 = 45.653953  # ending latitude
CONST_lon_e13 = -73.025775  # ending longitude

# Secteur Venise    134 500 photos        1522 km2    FAIT 15h50  MP + contour
CONST_lat_s14 = 45.003161  # starting latitude
CONST_lon_s14 = -73.609889  # starting longitude
CONST_lat_e14 = 45.266972  # ending latitude
CONST_lon_e14 = -72.948364  # ending longitude


#######################################################
# PRODUCTION : BASSIN VERSANT DE LA PETITE-NATION #
#######################################################

# COMPLET
CONST_lat_s15 = 45.565028  # starting latitude
CONST_lon_s15 = -75.374958  # starting longitude
CONST_lat_e15 = 47.106742  # ending latitude
CONST_lon_e15 = -74.262042  # ending longitude

# SUD
CONST_lat_s15 = 45.565028  # starting latitude
CONST_lon_s15 = -75.374958  # starting longitude
CONST_lat_e15 = 46.335885  # ending latitude
CONST_lon_e15 = -74.262042  # ending longitude

# NORD
CONST_lat_s15 = 46.335400  # starting latitude
CONST_lon_s15 = -75.374958  # starting longitude
CONST_lat_e15 = 47.106742  # ending latitude
CONST_lon_e15 = -74.262042  # ending longitude


