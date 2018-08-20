# Building_extraction
requirements:
* arcpy
* OpenCV
* PIL
* NumPy
* fiona
* geocoder
* GDAL
* shapely
* selenium

## Building_extractor.py
Extraction of building footprints from Google Maps to the shapefile format (.shp). 

Here is a example for extracting building footprints contained inside the St_sauveur.shp. The input shapefile must be projected and contain only one polygon 
```python
if __name__ == "__main__":
    shapefile_contour_path = "E:/Charles_Tousignant/Python_workspace/shapefile/St_sauveur.shp"
    main(shapefile_contour_path)
```
## geocode.py
Reverse geocoding of buildings in the shapefile. Create and fill new fields related to the address in the attribute table.

Here is an example how to reverse geocode an entire polygon shapefile. Enter the path of the shapefile to reverse geocode in the inShapefile variable and enter the desired path for the output file in the outShapefile variable..
```python
def main():
    inShapefile = "E:/Charles_Tousignant/Python_workspace/shapefile/Building_footprints.shp"
    outShapefile = "E:/Charles_Tousignant/Python_workspace/shapefile/Building_footprints_geocode.shp"
    geocode_shapefile(inShapefile, outShapefile)
```