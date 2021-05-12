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
                       QgsProcessingParameterNumber)
from qgis import processing
from pcraster import *


class PCRasterLDDCreateDEMAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_DEM = 'INPUT'
    INPUT_OUTFLOWDEPTH = 'INPUT2'
    INPUT_COREVOLUME = 'INPUT3'
    INPUT_COREAREA = 'INPUT4'
    INPUT_PRECIPITATION = 'INPUT5'
    OUTPUT_DEMFILLED = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterLDDCreateDEMAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lddcreatedem'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('lddcreatedem')

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
        return self.tr("Modified digital elevation model where sinks are filled")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input DEM.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DEM,
                self.tr('DEM layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_OUTFLOWDEPTH,
                self.tr('Outflow depth (map units)'),
                defaultValue=9999999
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_COREAREA,
                self.tr('Core area (map units)'),
                defaultValue=9999999
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_COREVOLUME,
                self.tr('Core volume (map units)'),
                defaultValue=9999999
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_PRECIPITATION,
                self.tr('Catchment precipitation (map units)'),
                defaultValue=9999999
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DEMFILLED,
                self.tr('Filled DEM')
            )
        )
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        input_outflowdepth = self.parameterAsDouble(parameters, self.INPUT_OUTFLOWDEPTH, context)
        input_corearea = self.parameterAsDouble(parameters, self.INPUT_COREAREA, context)
        input_corevolume = self.parameterAsDouble(parameters, self.INPUT_COREVOLUME, context)
        input_precipitation = self.parameterAsDouble(parameters, self.INPUT_PRECIPITATION, context)
        output_demfilled = self.parameterAsRasterLayer(parameters, self.OUTPUT_DEMFILLED, context)
        setclone(input_dem.dataProvider().dataSourceUri())
        DEM = readmap(input_dem.dataProvider().dataSourceUri())
        DEMFilled = lddcreatedem(DEM, input_outflowdepth, input_corearea, input_corevolume, input_precipitation)
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_DEMFILLED, context)
        report(DEMFilled,outputFilePath)

        results = {}
        results[self.OUTPUT_DEMFILLED] = output_demfilled
        
        return results
