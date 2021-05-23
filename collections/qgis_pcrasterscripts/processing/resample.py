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
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterDestination
                       )
from qgis import processing
from osgeo import gdal, gdalconst
import os,sys


class ResampleAlgorithm(QgsProcessingAlgorithm):
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
    INPUT_MASK = 'INPUT1'
    OUTPUT_PCRASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ResampleAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'resample'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('resample')

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
        return self.tr('pcraster')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """Cuts one map or joins together several maps by resampling to the cells of the result map.
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/app_resample.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input Raster layers</b> (required) - raster layers from any data type (all must have the same data type). When one layer is used, it will be resampled to the raster properties of the mask layer. When multiple layers are used, they will also be mosaiced into a raster with the dimensions of the mask layer.
            * <b>Input Mask</b> (required) - clone map that will be used to determine the output raster properties
            * <b>Output raster layer</b> (required) - raster layer with resample result
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
            QgsProcessingParameterRasterLayer(
                self.INPUT_MASK,
                self.tr('Raster mask layer')
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_PCRASTER,
                self.tr('Output resample raster layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        input_rasters = []
        for l in self.parameterAsLayerList(parameters, self.INPUT_RASTERS, context):
            input_rasters.append(l.source())
        input_mask = self.parameterAsRasterLayer(parameters, self.INPUT_MASK, context)
        clone = input_mask.dataProvider().dataSourceUri()
    
        dst_filename = self.parameterAsOutputLayer(parameters, self.OUTPUT_PCRASTER, context)
        rasterstrings = " ".join(input_rasters)
        cmd = "resample {} {} --clone {}".format(rasterstrings,dst_filename,clone)
        os.system(cmd)
        results = {}
        results[self.OUTPUT_PCRASTER] = dst_filename
        
        return results
