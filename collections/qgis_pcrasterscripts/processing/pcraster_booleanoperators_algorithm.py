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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer)
from qgis import processing
from pcraster import *


class PCRasterBooleanOperatorsAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_BOOLEAN1 = 'INPUT'
    INPUT_OPERATOR = 'INPUT1'
    INPUT_BOOLEAN2 = 'INPUT2'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterBooleanOperatorsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'booleanoperators'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('boolean operators')

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
            """Boolean operators
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/secfunclist.html#boolean-operators">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input boolean raster layer</b> (required) - boolean raster layer
            * <b>Boolean operator</b> (required) - AND, OR, XOR, NOT
            * <b>Input boolean raster layer</b> (required) - boolean raster layer
            * <b>Output raster</b> (required) - boolean raster layer
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_BOOLEAN1,
                self.tr('Input Boolean raster')
            )
        )
        
        self.unitoption = [self.tr('AND'),self.tr('NOT'),self.tr('OR'),self.tr('XOR')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_OPERATOR,
                self.tr('Boolean operator'),
                self.unitoption,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_BOOLEAN2,
                self.tr('Input Boolean raster')
            )
        )

        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Output Boolean raster')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_boolean1 = self.parameterAsRasterLayer(parameters, self.INPUT_BOOLEAN1, context)
        input_boolean2 = self.parameterAsRasterLayer(parameters, self.INPUT_BOOLEAN2, context)
        booleanoperator = self.parameterAsEnum(parameters, self.INPUT_OPERATOR, context)
        setclone(input_boolean1.dataProvider().dataSourceUri())
        Expression1 = readmap(input_boolean1.dataProvider().dataSourceUri())
        Expression2 = readmap(input_boolean2.dataProvider().dataSourceUri())
        if booleanoperator == 0:
            ResultBoolean = pcrand(Expression1,Expression2)
        elif booleanoperator == 1:
            ResultBoolean = pcrnot(Expression1,Expression2)
        elif booleanoperator == 2:
            ResultBoolean = pcror(Expression1,Expression2)
        else:
            ResultBoolean = pcrxor(Expression1,Expression2)

        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        report(ResultBoolean,outputFilePath)

        results = {}
        results[self.OUTPUT] = outputFilePath
        
        return results
