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

from pcraster import *
from pcraster.framework import *
import runoff

from console import console

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsDataSourceUri,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber)

class runoffModelAlgorithm(QgsProcessingAlgorithm):
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

    INPUT_CLONE = 'INPUT1'
    INPUT_LAST = 'INPUT2'
    INPUT_FIRST = 'INPUT3'
    INPUT_RAINSTAT = 'INPUT4'
    INPUT_INFTAB = 'INPUT5'
    INPUT_SOIL = 'INPUT6'
    INPUT_DEM = 'INPUT7'
    INPUT_RAINTSS = 'INPUT9'
    OUTPUT_RAINSTACK = 'OUTPUT2'
    OUTPUT_RUNOFF = 'OUTPUT3'


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return runoffModelAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'runoffmodel'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Example Runoff Model')

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
            """Runoff model provided with <a href="https://pcraster.geo.uu.nl/downloads/demo-data/">PCRaster demo data</a>
            Results will be displayed as an animation in with <a href="https://pcraster.geo.uu.nl/pcraster/4.3.3/documentation/pcraster_aguila/QuickStart.html">Aguila</a>
            
            Parameters:
            
            * <b>Input clone layer</b> (required) - raster layer
            * <b>Input raster with rain gauges</b> (required) - nominal raster layer
            * <b>Input rainfall time series</b> (required) - rainfall table in PCRaster TSS format
            * <b>Input lookup table with infiltration capacity</b> (required) - table in PCRaster column format
            * <b>Input soil raster</b> (required) - nominal raster with soil classes 
            * <b>Input Digital Elevation Model</b> (required) - scalar DEM raster
            * <b>Last time step</b> (required) - number of last time step (integer)
            * <b>First time step</b> (required) - number of first time step (integer)
            * <b>Output rain mapstack</b> (required) - PCRaster mapstack format, e.g. Z:/path/p
            * <b>Output runoff mapstack</b> (required) - PCRaster mapstack format, e.g. Z:/path/q
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_CLONE,
                self.tr('Clone layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RAINSTAT,
                self.tr('Raster with rain gauges')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_RAINTSS,
                self.tr('Rainfall timeseries file')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_INFTAB,
                self.tr('Lookup table with infiltration capacity')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_SOIL,
                self.tr('Soil raster')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DEM,
                self.tr('Digital Elevation Model')
            )
        )
        
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_LAST,
                self.tr('Last time step'),
                defaultValue=10
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_FIRST,
                self.tr('First time step'),
                defaultValue=1
            )
        )
              
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_RAINSTACK,
                self.tr('Output rain mapstack')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_RUNOFF,
                self.tr('Output runoff mapstack')
            )
        )
        
        
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_clone = self.parameterAsRasterLayer(parameters, self.INPUT_CLONE, context)
        input_last = self.parameterAsInt(parameters, self.INPUT_LAST, context)
        input_first = self.parameterAsInt(parameters, self.INPUT_FIRST, context)
        input_rainstat = self.parameterAsRasterLayer(parameters, self.INPUT_RAINSTAT, context)
        input_inftab = self.parameterAsString(parameters, self.INPUT_INFTAB, context)
        input_soil = self.parameterAsRasterLayer(parameters, self.INPUT_SOIL, context)
        input_DEM = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        input_raintss = self.parameterAsString(parameters, self.INPUT_RAINTSS, context)
        
        output_rainstack = self.parameterAsString(parameters, self.OUTPUT_RAINSTACK, context)
        output_runoff = self.parameterAsString(parameters, self.OUTPUT_RUNOFF, context)
        
        clone = input_clone.dataProvider().dataSourceUri()
        rainstat = input_rainstat.dataProvider().dataSourceUri()
        inftab = input_inftab
        soil = input_soil.dataProvider().dataSourceUri()
        DEM = input_DEM.dataProvider().dataSourceUri()
        raintss = input_raintss
        
        rainstack = output_rainstack
        runoffstack = output_runoff
        
        myModel = runoff.RunoffModel(clone,rainstat,inftab,soil,DEM,raintss,rainstack,runoffstack)
        dynModelFw = DynamicFramework(myModel,lastTimeStep = input_last,firstTimestep = input_first)
        console.show_console()
        dynModelFw.run()
        
        cmd = 'aguila --timesteps [{},{}] {} {}'.format(input_first,input_last,rainstack,runoffstack)
        feedback.pushInfo('Running command {}'.format(cmd))
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)
        
        cmd = 'aguila --timesteps [{},{}] -3 {} + {}'.format(input_first,input_last,DEM,runoffstack)
        feedback.pushInfo('Running command {}'.format(cmd))
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)

        results = {}
        
        return results
