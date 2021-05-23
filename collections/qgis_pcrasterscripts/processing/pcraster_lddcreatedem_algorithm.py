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
    INPUT_UNITS = 'INPUT1'
    INPUT_EDGE = 'INPUT0'
    INPUT_ELEVATION = 'INPUT6'
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
        return self.tr(
            """Modified digital elevation model
            
            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_lddcreatedem.html">PCRaster documentation</a>
            
            Parameters:
            
            * <b>Input DEM layer</b> (required) - scalar raster layer
            * <b>Remove pits at edge</b> (required) - no/yes
            * <b>Assignment of elevation in pits</b> (required) - fill or cut
            * <b>Units</b> (required) - map units or cells
            * <b>Outflow depth value</b> (required) - outflow depth
            * <b>Core volume value</b> (required) - core volume
            * <b>Core area value</b> (required) - core area
            * <b>Catchment precipitation</b> (required) - catchment precipitation
            * <b>Local drain direction layer output</b> (required) - raster with local drain direction (ldd data type)
            """
        )

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

        self.unitoption = [self.tr('No'),self.tr('Yes')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_EDGE,
                self.tr('Remove pits at edge?'),
                self.unitoption,
                defaultValue=0
            )
        )

        self.unitoption = [self.tr('Fill'),self.tr('Cut')]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_ELEVATION,
                self.tr('Assignment of elevation in pits'),
                self.unitoption,
                defaultValue=0
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
        elevationsetting = self.parameterAsEnum(parameters, self.INPUT_ELEVATION, context)
        if elevationsetting == 0:
            setglobaloption("lddfill")
        else:
            setglobaloption("lddcut")
        edgesetting = self.parameterAsEnum(parameters, self.INPUT_EDGE, context)
        if edgesetting == 0:
            setglobaloption("lddout")
        else:
            setglobaloption("lddin")
        lengthunits = self.parameterAsEnum(parameters, self.INPUT_UNITS, context)
        if lengthunits == 0:
            setglobaloption("unittrue")
        else:
            setglobaloption("unitcell")
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
        results[self.OUTPUT_DEMFILLED] = outputFilePath
        
        return results
