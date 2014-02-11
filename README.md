cad-to-arcgis-toolbox
=====================

CAD files store data according to geometry, distinguishing between different groups of features using an attribute table field named Layers. All points, all lines and all polygons are stored together.

Since ArcGIS groups similar features together in feature classes, when importing data from CAD, typically the workflow is to select one group of features based on the Layer field, export them and move on to the next. This is time consuming and redundant, a perfect task for a script. Hence this script.

UPDATE 11Feb2014: This repository is a complete rebuild. The class objects at the top of the script include functionality to export by layer and all layers in a CAD file across all three geometries; points, lines and polygons. Right now however, the toolbox only contains one tool with the the capability to export a single layer using the default name.
