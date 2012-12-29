AniMove algorithms for SEXTANTE
------------------------------

SEXTANTE is a geoprocessing environment that can be used to call native and third party algorithms from QGIS, making your spatial analysis tasks more productive and easy to accomplish.

The plugin implements, as Sextante submodule, kernel analyses with the following algs:

* "href", the “reference” bandwidth is used in the estimation
* "LSCV" (The Least Square Cross Validation) the “LSCV” bandwidth is used in the estimation
* kernel with adjusted h

Utilization distribution and contour lines will be produced, and area of the contour polygons will be calculated.

Additionally, restricted Minimum Convex Polygons (MCP) will be implemented, as:

* MCP calculation of the smallest convex polygon enclosing all the relocations of the animal, excluding an user-selected percentage of locations furthest from a centre.  provider for SEXTANTE and allows to run

--------------------------------------

Inside plugin folder you can find a sample_data directory where is stored a simple shapefiles.
It is useful to try the plugin.

QGIS_PLUGIN_FOLDER/sample_data/animals.shp 
