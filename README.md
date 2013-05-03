cad-to-arcgis-toolbox
=====================

CAD files store data according to geometry, distinguishing between different groups of features using an attribute table field named Layers. All points, all lines and all polygons are stored together.

Since ArcGIS groups similar features together in feature classes, when importing data from CAD, typically the workflow is to select one group of features based on the Layer field, export them and move on to the next. This is time consuming and redundant, a perfect task for a script. Hence this script. This script creates a new feature class in the target workspace for every unique value in the Layer field.
