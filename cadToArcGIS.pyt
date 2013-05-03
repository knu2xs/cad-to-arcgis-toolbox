'''
Name:        cadToArcGIS
Purpose:     Convert a single geometry CAD feature class to multiple feature
             classes in ArcGIS based on the Layer attribute field used in CAD
             to delineate different layers.

Author:      Joel McCune

Created:     02May2013
Copyright:   (c) Joel McCune 2013
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
'''

# import modules
import arcpy
import re
import os.path

class CadFc(object):
    '''
    The feature class in the dwg CAD file. This is a single simple geometry with
    the individual layers defined in the Layers field of the attribute table. This
    layers field will be used to determine the feature classes to be created in the
    designated workspace.
    '''
    def __init__(self, cadFcPath, outputWorkspace):
        self.path = cadFcPath
        self.layers = self._getLayers()
        self.outputWorkspace = outputWorkspace
        
    def _getLayers(self):
        '''
        Populate layer list by collecting all unique value permutations from the
        Layer attribute field.
        '''
        # set object does not allow duplicates, so used to collect field values
        layers = set()
        layerObjs = []
        
        # use search cursor object to iterate through every record and get Layer name
        with arcpy.da.SearchCursor(self.path, 'Layer') as cursor:
            for row in cursor:
                layers.add(row[0])
                
        # sort layers alphabetically
        layers = sorted(layers)
        
        # create layer object for each layer
        for layer in layers:
            layerObjs.append(Layer(layer, self.path))
            
        # return the layer objects
        return layerObjs
    
    def outputToWorkspace(self):
        '''
        Create a separate feature class for each layer in the input CAD file.
        '''
        for layer in self.layers:
            try:
                layer.outputToFc(self.outputWorkspace)
            except:
                pass
        
    
class Layer(object):
    '''
    Each CAD layer has a source feature class, an output feature class name and an
    SQL query string used to select it from the CAD feature class.
    '''
    
    def __init__(self, layer, cadFile):
        self.cadFile = cadFile
        self.layerName = layer
        self.outputName = self._createOutputName()
        self.sqlQuery = self._createSqlQuery()
    
    def _createOutputName(self):
        '''
        Create the output name, taking into account dashes are not allowed in feature
        class names.
        '''
        # use regular expression matching to replace dashes with underscores
        regex = re.compile('-')
        return regex.sub('_', self.layerName)
    
    def _createSqlQuery(self):
        '''
        Create the SQL query string to be used to select the layer from the CAD file.
        '''
        # escape possible single quotes creating problems
        regex = re.compile("'")
        nameStr = regex.sub("''", self.layerName)
        
        # create sql string and return
        sqlQuery = ('"Layer" = \'{0}\'').format(nameStr)
        return sqlQuery
    
    def outputToFc(self, workspace):
        '''
        Create an output feature class for the source layer from the CAD file.
        '''
        arcpy.Select_analysis(self.cadFile, os.path.join(workspace, self.outputName), 
                              self.sqlQuery)

def parameter(displayName, name, datatype, defaultValue=None,
    parameterType=None, direction=None):
    '''
    The parameter implementation makes it a little difficult to quickly
    create parameters with defaults. This method prepopulates the paramaeterType
    and direction parameters and leaves the setting a default value for the
    newly created parameter as optional. The displayName, name and datatype are
    the only required inputs.
    '''
    # create parameter with a few defaults
    param = arcpy.Parameter(
        displayName = displayName,
        name = name,
        datatype = datatype,
        parameterType = 'Required',
        direction = 'Input')

    # set new parameter to a default value
    param.value = defaultValue

    # return the complete parameter object
    return param

class Toolbox(object):
    def __init__(self):
        '''
        Define the toolbox properties here. Do not change the name of this
        class. ArcGIS locates this class by name. It will not be able to find
        the toolbox and your toolbox will not work if you modify this.
        '''
        self.label = 'CadConversion'
        self.alias = 'CAD Conversion'

        # List of tool classes associated with this toolbox
        self.tools = [cadToArcGIS]


class cadToArcGIS(object):
    '''
    Calls the above business logic to convert a single CAD feature class into
    multiple ArcGIS feature classes based on the layers defined by CAD in the
    Layer attribute field.
    '''
    def __init__(self):
        self.label = 'CAD FC to ArcGIS Workspace'
        self.canRunInBackground = False

        self.parameters = [
            parameter('Input CAD Feature Class', 'inputCad', 'DEFeatureClass'),
            parameter('Output Workspace', 'outputWksp', 'DEWorkspace')
        ]

    def getParameterInfo(self):
        '''
        Return your parameter list defined in the __init__ method for the tool.
        If you want to set any additional properties, such as filters, for your
        parameters, do this here. Just reference them using their index in the
        parameter list'''

        # self.param[0].filter.list = ['Option1', 'Option2', 'Option3']
        # self.param[1].filter.list = ['xml'] # only xml files for DEFile

        return self.parameters

    def isLicensed(self):
        '''
        Set whether tool is licensed to execute and replace this text with a
        good explanation of what you are doing here.
        '''
        return True

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        return

    def updateMessages(self, parameters):
        '''
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.
        '''
        return

    def execute(self, parameters, messages):
        '''
        Create an instance of the CadFc object. It will load the layers and set their
        properties. Once loaded, export them to the workspace as individual feature
        classes.
        '''
        cadFeatureClass = CadFc(parameters[0].valueAsText, parameters[1].valueAsText)
        cadFeatureClass.outputToWorkspace()
        return