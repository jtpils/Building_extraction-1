# # -*- coding: utf-8 -*-

import geocoder

g = geocoder.bing([45.306154, -73.258873], method="elevation", key="AigfUkIm24vYk0sWgbUwgBv5klsfc5tAwFArERnDcr39MnTbPS5WE9ZRko8WiMgc")
print (g)

print g.meters




# import fiona
# from shapely.geometry import shape
#
# bv = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/Bassin_versant/Bassin_versant_SJSR_buffer.shp"
# munic = "E:/Charles_Tousignant/Python_workspace/Gari/shapefile/limite_municipalite/CAN_adm3_Clip.shp"
# zone = fiona.open(munic)
#
# polygon = next(zone)
# polygon2 = zone.next()  # meme chose
#
# shp_geom = shape(polygon['geometry'])
# shp_geom2 = shape(polygon2['geometry'])
#
# print shp_geom
# print shp_geom2
#
# print(len(zone))
# print(zone.bounds)  # bbox
# print(shp_geom.bounds)  # bbox
#
# print polygon2["id"]







# zone.close()













