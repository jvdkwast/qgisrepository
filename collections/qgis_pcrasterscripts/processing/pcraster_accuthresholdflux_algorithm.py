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
                       QgsProcessingParameterRasterLayer)
from qgis import processing
from pcraster import *


class PCRasterAccuthresholdfluxAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_FLOWDIRECTION = 'INPUT'
    INPUT_MATERIAL = 'INPUT2'
    INPUT_THRESHOLD = 'INPUT3'
    OUTPUT_FLUX = 'OUTPUT'
    OUTPUT_STATE = 'OUTPUT2'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterAccuthresholdfluxAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'accuthresholdflux'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('accuthresholdflux and accuthresholdstate')

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
            """Input of material downstream over a local drain direction network when transport threshold is exceeded
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_accuthreshold.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input flow direction raster</b> (required) - Flow direction in PCRaster LDD format (see lddcreate)
            * <b>Input material raster</b> (required) - Scalar raster with amount of material input (>= 0)
            * <b>Input transport threshold raster</b> (required) - Scalar raster with transport threshold values (>= 0)
            * <b>Output Flux raster</b> (required) - Scalar raster with result flux of material
            * <b>Output State raster</b> (required) - Scalar raster with result state of stored material
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_FLOWDIRECTION,
                self.tr('Input Flow Direction Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_MATERIAL,
                self.tr('Input Material Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_THRESHOLD,
                self.tr('Input Transport Threshold Raster Layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_FLUX,
                self.tr('Output Material Flux Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_STATE,
                self.tr('Output State Raster Layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_flowdirection = self.parameterAsRasterLayer(parameters, self.INPUT_FLOWDIRECTION, context)
        input_material = self.parameterAsRasterLayer(parameters, self.INPUT_MATERIAL, context)
        input_threshold = self.parameterAsRasterLayer(parameters, self.INPUT_THRESHOLD, context)
        output_flux = self.parameterAsRasterLayer(parameters, self.OUTPUT_FLUX, context)
        output_state = self.parameterAsRasterLayer(parameters, self.OUTPUT_STATE, context)
        setclone(input_flowdirection.dataProvider().dataSourceUri())
        LDD = readmap(input_flowdirection.dataProvider().dataSourceUri())
        material = readmap(input_material.dataProvider().dataSourceUri())
        transportthreshold = readmap(input_threshold.dataProvider().dataSourceUri())
        resultflux = accuthresholdflux(LDD, material, transportthreshold)
        resultstate = accuthresholdstate(LDD, material, transportthreshold)
        
        outputFlux = self.parameterAsOutputLayer(parameters, self.OUTPUT_FLUX, context)
        outputState = self.parameterAsOutputLayer(parameters, self.OUTPUT_STATE, context)

        report(resultflux,outputFlux)
        report(resultstate,outputState)

        results = {}
        results[self.OUTPUT_FLUX] = outputFlux
        results[self.OUTPUT_STATE] = outputState
        
        
        return results
