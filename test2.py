from shapely.geometry import shape, Point
import fiona
from rasterstats import zonal_stats, point_query

MNT = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\inputs\Modele Numerique de Terrain\mnt_grand.tif"
bat = r"E:\Charles_Tousignant\Python_workspace\Gari\shapefile\hauteur_RDC\SJSR_2013\batiment_google.shp"

pt = Point(323982.8811404071, 5015820.659937422)
print pt

for batiment in fiona.open(bat):
    if pt.within(shape(batiment['geometry'])):
        poly = shape(batiment['geometry'])
        zs = zonal_stats(poly, MNT)
        zs_min = zs[0]['min']
        zs_max = zs[0]['max']
        zs_mean = zs[0]['mean']



# stats = zonal_stats(bat, MNT,stats=['min', 'max', 'median', 'mean', 'count', 'unique', 'std'])
# pts = point_query(bat, MNT)
#
#
# with fiona.open(bat) as src:
#     for batiment in fiona.open(src):
#         if pt.within(shape(batiment['geometry'])):
#             #print shape(bat['geometry'])
#             zs = zonal_stats(src, MNT)
#             print zs


# from shapely.geometry import Point
# pt = Point(323982.8811404071, 5015820.659937422)
# print pt
# pt.__geo_interface__
# print pt
# #{'type': 'Point', 'coordinates': (245000.0, 1000000.0)}
# a = point_query(pt, MNT)
# print a