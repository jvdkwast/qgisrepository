# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsDataSourceUri,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterMultipleLayers)
from qgis import processing
from pcraster import *


class PCRasterLookupAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_RASTERS = 'INPUT'
    INPUT_TABLE = 'INPUT1'
    INPUT_DATATYPE = 'INPUT2'
    OUTPUT_RASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterLookupAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lookup'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('lookup')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('PCRaster')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pcraster'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """Compares cell value(s) of one or more expression(s) with the search key in a table
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_lookup.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input Raster layer(s)</b> (required) - rasters layer from any data type
            * <b>Input lookup table</b> (required) - lookup table in ASCII text format. Nr of columns is number of input rasters plus one.
            * <b>Output data type</b> (required) - data type of output raster
            * <b>Output raster layer</b> (required) - raster layer with result of the lookup in output data type
            
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """


        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                self.tr('Input Raster Layer(s)'),
                QgsProcessing.TypeRaster
           )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_TABLE,
                self.tr('Input lookup table')
            )
        )
        
        self.datatypes = [self.tr('Boolean'),self.tr('Nominal'),self.tr('Ordinal'),self.tr('Scalar'),self.tr('Directional'),self.tr('LDD')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_DATATYPE,
                self.tr('Output data type'),
                self.datatypes,
                defaultValue=0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RASTER,
                self.tr('Output Raster Layer')
            )
        )
                
    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_rasters = []
        for l in self.parameterAsLayerList(parameters, self.INPUT_RASTERS, context):
            input_rasters.append(l.source())
        input_lookuptable = self.parameterAsFile(parameters, self.INPUT_TABLE, context)
        output_raster = self.parameterAsRasterLayer(parameters, self.OUTPUT_RASTER, context)
        setclone(input_rasters[0])
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)

        input_datatype = self.parameterAsEnum(parameters, self.INPUT_DATATYPE, context)
        if input_datatype == 0:
            Result = lookupboolean(input_lookuptable,*input_rasters)
        elif input_datatype == 1:
            Result = lookupnominal(input_lookuptable,*input_rasters)
        elif input_datatype == 2:
            Result = lookupordinal(input_lookuptable,*input_rasters)
        elif input_datatype == 3:
            Result = lookupscalar(input_lookuptable,*input_rasters)
        elif input_datatype == 4:
            Result = lookupdirectional(input_lookuptable,*input_rasters)
        else:
            Result = lookupldd(input_lookuptable,*input_rasters)
        
        report(Result,outputFilePath)

        results = {}
        results[self.OUTPUT_RASTER] = outputFilePath
        
        return results
