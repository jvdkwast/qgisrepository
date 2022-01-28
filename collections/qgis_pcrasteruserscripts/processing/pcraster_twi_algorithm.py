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

from pcraster import (
    readmap,
    setclone,
    cellarea,
    slope,
    lddcreate,
    accuflux,
    ln,
    tan,
    report
)

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterCrs,
    QgsProcessingParameterRasterDestination)

#from pcraster_tools.processing.algorithm import PCRasterAlgorithm

class TwiAlgorithm(QgsProcessingAlgorithm):
    INPUT_RASTER = 'INPUT'
    OUTPUT_RASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TwiAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'twi'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Topographic Wetness Index')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('PCRaster User Scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pcrasteruser'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """Calculates the Topographic Wetness Index (TWI) from a DTM
          
          
            Parameters:
            
            * <b>Input DTM</b> (required) - scalar raster layer
            * <b>Output TWI</b> (required) - Scalar raster with result
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr('DTM layer')
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RASTER,
                self.tr("Output TWI layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        output_raster = self.parameterAsRasterLayer(parameters, self.OUTPUT_RASTER, context)
        setclone(input_raster.dataProvider().dataSourceUri())
        DTM = readmap(input_raster.dataProvider().dataSourceUri())
        # Calculate Slope
        SlopeFraction = slope(DTM)
        SlopePercentage = SlopeFraction * 100
        SlopeRadians = SlopePercentage * 0.062831853071796
        
        # Calculate Flow Accumulation
        LDD = lddcreate(DTM,1E31,1E31,1E31,1E31)
        FlowAccumulation = accuflux(LDD,1)
        
        # Calculate TWI
        TWI = ln((FlowAccumulation * cellarea())/tan(SlopeRadians))

        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)

        report(TWI,outputFilePath)
        
#        self.set_output_crs(output_file=outputFilePath, crs=input_raster.crs(), feedback=feedback, context=context)

        return {self.OUTPUT_RASTER: outputFilePath}
