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
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterDestination
                       )
from qgis import processing
from osgeo import gdal, gdalconst
import os,sys


class Col2mapAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_CSV = 'INPUT'
    INPUT_MASK = 'INPUT1'
    INPUT_DATATYPE = 'INPUT2'
    OUTPUT_PCRASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Col2mapAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'col2map'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Column file to PCRaster Map')

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
        """
        Convert CSV files to PCRaster format with control of the output data type. The algorithm uses <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/app_col2map.html">col2map</a>
        """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_CSV,
                self.tr('Input column table text file')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_MASK,
                self.tr('Raster mask layer')
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

        input_mask = self.parameterAsRasterLayer(parameters, self.INPUT_MASK, context)
        clone = input_mask.dataProvider().dataSourceUri()
        #print(input_dem.dataProvider().dataSourceUri())

        table = self.parameterAsFile(parameters, self.INPUT_CSV, context)
    
        dst_filename = self.parameterAsOutputLayer(parameters, self.OUTPUT_PCRASTER, context)
        
        input_datatype = self.parameterAsEnum(parameters, self.INPUT_DATATYPE, context)
        if input_datatype == 0:
            cmd = "col2map -B {} {} --clone {}".format(table, dst_filename,clone)
            feedback.pushInfo('Running command {}'.format(cmd))
        elif input_datatype == 1:
            cmd = "col2map -N {} {} --clone {}".format(table, dst_filename,clone)
        elif input_datatype == 2:
            cmd = "col2map -O {} {} --clone {}".format(table, dst_filename,clone)
        elif input_datatype == 3:
            cmd = "col2map -S {} {} --clone {}".format(table, dst_filename,clone)
        elif input_datatype == 4:
            cmd = "col2map -D {} {} --clone {}".format(table, dst_filename,clone)
        else:
            cmd = "col2map -L {} {} --clone {}".format(table, dst_filename,clone)
    
        os.system(cmd)
        results = {}
        results[self.OUTPUT_PCRASTER] = dst_filename
        
        return results
