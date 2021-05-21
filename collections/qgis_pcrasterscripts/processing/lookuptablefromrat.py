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
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination)
from qgis import processing
from pcraster import *
from osgeo import gdal
import sys
import csv


class Lookuptablefromrat(QgsProcessingAlgorithm):
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
    OUTPUT_TABLE = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Lookuptablefromrat()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lookuptablefromrat'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('lookup table from RAT')

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
            """Creates a lookup table from the Value and Class columns of the Raster Attribute Table.
            
            Parameters:
            
            * <b>Input Raster layer</b> (required) - rasters layer with RAT
            * <b>Output lookup table</b> (required) - lookup table in ASCII text format.
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
                self.tr('Raster layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_TABLE,
                self.tr('Output Lookup Table'),
                'CSV files (*.csv)',
            )
        )
    
    def tocsv(self, rat, filepath, tableType):
        with open(filepath, 'w',newline='') as csvfile:
            csvwriter = csv.writer(csvfile,delimiter=' ')

            #Write out column headers
            icolcount=rat.GetColumnCount()
            cols=[]
            skipcols=['Count','R','G','B','A']
            for icol in range(icolcount):
                if rat.GetNameOfCol(icol) not in skipcols:
                    cols.append(rat.GetNameOfCol(icol))
            #csvwriter.writerow(cols)


            #Write out each row.
            irowcount = rat.GetRowCount()
            
            for irow in range(irowcount):
                cols=[]
                if tableType == 'thematic':
                    for icol in range(icolcount):
                        if rat.GetNameOfCol(icol) not in skipcols:
                            itype=rat.GetTypeOfCol(icol)
                            if itype==gdal.GFT_Integer:
                                value='%s'%rat.GetValueAsInt(irow,icol)
                            elif itype==gdal.GFT_Real:
                                value='%.16g'%rat.GetValueAsDouble(irow,icol)
                            else:
                                value='%s'%rat.GetValueAsString(irow,icol)
                            cols.append(value)
                    csvwriter.writerow(cols)
                
                if tableType == 'athematic':
                    for icol in range(3):
                        if rat.GetNameOfCol(icol) not in skipcols:
                            itype=rat.GetTypeOfCol(icol)
                            if itype==gdal.GFT_Integer:
                                value='%s'%rat.GetValueAsInt(irow,icol)
                            elif itype==gdal.GFT_Real:
                                #value='%.16g'%rat.GetValueAsDouble(irow,icol)
                                if icol == 0 and irow == 0:
                                    value='[%s'%rat.GetValueAsString(irow,icol)
                                elif icol == 1:
                                    value='%s]'%rat.GetValueAsString(irow,icol)
                                else:
                                    value='<%s'%rat.GetValueAsString(irow,icol)   
                            else:
                                value='%s'%rat.GetValueAsString(irow,icol)
                            cols.append(value)
                    cols[0:2] = [','.join(cols[0:2])]
                    csvwriter.writerow(cols)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        output_lookuptable = self.parameterAsFile(parameters, self.OUTPUT_TABLE, context)
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        ds=gdal.Open(input_raster.dataProvider().dataSourceUri())
        rat=ds.GetRasterBand(1).GetDefaultRAT()
        metadata=ds.GetMetadata()
        if metadata['PCRASTER_VALUESCALE'] == 'VS_SCALAR':
            tableType = 'athematic'
        else:
            tableType = 'thematic'
        
        self.tocsv(rat, output_lookuptable, tableType)
        
        results = {}
        results[self.OUTPUT_TABLE] = output_lookuptable
        
        return results
