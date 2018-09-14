# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Enundation.py
# Created on: 2018-09-14
# Author : Charles Tousignant
# Project : Enundation
# Description : backend of Enundation website
# ---------------------------------------------------------------------------
import sys
import geocoder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import *
from Building_locator import *


def get_report(add1="", add2="", city="", prov="", pc=""):
    full_add = add1 + ", " + add2 + ", " + city + ", " + prov + ", " + pc
    a = building_locator(full_add)
    b = building_image(a[0])
    img = cv.imread(a[0])
    tracer_contour(b, img)


if __name__ == "__main__":
    get_report("116", "rue de Liege", "St-jean-sur-Richelieu", "Quebec")

