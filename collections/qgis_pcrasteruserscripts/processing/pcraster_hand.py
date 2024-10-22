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
    uniqueid,
    nominal,
    lddcreate,
    subcatchment,
    areaminimum,
    report
)

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterCrs,
    QgsProcessingParameterRasterDestination)

#from pcraster_tools.processing.algorithm import PCRasterAlgorithm

class PCRasterHandAlgorithm(QgsProcessingAlgorithm):
    INPUT_DEM = 'INPUT1'
    INPUT_DRAINAGE = 'INPUT2'
    OUTPUT_RASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterHandAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'hand'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Height Above Nearest Drainage')

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
            """Calculates Height Above Nearest Drainage (HAND)
          
          
            Parameters:
            
            * <b>Input DEM layer</b> (required) - scalar raster layer
            * <b>Input drainage layer</b> (required) - boolean raster layer
            * <b>Output HAND layer</b> (required) - Output layer with Height Above the Nearest Drainage
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DEM,
                self.tr('DEM layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DRAINAGE,
                self.tr('Drainage layer')
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RASTER,
                self.tr("Output HAND raster layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        input_drainage = self.parameterAsRasterLayer(parameters, self.INPUT_DRAINAGE, context)

        setclone(input_dem.dataProvider().dataSourceUri())
        DEM = readmap(input_dem.dataProvider().dataSourceUri())
        drainage = readmap(input_drainage.dataProvider().dataSourceUri())
        flowdir = lddcreate(DEM,1e31,1e31,1e31,1e31)
        drainageID = nominal(uniqueid(drainage))
        catchments = subcatchment(flowdir,drainageID)
        drainageZ = areaminimum(DEM,catchments)
        hand = DEM - drainageZ
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)
        report(hand,outputFilePath)
        results = {}
        results[self.OUTPUT_RASTER] = outputFilePath

        return results
