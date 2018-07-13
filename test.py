# -*- coding: utf-8 -*-

import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

# data = np.array([1,2,3])
# a = np.array([True,False,True])
# b = np.array([True,True,False])
#
# x = data[~a & b]
# print x
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


# #############################################################################
# Generate sample data
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
                            random_state=0)
print labels_true
X = StandardScaler().fit_transform(X)

# #############################################################################
# Compute DBSCAN
db = DBSCAN(eps=0.3, min_samples=10).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
print("Adjusted Rand Index: %0.3f"
      % metrics.adjusted_rand_score(labels_true, labels))
print("Adjusted Mutual Information: %0.3f"
      % metrics.adjusted_mutual_info_score(labels_true, labels))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))

# #############################################################################
# Plot result
import matplotlib.pyplot as plt

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

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