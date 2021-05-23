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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer)
from qgis import processing
from pcraster import *


class PCRasterTransientAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_ELEVATION = 'INPUT'
    INPUT_RECHARGE = 'INPUT2'
    INPUT_TRANSMISSIVITY = 'INPUT3'
    INPUT_FLOWCONDITION = 'INPUT4'
    INPUT_STORAGE = 'INPUT5'
    INPUT_TIMESTEP = 'INPUT6'
    INPUT_TOLERANCE = 'INPUT7'
    OUTPUT_TRANSIENT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterTransientAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'transient'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('transient')

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
            """Simulates transient groundwater flow according to the implicit finite difference method.
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_transient.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input elevation raster</b> (required) - Scalar elevation raster
            * <b>Input recharge raster</b> (required) - Scalar raster with recharge [L T-1]
            * <b>Input transmissivity raster</b> (required) - Scalar raster transmissivity [L2 T-1]
            * <b>Input flow condition raster</b> (required) - Nominal raster with values for inactive (0), active (1) or constant head (2)
            * <b>Input storage coefficient raster</b> (required) - Scalar raster with storage coefficient [L3/L3]
            * <b>Input time step value</b> (required) - Time step [T]
            * <b>Input tolerance value</b> (required) - Value specifies the maximum difference between the current elevation and the new elevation
            * <b>Output transient raster</b> (required) - Scalar raster with result
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_ELEVATION,
                self.tr('Input Elevation Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RECHARGE,
                self.tr('Input Recharge Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_TRANSMISSIVITY,
                self.tr('Input Transmissivity Raster Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_FLOWCONDITION,
                self.tr('Input Flow Condition Raster Layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_STORAGE,
                self.tr('Storage coefficient'),
                defaultValue=0.5
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_TIMESTEP,
                self.tr('Time step'),
                defaultValue=10
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_TOLERANCE,
                self.tr('Tolerance'),
                defaultValue=10
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_TRANSIENT,
                self.tr('Output Transient Raster Layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_elevation = self.parameterAsRasterLayer(parameters, self.INPUT_ELEVATION, context)
        input_recharge = self.parameterAsRasterLayer(parameters, self.INPUT_RECHARGE, context)
        input_transmissivity = self.parameterAsRasterLayer(parameters, self.INPUT_TRANSMISSIVITY, context)
        input_flowcondition = self.parameterAsRasterLayer(parameters, self.INPUT_FLOWCONDITION, context)
        input_storage = self.parameterAsRasterLayer(parameters, self.INPUT_STORAGE, context)
        timestep = self.parameterAsDouble(parameters, self.INPUT_TIMESTEP, context)
        tolerance = self.parameterAsDouble(parameters, self.INPUT_TOLERANCE, context)
        output_transient = self.parameterAsRasterLayer(parameters, self.OUTPUT_TRANSIENT, context)
        setclone(input_elevation.dataProvider().dataSourceUri())
        elevation = readmap(input_elevation.dataProvider().dataSourceUri())
        recharge = readmap(input_recharge.dataProvider().dataSourceUri())
        transmissivity = readmap(input_transmissivity.dataProvider().dataSourceUri())
        flowcondition = readmap(input_flowcondition.dataProvider().dataSourceUri())
        storage = readmap(input_storage.dataProvider().dataSourceUri())
        resulttransient = transient(elevation,recharge,transmissivity,flowcondition,storage,timestep,tolerance)
        
        outputTransient = self.parameterAsOutputLayer(parameters, self.OUTPUT_TRANSIENT, context)

        report(resulttransient,outputTransient)

        results = {}
        results[self.OUTPUT_TRANSIENT] = outputTransient
        
        return results
