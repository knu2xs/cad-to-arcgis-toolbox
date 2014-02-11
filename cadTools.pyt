"""
Purpose:
    A new and improved version of the CAD conversion Python toolbox. The business logic includes the capability to
    export a single layer or all layers from the CAD file, although this has yet to be integrated into the
Licence:
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# import modules
import arcpy
import os.path


class CadLayer(object):
    """
    Although these become a feature class, they start as CAD layers. Hence, this encompasses the capability to manage
    these as autonomous objects.
    """
    def __init__(self, cad_file, cad_fc, cad_layer):
        self.cad_file = cad_file
        self.cad_fc = cad_fc
        self.name = cad_layer

    def export(self, output_gdb, new_name=None):
        """
        Export the feature class to a new location with an optional new name.
        """
        # if a new name is not specified, the output name is pulled from the cad layer name
        if new_name is None:
            output_name = self.name

        # clean up any invalid names
        output_name = arcpy.ValidateTableName(output_name, output_gdb)

        # create sql query for exporting
        sql = """"Layer" = '{0}'""".format(self.name)

        # create full path to cad feature class
        fc_path = os.path.join(self.cad_file, self.cad_fc)

        # export layer as feature class to target workspace
        arcpy.FeatureClassToFeatureClass_conversion(fc_path, output_gdb, output_name, sql)


class CadFile(object):
    """
    A CAD file including what we are interested in, the source and the ability to catalog all layers. Also includes
    the capability to export all the layers to a target geodatabase as distinct feature classes in one fell swoop.
    """
    def __init__(self, cad_file):
        self.cad_file = cad_file
        self.layers = self.get_layers()
        self.layer_names = [layer.name for layer in self.layers]

    def get_layers(self):
        """
        Get a full list of layers from the points, lines and polygons the CAD file for exporting.
        """
        # set workspace for listing
        arcpy.env.workspace = self.cad_file

        # list to store all layers
        layers = []

        # for every feature class in the cad file we are interested in
        for fc in ['Polyline', 'Point', 'Polygon']:

            # get list of layers in cad file
            allValues = [row[0] for row in arcpy.da.SearchCursor(fc, 'Layer')]

            # make a set of values to get rid of duplicates
            layer_names = sorted(set(allValues))

            # for every layer in the feature class
            for lyr in layer_names:

                # create a layer object instance for the layer
                layers.append(CadLayer(self.cad_file, fc, lyr))

        # return layer object list
        return layers

    def export_layer(self, out_layer_name, output_gdb):
        """
        Export a single layer from the CAD file
        """
        # for every layer name
        for layer in self.layers:

            # if the name matches the output
            if out_layer_name == layer.name:

                # export the layer
                layer.export(output_gdb)

    def export_all(self, output_gdb):
        """
        Provide functionality for export all layers to a target feature class
        """
        # for every layer found
        for layer in self.layers:

            # export the layer using the built in method
            layer.export(output_gdb)


def parameter(displayName, name, datatype, defaultValue=None, parameterType=None, direction=None):
    """
    The parameter implementation makes it a little difficult to quickly
    create parameters with defaults. This method prepopulates the paramaeterType
    and direction parameters and leaves the setting a default value for the
    newly created parameter as optional. The displayName, name and datatype are
    the only required inputs.
    """
    # create parameter with a few defaults
    param = arcpy.Parameter(
        displayName=displayName,
        name=name,
        datatype=datatype,
        parameterType='Required',
        direction='Input'
    )

    # set new parameter to a default value
    param.value = defaultValue

    # return the complete parameter object
    return param


class Toolbox(object):
    def __init__(self):
        """
        Define the toolbox properties here. Do not change the name of this
        class. ArcGIS locates this class by name. It will not be able to find
        the toolbox and your toolbox will not work if you modify this.
        """
        self.label = 'cadTools'
        self.alias = 'CAD Tools'

        # List of tool classes associated with this toolbox
        self.tools = [ExportLayer]


class ExportLayer(object):
    """
    Add documentation here explaining your tool. The name of this class
    identifying the tool is referenced as a list item above, in the Toolbox's
    self.tools list.
    """
    def __init__(self):
        """
        Define the tool class attributes, including your tool parameters.
        """
        self.label = 'Export CAD Layer'
        self.alias = 'exportCadLayer'
        self.canRunInBackground = False

        self.parameters = [
            parameter('Input CAD File', 'input_cad', 'DEFile'),
            parameter('CAD Layer', 'cad_layer', 'GPString'),
            parameter('Output Geodatabase', 'output_gdb', 'DEWorkspace')
        ]

    def getParameterInfo(self):
        """
        Return your parameter list defined in the __init__ method for the tool.
        If you want to set any additional proprieties, such as filters, for your
        parameters, do this here. Just reference them using their index in the
        parameter list
        """
        # make it so we can only dmg files are allowed
        self.parameters[0].filter.list = ['dwg']

        # only allow databases for target
        self.parameters[2].filter.list = ['Local Database', 'Remote Database']

        # disable layer parameter for now
        self.parameters[1].enabled = False

        # hand back parameters to ArcGIS
        return self.parameters

    def isLicensed(self):
        """
        Set whether tool is licensed to execute and replace this text with a
        good explanation of what you are doing here.
        """
        return True

    def updateParameters(self, parameters):
        """
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        """
        # if the dwg field has been populated or changed
        if parameters[0].value:
            if parameters[0].altered:

                # create a cad file object instance
                cad_file = CadFile(parameters[0].valueAsText)

                # populate picklist using list of layer names
                parameters[1].filter.list = cad_file.layer_names

                # enable the fields value
                parameters[1].enabled = True

        return

    def updateMessages(self, parameters):
        """
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.
        """
        return

    def execute(self, parameters, messages):
        """
        Reference the business logic captured in your object defined
        separately in the module, preferably above.
        """
        # populate parameters into cad file instance
        cad_file = CadFile(parameters[0].valueAsText)
        cad_layer = parameters[1].valueAsText
        output_gdb = parameters[2].valueAsText

        # execute tool
        cad_file.export_layer(cad_layer, output_gdb)

        return