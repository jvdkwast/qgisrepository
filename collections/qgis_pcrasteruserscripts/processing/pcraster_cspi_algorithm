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
    scalar,
    lddcreate,
    accuflux,
    report
)
#from math import pi
#from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
#from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterCrs,
    QgsProcessingParameterRasterDestination)

#from pcraster_tools.processing.algorithm import PCRasterAlgorithm   

class cspiAlgorithm(QgsProcessingAlgorithm):
    INPUT_DEM = 'INPUT1'
    INPUT_URBAN_RASTER = 'INPUT2'
    URBAN_PIXEL_AREA  = 'PIXELAREA'
    INFILTRATION_COEFFICIENT_URBANIZED_AREA = 'URBANCOEFFICIENT'
    INFILTRATION_COEFFICIENT_NONURBANIZED_AREA = 'NONURBANCOEFFICIENT'
    INPUT_SPI_RASTER = 'INPUT3'
    OUTPUT_RASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return cspiAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'correctedstreampowerindex'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Corrected Stream Power Index (CSPI)')

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
            """ Stream power is a measure that captures the force of surface flows and is commonly used to indicate susceptibility to land erosion. 
           Corrected Stream Power Index calculates the stream power by including the impact of urbanization
          
          
            Parameters:
            
            * <b>Input DEM layer</b> (required) - scalar raster layer 
            * <b>Input urban raster layer</b> (required) - scalar urban footprint. 
            * <b>Raster pixel area (urban)</b> (required) - pixel size of input urban raster layer 
            * <b>Cu</b> (required) - infiltration coefficient of urbanized area (value ranges from 0-1)
            * <b>C</b> (required) - infiltration coefficient of nonurbanized area. This is usually the infiltration coefficient of the soil (value ranges from 0-1)
            * <b>Input SPI raster</b> (required) - scalar raster layer. It can be calculated using SPI tool from the PCRaster User Scripts.
            * <b>Output CSPI raster</b> (required) - Scalar raster with a result of corrected stream power index 
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
                self.INPUT_URBAN_RASTER,
                self.tr('Urban raster layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.URBAN_PIXEL_AREA,
                'Raster pixel area (urban)',
                defaultValue=900,
                minValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INFILTRATION_COEFFICIENT_URBANIZED_AREA,
                'Infiltration coefficient urbanized area (Cu)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1,
                minValue=0.1,
                maxValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INFILTRATION_COEFFICIENT_NONURBANIZED_AREA,
                'Infiltration coefficient nonurbanized area (C)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.2,
                minValue=0.1,
                maxValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_SPI_RASTER,
                self.tr('SPI layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RASTER,
                self.tr("Output CSPI raster layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        input_urban_raster = self.parameterAsRasterLayer(parameters, self.INPUT_URBAN_RASTER, context)
        input_urban_pixel_area = self.parameterAsInt(parameters, self.URBAN_PIXEL_AREA, context)
        input_infiltration_coefficient_urbanized_area = self.parameterAsDouble(parameters, self.INFILTRATION_COEFFICIENT_URBANIZED_AREA , context)
        input_infiltration_coefficient_nonurbanized_area = self.parameterAsDouble(parameters, self.INFILTRATION_COEFFICIENT_NONURBANIZED_AREA , context)
        input_spi_raster = self.parameterAsRasterLayer(parameters, self.INPUT_SPI_RASTER, context)
        output_raster = self.parameterAsRasterLayer(parameters, self.OUTPUT_RASTER, context)
        setclone(input_dem.dataProvider().dataSourceUri())
        
        INPUTDEM = readmap(input_dem.dataProvider().dataSourceUri())
        INPUTURBANRASTER = readmap(input_urban_raster.dataProvider().dataSourceUri())
        INPUTSPIRASTER = readmap(input_spi_raster.dataProvider().dataSourceUri())
        
        # Calculate Flow Accumulation
        LDD = lddcreate(INPUTDEM,1e31,1e31,1e31,1e31)
        ACC = accuflux(LDD,1)
        
        # Calculate Flow Accumulation with buildings as a material layer. The material layer (urban areas in this case) acts as an obstruction to the flow, influencing how water accumulates and flows in the landscape
        ACCu = accuflux(LDD,INPUTURBANRASTER)
        
        # Upstream urbanization for each pixel
        Ru = (INPUTURBANRASTER/input_urban_pixel_area)
        
        # Urbanization per cell.
        ru = (ACCu/ ACC)
        
        # Local urbanisation correction for flow concentration due to reduced open space.
        f1 = 1/(1-Ru**0.5)
        
        # Upstream correction to account for reduced ground infiltration
        f2 = (1+ru*(input_infiltration_coefficient_urbanized_area/input_infiltration_coefficient_nonurbanized_area)) 
        
        # Corrected Stream power index
        
        CSPI = INPUTSPIRASTER * f1 * f2
        
    
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)

        report(CSPI,outputFilePath)
        
#        self.set_output_crs(output_file=outputFilePath, crs=input_raster.crs(), feedback=feedback, context=context)

        return {self.OUTPUT_RASTER: outputFilePath}
