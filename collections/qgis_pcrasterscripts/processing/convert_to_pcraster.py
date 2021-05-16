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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterDestination
                       )
from qgis import processing
from osgeo import gdal, gdalconst


class ConvertToPCRasterAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_RASTER = 'INPUT'
    INPUT_DATATYPE = 'INPUT2'
    OUTPUT_PCRASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConvertToPCRasterAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'converttopcrasterformat'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert to PCRaster Format')

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
        return self.tr("Convert GDAL supported raster layers to PCRaster format with control of the output data type")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr('Raster layer')
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

 # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_PCRASTER,
                self.tr('PCRaster layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        #print(input_dem.dataProvider().dataSourceUri())

        #Open existing dataset
        src_ds = gdal.Open( input_raster.dataProvider().dataSourceUri() )
    
    	#GDAL Translate
        dst_filename = self.parameterAsOutputLayer(parameters, self.OUTPUT_PCRASTER, context)
        
        input_datatype = self.parameterAsEnum(parameters, self.INPUT_DATATYPE, context)
        if input_datatype == 0:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Byte, metadataOptions="VS_BOOLEAN")
        elif input_datatype == 1:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Int32, metadataOptions="VS_NOMINAL")
        elif input_datatype == 2:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Int32, metadataOptions="VS_ORDINAL")
        elif input_datatype == 3:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Float32, metadataOptions="VS_SCALAR")
        elif input_datatype == 4:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Float32, metadataOptions="VS_DIRECTION")
        else:
            dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=gdalconst.GDT_Byte, metadataOptions="VS_LDD")
    
    	#Properly close the datasets to flush to disk
        dst_ds = None
        src_ds = None

        results = {}
        results[self.OUTPUT_PCRASTER] = dst_filename
        
        return results
