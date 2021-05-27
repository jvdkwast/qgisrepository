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


class PotRadAlgorithm(QgsProcessingAlgorithm):
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
    INPUT_TRANS = 'INPUT1'
    INPUT_LAT = 'INPUT2'
    INPUT_DOY = 'INPUT3'
    INPUT_TIME = 'INPUT4'
    OUTPUT_DIR = 'OUTPUT1'
    OUTPUT_DIF = 'OUTPUT2'
    OUTPUT_TOT = 'OUTPUT3'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PotRadAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'potrad'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('POTRAD model')

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
            """Model for calculation incoming potential light energy (O. van Dam, 2000)
            
          
            Parameters:
            
            * <b>Input DEM layer</b> (required) - scalar raster layer
            * <b>Latitude</b> (required) - latitude in decimal degrees
            * <b>Transmissivity</b> (required) - Transmissivity tau [0-1]
            * <b>DOY</b> (required) - Day of Year
            * <b>Time</b> (required) - Time in hours
            * <b>Output direct sunlight</b> (required) - direct sunlight on a horizontal surface [W/m2] if no shade
            * <b>Output diffuse sunlight</b> (required) - diffuse light [W/m2] for shade and no shade
            * <b>Total incomming light</b> (required) - sum of direct and indirect sunlight [W/m2]
            
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
            QgsProcessingParameterNumber(
                self.INPUT_TRANS,
                self.tr('Transmissivity [0-1]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_LAT,
                self.tr('Latitude [DD]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=33.9932
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_DOY,
                self.tr('Day of year'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=294.0
            )
        )

        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_TIME,
                self.tr('Time of overpass [decimal hours UTC]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=11.217
            )
        )

        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DIR,
                self.tr('Output direct radiation [W/m2]')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DIF,
                self.tr('Output diffuse radiation [W/m2]')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_TOT,
                self.tr('Output Total Incoming Radiation (Rn) raster [W/m2]')
            )
        )

        
    def Rswd(self, DEM, Lat, Trans, DOY, Time):
        """ Potential Radiation Equator model
        (c) O. van Dam, UU, Tropenbos-Guyana
        Version 5, June 2000
        NOTE: Copyright: This program is free to use provided·
        you refer to the manualfor citation.
        Do not distribute without prior approval of the author.
        Manual and additional info: O.vanDam@geog.uu.nl

        -----------------------------------------------------
                   Model for calculation
               incoming potential light energy
        -----------------------------------------------------
   
        DEM Input Digital Elevation Model (spatial)
        Lat Latitude in decimal degrees (non-spatia)
        Trans Transmissivity tau (Gates, 1980) (non-spatial)
        DOY Day of Year (non-spatial)
        Time Time in hours (non-spatial)"""
   
        # constants
        pi = 3.1415 # pi
        Sc = 1367.0 # Solar constant (Gates, 1980) [W/m2]

        SlopMap = scalar(atan(slope(DEM)))
        AspMap  = scalar(aspect(DEM)) # aspect [deg]
        AtmPcor = ((288.0-0.0065*DEM)/288.0)**5.256 # atmospheric pressure correction [-]

        # Solar geometry
        # ----------------------------
        # SolDec  :declination sun per day  between +23 & -23 [deg]
        # HourAng :hour angle [-] of sun during day
        # SolAlt  :solar altitude [deg], height of sun above horizon
        SolDec  = -23.4*cos(360.0*(DOY+10.0)/365.0)
        HourAng = 15.0*(Time-12.01)
        SolAlt  = scalar(asin(scalar(sin(Lat)*sin(SolDec)+cos(Lat)*cos(SolDec)*cos(HourAng))))

        # Solar azimuth
        # ----------------------------
        # SolAzi  :angle solar beams to N-S axes earth [deg]
        SolAzi = scalar(acos((sin(SolDec)*cos(Lat)-cos(SolDec)*sin(Lat)*cos(HourAng))/cos(SolAlt)))
        SolAzi = ifthenelse(Time <= 12.0, SolAzi, 360.0 - SolAzi)
        # Additonal extra correction by R.Sluiter, Aug '99
        SolAzi = ifthenelse(SolAzi > 89.994 and SolAzi < 90.0, 90.0, SolAzi)
        SolAzi = ifthenelse(SolAzi > 269.994 and SolAzi < 270.0, 270.0, SolAzi)

        # Surface azimuth
        # ----------------------------
        # cosIncident :cosine of angle of incident; angle solar beams to angle surface
        cosIncident = sin(SolAlt)*cos(SlopMap)+cos(SolAlt)*sin(SlopMap)*cos(SolAzi-AspMap)

        # Critical angle sun
        # ----------------------------
        # HoriAng  :tan maximum angle over DEM in direction sun, 0 if neg·
        # CritSun  :tan of maximum angle in direction solar beams
        # Shade    :cell in sun 1, in shade 0
        HoriAng   = horizontan(DEM,directional(SolAzi))
        HoriAng   = ifthenelse(HoriAng < 0.0, scalar(0.0), HoriAng)
        CritSun   = ifthenelse(SolAlt > 90.0, scalar(0.0), scalar(atan(HoriAng)))
        Shade   = ifthenelse(SolAlt > CritSun, scalar(1), scalar(0))
   
        # Radiation outer atmosphere
        # ----------------------------
        OpCorr = Trans**((sqrt(1229.0+(614.0*sin(SolAlt))**2.0)-614.0*sin(SolAlt))*AtmPcor)     # correction for air masses [-]
        Sout = Sc*(1.0+0.034*cos(360.0*DOY/365.0)) # radiation outer atmosphere [W/m2]
        Snor = Sout*OpCorr                    # rad on surface normal to the beam [W/m2]

        # Radiation at DEM
        # ----------------------------
        # Sdir   :direct sunlight on a horizontal surface [W/m2] if no shade
        # Sdiff  :diffuse light [W/m2] for shade and no shade
        # Stot   :total incomming light Sdir+Sdiff [W/m2] at Hour
        # PotRad :avg of Stot(Hour) and Stot(Hour-HourStep)
        Sdir   = ifthenelse(Snor*cosIncident*Shade < 0.0, 0.0, Snor*cosIncident*Shade)
        Sdiff  = ifthenelse(Sout*(0.271-0.294*OpCorr)*sin(SolAlt) < 0.0, 0.0, Sout*(0.271-0.294*OpCorr)*sin(SolAlt))
        Stot = Sdir + Sdiff                                         # Rad [W/m2]
        #Rswd = Snor
        return Sdir,Sdiff,Stot

    def writePCRastermaps(self,pcrastermap,outputraster,parameters,context):
        outputFilePath = self.parameterAsOutputLayer(parameters, outputraster, context)
        report(pcrastermap,outputFilePath)
        return outputFilePath
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # set clone
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        setclone(input_raster.dataProvider().dataSourceUri())
        
        # read DEM
        DEM = readmap(input_raster.dataProvider().dataSourceUri())


        # read parameters
        Trans = self.parameterAsDouble(parameters, self.INPUT_TRANS, context)
        Lat = self.parameterAsDouble(parameters, self.INPUT_LAT, context)
        DOY = self.parameterAsDouble(parameters, self.INPUT_DOY, context)
        Time = self.parameterAsDouble(parameters, self.INPUT_TIME, context)


        # Calculate radiation
        Rswd = self.Rswd(DEM, Lat, Trans, DOY, Time)
        
        # Write output rasters
        results = {}
        results[self.OUTPUT_DIF] = self.writePCRastermaps(Rswd[0],self.OUTPUT_DIF,parameters,context)
        results[self.OUTPUT_DIR] = self.writePCRastermaps(Rswd[1],self.OUTPUT_DIR,parameters,context)
        results[self.OUTPUT_TOT] = self.writePCRastermaps(Rswd[2],self.OUTPUT_TOT,parameters,context)

        
        return results
