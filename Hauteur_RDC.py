# -*- coding: utf-8 -*-
import numpy as np
from laspy.file import File
import laspy
import matplotlib.pyplot as plt
import numpy
import scipy
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from osgeo import ogr
from shapely.geometry import mapping, Point, shape
import fiona
from rasterstats import zonal_stats, point_query

np.set_printoptions(threshold=np.nan)

# inFile = classified .las
#inFile = File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_zone_test_petit2.las", mode="r")

#inLas = laspy.file.File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_6_maisons_toit.las")
inLas = laspy.file.File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_zone_test_toit.las")
#inLas = laspy.file.File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_zone_test_petit2_toit.las")
dataset = np.vstack([inLas.x, inLas.y, inLas.z]).transpose()

MNT = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\inputs\Modele Numerique de Terrain\mnt_grand.tif"
bat = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\batiment_google.shp"

# Compute DBSCAN
db = DBSCAN(eps=2, min_samples=15).fit(dataset)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)


# #############################################################################
# Plot result


# Black removed and is used for noise instead.
unique_labels = set(labels)

colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]

point = ogr.Geometry(ogr.wkbPoint)
point_list = []
z_rdc_list = []
nb_etage_list = []

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]
    # print k

    class_member_mask = (labels == k)
    xyz = dataset[class_member_mask & core_samples_mask]

    plt.plot(xyz[:, 0], xyz[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)
    # xyz = dataset[class_member_mask & ~core_samples_mask]
    # print len(xyz)
    # plt.plot(xyz[:, 0], xyz[:, 1], 'o', markerfacecolor=tuple(col),
    #          markeredgecolor='k', markersize=6)


    #if len(xyz) != 0:
    if len(xyz) > 25:  # minimum number of points
        # var2 = np.std(xyz[:, 2])
        # print var2
        nb_etage = 1
        x_centroid = sum(xyz[:, 0]) / len(xyz)
        y_centroid = sum(xyz[:, 1]) / len(xyz)
        pt = Point(x_centroid, y_centroid)
        for batiment in fiona.open(bat):
            if pt.within(shape(batiment['geometry'])):
                poly = shape(batiment['geometry'])
                zs = zonal_stats(poly, MNT)
                zs_min = zs[0]['min']
                zs_max = zs[0]['max']
                zs_mean = zs[0]['mean']
                point_list.append(pt)
                #z_rdc = sum(xyz[:, 2]) / len(xyz)# - 2.75  # pour 1 étage
                z_rdc = min(xyz[:, 2]) - 2.50  # pour 1 étage
                while z_rdc > zs_mean + 2.50:  # au moins 25cm au desus du sol
                    nb_etage += 1
                    z_rdc = z_rdc - 2.5
                z_rdc_list.append(z_rdc)
                nb_etage_list.append(nb_etage)

schema = {
    'geometry': 'Point',
    'properties': {'Z_RDC': 'float:9.2', 'nb_etage': 'int'}
}

with fiona.open('E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\hauteur_RDC.shp', 'w', 'ESRI Shapefile', schema) as c:
    ## If there are multiple geometries, put the "for" loop here
    for i in range(len(point_list)):
        c.write({
            'geometry': mapping(point_list[i]),
            'properties': {'Z_RDC': z_rdc_list[i], 'nb_etage': nb_etage_list[i]}
        })


plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()


########################################################################
# extract roof points
# header = laspy.header.Header()
# outFile = laspy.file.File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\output.las", mode="w", header=header)
# x_list, y_list, z_list = [], [], []
# for i in range(len(inFile.points)):
#     if inFile.raw_classification[i] == 6:  # 6 = building roof
#         x_list.append(inFile.x[i].item())
#         y_list.append(inFile.y[i].item())
#         z_list.append(inFile.z[i].item())
#
#
# xmin = np.floor(np.min(x_list))
# ymin = np.floor(np.min(y_list))
# zmin = np.floor(np.min(z_list))
# outFile.header.offset = [xmin, ymin, zmin]
# outFile.header.scale = [0.001, 0.001, 0.001]
# outFile.x = np.array(x_list)
# outFile.y = np.array(y_list)
# outFile.z = np.array(z_list)
# outFile.close()
#########################################################################

#######################################################################################################
# # Grab all of the points from the file.
# point_records = inFile.points
#
#
# # Grab just the X dimension from the file, and scale it.
# def scaled_x_dimension(las_file):
#     x_dimension = las_file.X
#     scale = las_file.header.scale[0]
#     offset = las_file.header.offset[0]
#     return(x_dimension*scale + offset)
#
#
# scaled_x = scaled_x_dimension(inFile)
# print scaled_x


# Find out what the point format looks like.
# pointformat = inFile.point_format
# for spec in inFile.point_format:
#     print(spec.name)

# points_kept = []
# outFile1 = File("E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\LIDAR_zone_test_petit_1.las", mode="w", header=inFile.header)
#
# print(inFile.points)
#
# for i in range(len(inFile.points)):
#     if inFile.raw_classification[i] == 6:
#         points_kept += inFile.points[i]
#
# outFile1.points = points_kept
# outFile1.close()

# Lets take a look at the header also.
# headerformat = inFile.header.header_format
# for spec in headerformat:
#     print(spec.name)


# plt.hist(inFile.z)
# plt.title("Histogram of Z")
# plt.show()


# dataset = np.vstack([inFile.x, inFile.y, inFile.z]).transpose()
#print(dataset)