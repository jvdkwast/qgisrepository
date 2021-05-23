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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber)
from qgis import processing
from pcraster import *


class PCRasterInversedistanceAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_MASK = 'INPUT'
    INPUT_UNITS = 'INPUT1'
    INPUT_POINTS = 'INPUT2'
    INPUT_IDP = 'INPUT3'
    INPUT_RADIUS = 'INPUT4'
    INPUT_MAXNR = 'INPUT5'
    OUTPUT_INVERSEDISTANCE = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PCRasterInversedistanceAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'inversedistance'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('inversedistance')

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
            """Interpolate values using inverse distance weighting
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_inversedistance.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input mask raster layer</b> (required) - boolean raster layer with mask
            * <b>Raster layer with values to be interpolated</b> (required) - scalar raster layer
            * <b>Power</b> (required) - power of the weight function (default 2)
            * <b>Units</b> (required) - unit of radius in map units or cells
            * <b>Radius</b> (required) - select only the points at a distance less or equal to the cell. Default 0 includes all points.
            * <b>Maximum number of closest points</b> (required) - the maximum number of points used in the computation. Default 0 includes all points.
            * <b>Inverse Distance Interpolation output</b> (required) - Scalar raster with interpolation result.
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_MASK,
                self.tr('Mask layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_POINTS,
                self.tr('Raster layer with values to be interpolated')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_IDP,
                self.tr('Power'),
                defaultValue=2
            )
        )

        self.unitoption = [self.tr('Map units'),self.tr('Cells')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_UNITS,
                self.tr('Units'),
                self.unitoption,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_RADIUS,
                self.tr('Radius'),
                defaultValue=0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_MAXNR,
                self.tr('Maximum number of closest points'),
                defaultValue=0
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_INVERSEDISTANCE,
                self.tr('Inverse Distance Interpolation output')
            )
        )
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_mask = self.parameterAsRasterLayer(parameters, self.INPUT_MASK, context)
        input_points = self.parameterAsRasterLayer(parameters, self.INPUT_POINTS, context)
        input_idp = self.parameterAsDouble(parameters, self.INPUT_IDP, context)
        lengthunits = self.parameterAsEnum(parameters, self.INPUT_UNITS, context)
        if lengthunits == 0:
            setglobaloption("unittrue")
        else:
            setglobaloption("unitcell")
        input_radius = self.parameterAsDouble(parameters, self.INPUT_RADIUS, context)
        input_maxnr = self.parameterAsDouble(parameters, self.INPUT_MAXNR, context)
        output_idw = self.parameterAsRasterLayer(parameters, self.OUTPUT_INVERSEDISTANCE, context)
        setclone(input_mask.dataProvider().dataSourceUri())
        MaskLayer = readmap(input_mask.dataProvider().dataSourceUri())
        PointsLayer = readmap(input_points.dataProvider().dataSourceUri())
        IDW = inversedistance(MaskLayer,PointsLayer,input_idp,input_radius,input_maxnr)
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_INVERSEDISTANCE, context)
        report(IDW,outputFilePath)

        results = {}
        results[self.OUTPUT_INVERSEDISTANCE] = outputFilePath
        
        return results
