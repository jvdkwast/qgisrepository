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


class PCRasterComparisonOperatorsAlgorithm(QgsProcessingAlgorithm):
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

    INPUT1 = 'INPUT'
    INPUT_OPERATOR = 'INPUT1'
    INPUT2 = 'INPUT2'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterComparisonOperatorsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'comparisonoperators'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('comparison operators')

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
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/secfunclist.html#comparison-operators">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input raster layer</b> (required) - raster layer of any data type
            * <b>Comparison operator</b> (required) - ==,>,>=,<,<=,!=
            * <b>Input raster layer</b> (required) - raster layer of same data type as first input raster layer
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
                self.INPUT1,
                self.tr('Input raster')
            )
        )
        
        self.unitoption = [self.tr('=='),self.tr('>='),self.tr('>'),self.tr('<='),self.tr('<'),self.tr('!=')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_OPERATOR,
                self.tr('Comparison operator'),
                self.unitoption,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT2,
                self.tr('Input raster')
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

        input1 = self.parameterAsRasterLayer(parameters, self.INPUT1, context)
        input2 = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        comparisonoperator = self.parameterAsEnum(parameters, self.INPUT_OPERATOR, context)
        setclone(input1.dataProvider().dataSourceUri())
        Expression1 = readmap(input1.dataProvider().dataSourceUri())
        Expression2 = readmap(input2.dataProvider().dataSourceUri())
        if comparisonoperator == 0:
            ResultComparison = Expression1 == Expression2
        elif comparisonoperator == 1:
            ResultComparison = Expression1 >= Expression2
        elif comparisonoperator == 2:
            ResultComparison = Expression1 > Expression2
        elif comparisonoperator == 3:
            ResultComparison = Expression1 <= Expression2
        elif comparisonoperator == 4:
            ResultComparison = Expression1 < Expression2
        else:
            ResultComparison = Expression1 != Expression2

        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        report(ResultComparison,outputFilePath)

        results = {}
        results[self.OUTPUT] = outputFilePath
        
        return results
