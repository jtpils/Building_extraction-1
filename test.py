# -*- coding: utf-8 -*-

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import time
import ogr
import osr
import gdal
import laspy
np.set_printoptions(threshold=np.nan)






#################################################################################################################
# def create_z_raster(las, tif, srs):
#     """
#     Create a height raster
#
#     las = an open laspy File
#     tif = 'path/to/tif'
#     srs = string format of spatial reference
#     """
#
#     # set up the driver in memory
#     driver = ogr.GetDriverByName('Memory')
#
#     # create the data source
#     data_source = driver.CreateDataSource('in_mem')  # get in_memory driver
#
#     # create the spatial reference
#     sr = osr.SpatialReference()
#     #sr.ImportFromWkt(srs)
#     sr.ImportFromEPSG(srs)
#     # create the layer
#     layer = data_source.CreateLayer('points', sr, ogr.wkbPoint)
#
#     # process numpy array of las points
#     las_points = np.vstack((las.x, las.y, las.z)).transpose()
#
#     print("creating point vectors...")
#     start_time = time.time()
#     for pnt in las_points:
#         # create the feature
#         feature = ogr.Feature(layer.GetLayerDefn())
#         # create the wkt for the feature
#         wkt = 'POINT ({0} {1} {2})'.format(float(pnt[0]), float(pnt[1]), float(pnt[2]))
#         # create the point from the wkt
#         point = ogr.CreateGeometryFromWkt(wkt)
#         # set the feature geometry using the point
#         feature.SetGeometry(point)
#         # create the feature in the layer
#         layer.CreateFeature(feature)
#         # dereference the feature
#         feature = None
#     print("done...")
#     print(time.time() - start_time)
#
#     # calculate raster resolutions
#     pixel_size = .2
#     xmin, xmax, ymin, ymax = layer.GetExtent()
#     x_res = int((xmax - xmin) / pixel_size) + 1  # round up and add additional pixel for remainder
#     y_res = int((ymax - ymin) / pixel_size) + 1  # round up and add additional pixel for remainder
#
#     # create destination source
#     target_ds = gdal.GetDriverByName('GTiff').Create(tif, x_res, y_res, 1, gdal.GDT_Byte)
#     target_ds.SetGeoTransform((xmin, pixel_size, 0, ymax, 0, -pixel_size))
#     band = target_ds.GetRasterBand(1)
#     band.SetNoDataValue(0)
#
#     # Rasterize
#     gdal.RasterizeLayer(target_ds, [1], layer, options=["BURN_VALUE_FROM=Z"])
#     layer = None
#     target_ds = None
#
#
#
# inLas = laspy.file.File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_6_maisons.las")
# tif_path = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\test.tif"
# create_z_raster(inLas, tif_path, 2950)
#
#
# from scipy.interpolate import griddata
# import matplotlib.pyplot as plt
# ds = gdal.Open(tif_path)
# myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
# x = len(myarray[0])
# y = len(myarray)
# print x
# print y
#
# grid_x, grid_y = np.mgrid[0:1:335j, 0:1:220j]
# points = []
# values = []
# #print myarray[219][0]
# for i in range(x):
#     for j in range(y):
#         if myarray[j-1][i-1] != 0:
#
#             points.append([i, j])
#             values.append(myarray[j-1][i-1])
#
# points_array = np.array(points)
# values_array = np.array(values)
# print len(points_array)
#
# grid_z0 = griddata(points_array, values_array, (grid_x, grid_y), method='nearest')




############################################################################
# import numpy as np
# import matplotlib.pyplot as plot
# import pylab
#
# # List of points in x axis
# XPoints     = []
#
# # List of points in y axis
# YPoints     = []
#
# # X and Y points are from -6 to +6 varying in steps of 2
# for val in range(-6, 8, 2):
#     XPoints.append(val)
#     YPoints.append(val)
#
# # Z values as a matrix
# ZPoints     = np.ndarray((7,7))
#
# # Populate Z Values (a 7x7 matrix) - For a circle x^2+y^2=z
# for x in range(0, len(XPoints)):
#     for y in range(0, len(YPoints)):
#         ZPoints[x][y] = (XPoints[x]* XPoints[x]) + (YPoints[y]*YPoints[y])
#
# # Print x,y and z values
# print(XPoints)
# print(YPoints)
# print(ZPoints)
#
# # Set the x axis and y axis limits
# pylab.xlim([-10,10])
# pylab.ylim([-10,10])
#
# # Provide a title for the contour plot
# plot.title('Contour plot')
#
# # Set x axis label for the contour plot
# plot.xlabel('X')
#
# # Set y axis label for the contour plot
# plot.ylabel('Y')
#
# # Create contour lines or level curves using matplotlib.pyplot module
# contours = plot.contour(XPoints, YPoints, ZPoints)
# print type(contours)
# # Display z values on contour lines
# plot.clabel(contours, inline=1, fontsize=10)
#
# # Display the contour plot
# plot.show()

#####################################################################

import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# delta = 0.025
# x = np.arange(-3.0, 3.0, delta)
# y = np.arange(-2.0, 2.0, delta)
# X, Y = np.meshgrid(x, y)
# Z1 = np.exp(-X**2 - Y**2)
# Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
# Z = (Z1 - Z2) * 2
#
# print Z


# matplotlib.rcParams['xtick.direction'] = 'out'
# matplotlib.rcParams['ytick.direction'] = 'out'
#
# delta = 0.025
# x = np.arange(-3.0, 3.0, delta)
# y = np.arange(-2.0, 2.0, delta)
# X, Y = np.meshgrid(x, y)
# Z1 = mlab.bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
# Z2 = mlab.bivariate_normal(X, Y, 1.5, 0.5, 1, 2)
# # difference of Gaussians
# Z = 10.0 * (Z2 - Z1)
#
# # Create a simple contour plot with labels using default colors.  The
# # inline argument to clabel will control whether the labels are draw
# # over the line segments of the contour, removing the lines beneath
# # the label
# plt.figure()
# print Y
# CS = plt.contour(X, Y, Z)
# plt.clabel(CS, inline=1, fontsize=10)
# plt.title('Simplest default with labels')
# plt.show()
#
#
# dat0= CS.allsegs[5][0]
#
# plt.plot(dat0[:,0],dat0[:,1])
# plt.show()



# # #############################################################################
# # Generate sample data
# centers = [[1, 1], [-1, -1], [1, -1]]
# X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
#                             random_state=0)
# X = StandardScaler().fit_transform(X)
#
# # #############################################################################
# # Compute DBSCAN
# db = DBSCAN(eps=0.3, min_samples=10).fit(X)
# core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
# core_samples_mask[db.core_sample_indices_] = True
# labels = db.labels_
#
# # Number of clusters in labels, ignoring noise if present.
# n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#
# print('Estimated number of clusters: %d' % n_clusters_)
# print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
# print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
# print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
# print("Adjusted Rand Index: %0.3f"
#       % metrics.adjusted_rand_score(labels_true, labels))
# print("Adjusted Mutual Information: %0.3f"
#       % metrics.adjusted_mutual_info_score(labels_true, labels))
# print("Silhouette Coefficient: %0.3f"
#       % metrics.silhouette_score(X, labels))
#
# # #############################################################################
# # Plot result
# import matplotlib.pyplot as plt
#
# # Black removed and is used for noise instead.
# unique_labels = set(labels)
# colors = [plt.cm.Spectral(each)
#           for each in np.linspace(0, 1, len(unique_labels))]
# for k, col in zip(unique_labels, colors):
#     if k == -1:
#         # Black used for noise.
#         col = [0, 0, 0, 1]
#
#     class_member_mask = (labels == k)
#
#     xy = X[class_member_mask & core_samples_mask]
#     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
#              markeredgecolor='k', markersize=14)
#
#     xy = X[class_member_mask & ~core_samples_mask]
#     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
#              markeredgecolor='k', markersize=6)
#
# plt.title('Estimated number of clusters: %d' % n_clusters_)
# plt.show()


















###########  TEST couleur#########################
# import Utils_MP
# import cv2 as cv
#
# im_path = "E:/Charles_Tousignant/Python_workspace/Gari/screenshots/test3.png"
# img_google = cv.imread(im_path)
# img_gray = cv.cvtColor(img_google, cv.COLOR_BGR2GRAY)
#
# image_bat = Utils_MP.building_image(img_google)
# #Utils_MP.tracer_contour(image_bat, img_google)
#
# ret, thresh1 = cv.threshold(img_gray, 234, 255, cv.THRESH_BINARY)  # with 3D buildings 239
# ret, thresh2 = cv.threshold(img_gray, 237, 255, cv.THRESH_BINARY)  # without 3D buildings 240
# residentiel = thresh1 - thresh2  #3D buildings in white
#
# Utils_MP.tracer_contour(residentiel, img_google)

# cv.imshow("T1", thresh1)
# cv.imshow("T2", thresh2)
# cv.imshow("res", residentiel)
# cv.imshow("gray", img_gray)
# cv.waitKey(0)
#image2features(image_bat, feat, lat, lon_s)

#################################TEST OPENCV #########################
# import cv2 as cv
# import Utils_MP
#
# image = cv.imread("E:/Charles_Tousignant/Python_workspace/Gari/screenshots/screenshot5.png")
# gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # grayscale
# _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)  # threshold
# kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))
# dilated = cv.dilate(thresh, kernel, iterations=10)  # dilate
# #_, contours, hierarchy = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)  # get contours
#
# #dst1 = cv.inpaint(image, dilated, 3, cv.INPAINT_TELEA)
# dst2 = cv.inpaint(image, dilated, 3, cv.INPAINT_NS)
# gray2 = cv.cvtColor(dst2, cv.COLOR_BGR2GRAY)  # grayscale
#
#
# ret, thresh1 = cv.threshold(gray2, 234, 255, cv.THRESH_BINARY)  # 234 # with residential buildings 236
# # cv.imshow('Image thresh1', thresh1)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh2 = cv.threshold(gray2, 237, 255, cv.THRESH_BINARY)  # 237 without residential buildings 237
# # cv.imshow('Image thresh2', thresh2)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# residentiel = thresh1 - thresh2  # residential buildings in white
# # cv.imshow('Image residentiel', residentiel)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh3 = cv.threshold(gray2, 247, 255, cv.THRESH_BINARY)  # with commercial buildings
# # cv.imshow('Image thresh3', thresh3)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# ret, thresh4 = cv.threshold(gray2, 248, 255, cv.THRESH_BINARY)  # without commercial buildings
# # cv.imshow('Image thresh4', thresh4)
# # cv.waitKey(0)
# # cv.destroyAllWindows()
# commercial = thresh3 - thresh4  # commercial buildings in white
# cv.imshow('Image commercial', commercial)
# cv.waitKey(0)
# cv.destroyAllWindows()
# kernel = cv.getStructuringElement(cv.MORPH_RECT, (20, 20))
# closing = cv.morphologyEx(commercial, cv.MORPH_CLOSE, kernel)
# cv.imshow('Image closing', closing)
# cv.waitKey(0)
# cv.destroyAllWindows()
# ret, thresh5 = cv.threshold(gray2, 238, 255, cv.THRESH_BINARY)  # with 3D buildings 239
# ret, thresh6 = cv.threshold(gray2, 240, 255, cv.THRESH_BINARY)  # without 3D buildings 240
# building_3d = thresh5 - thresh6  # 3D buildings in white
# #  Erase white lines
# minThick = 15  # Define minimum thickness
# se = cv.getStructuringElement(cv.MORPH_ELLIPSE, (minThick, minThick))  # define a disk element
# img_bat = 255 * cv.morphologyEx(residentiel.astype('uint8'), cv.MORPH_OPEN, se)
# img_bat += 255 * cv.morphologyEx(commercial.astype('uint8'), cv.MORPH_OPEN, se)
# img_bat += 255 * cv.morphologyEx(building_3d.astype('uint8'), cv.MORPH_OPEN, se)





# Utils_MP.tracer_contour(img_bat, image)
# features = []
# Utils_MP.image2features(img_bat, features, 45.45, -73.25)
# print features

# cv.imshow('Image Google', thresh)
# cv.imshow('Image Google', kernel)
# cv.imshow('Image Google', dilated)
# cv.imshow('Image Google', dst1)
# cv.waitKey(0)
# cv.imshow('Image Google', img_bat)
# cv.waitKey(0)
# cv.destroyAllWindows()



# for each contour found, draw a rectangle around it on original image
# for contour in contours:
#     # get rectangle bounding contour
#     [x, y, w, h] = cv.boundingRect(contour)
#
#     # discard areas that are too large
#     # if h > 300 and w > 300:
#     #     continue
#     #
#     # # discard areas that are too small
#     # if h < 40 or w < 40:
#     #     continue
#
#     # draw rectangle around contour on original image
#     cv.rectangle(image, (x, y), (x+w, y+h), (255, 0, 255), 2)

# write original image with added contours to disk
#cv.imwrite("contoured.jpg", image)