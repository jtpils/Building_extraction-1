# # -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Utils_MP import *
from PIL import Image
from io import BytesIO
import numpy as np

feat = []

image_path = "E:\Charles_Tousignant\Python_workspace\Gari\screenshots\imagetest.png"
image = cv.imread(image_path)
img_bat = building_image(image)
#tracer_contour(img_bat, image)
image2features(img_bat, feat, 45, -73)

shapefile_creator(feat,1)

# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('start-maximized')
# options.add_argument('disable-infobars')
# options.add_argument("--disable-extensions")
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome("E:/Charles_Tousignant/Python_workspace/Gari/chromedriver", chrome_options=options)
# driver.set_window_size(2418, 2000)
# feat = []
#
# url = "https://www.google.ca/maps/@46.1551014,-74.6953247,21z?hl=en-US"
# driver.get(url)
#
#
#
# png = driver.get_screenshot_as_png()
# im = Image.open(BytesIO(png))  # uses PIL library to open image in memory
# im = im.crop((418, 0, 2418, 2000))  # defines crop points
# im.save("E:/Charles_Tousignant/Python_workspace/Gari/screenshots2/screenshotfff.png")  # saves new cropped image
#
# image_bat = building_image(np.array(im))
# image2features(image_bat, feat, 46.1551014, -74.6953247)
# shapefile_creator(feat, 1)
#
# driver.quit()












