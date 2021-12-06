"""
Model exported as python.
Name : Burn lines in DEM v2
Group : PCRaster
With QGIS : 31614
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterRasterDestination,
    )
import processing


class BurnDrainageInDEM(QgsProcessingAlgorithm):
    
    INPUT_DEM = 'INPUT_DEM'
    DRAINAGE_LAYERS = 'DRAINAGE_LAYERS'
    BUFFER_SIZE = 'BUFFER_SIZE'
    SMOOTH_DROP = 'SMOOTH_DROP'
    SHARP_DROP = 'SHARP_DROP'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM, 'Input DEM', defaultValue=None))
        self.addParameter(QgsProcessingParameterMultipleLayers(self.DRAINAGE_LAYERS, 'Drainage layers', layerType=QgsProcessing.TypeVectorAnyGeometry, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber(self.BUFFER_SIZE, 'Buffer distance', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=100))
        self.addParameter(QgsProcessingParameterNumber(self.SMOOTH_DROP, 'Smooth drop', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=90))
        self.addParameter(QgsProcessingParameterNumber(self.SHARP_DROP, 'Sharp drop', type=QgsProcessingParameterNumber.Double, defaultValue=30))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, 'Burned DEM', createByDefault=True, defaultValue=None))

    def flags(self):
        return QgsProcessingAlgorithm.FlagNoThreading
        
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        
        dem_layer = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        dem_crs = dem_layer.crs()
        dem_resolution = dem_layer.rasterUnitsPerPixelX()
        if dem_layer.rasterUnitsPerPixelY() != dem_resolution:
            raise QgsProcessingException('DEM y resolution ({}) must match x resolution ({})'.format(dem_layer.rasterUnitsPerPixelY(), dem_resolution))
        
        # check drainage layers for validity
        drainage_layers = self.parameterAsLayerList(parameters, self.DRAINAGE_LAYERS, context)
        for layer in drainage_layers:
            if layer.crs() != dem_crs:
                raise QgsProcessingException('All drainage layers must have the same CRS as the DEM ({})'.format(dem_crs.authid()))
            
        # Merge drainage layers
        alg_params = {
            'INPUT': parameters[self.DRAINAGE_LAYERS],
            'UNIONED': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        feedback.pushInfo('Merging drainage layers')
        merged_drainage_layer = processing.run('gdal:buildvirtualvector', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Rasterize drainage
        feedback.pushInfo('Converting drainage to raster')
        alg_params = {
            'BURN': 1,
            'DATA_TYPE': 0,  # byte
            'EXTENT': parameters[self.INPUT_DEM],
            'EXTRA': '',
            'FIELD': '',
            'HEIGHT': dem_resolution,
            'INIT': None,
            'INPUT': merged_drainage_layer,
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'WIDTH': dem_resolution,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        rasterized_drainage = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Convert drainage to PCRaster Format
        feedback.pushInfo('Convert drainage to PCRaster format')
        alg_params = {
            'INPUT': rasterized_drainage,
            'INPUT2': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        pcraster_drainage = processing.run('pcraster:converttopcrasterformat', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        feedback.pushInfo('Convert DEM to PCRaster format')
        # Convert DEM to PCRaster Format
        alg_params = {
            'INPUT': parameters[self.INPUT_DEM],
            'INPUT2': 3,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        pcraster_dem = processing.run('pcraster:converttopcrasterformat', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # spatial
        feedback.pushInfo('Preparing drainage pt 1')
        alg_params = {
            'INPUT': 0,
            'INPUT1': 0,
            'INPUT2': pcraster_dem,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        dem_spatial = processing.run('pcraster:spatial', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # cover
        # This is needed to create a boolean with zeros and ones. Otherwise it has ones and nodata.
        feedback.pushInfo('Preparing drainage pt 2')
        alg_params = {
            'INPUT': pcraster_drainage,
            'INPUT2': dem_spatial,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        drainage_cover = processing.run('pcraster:cover', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # burndem
        # Not all parameters of burndem are asked as input in this model.
        feedback.pushInfo('Burning DEM')
        alg_params = {
            'INPUT': pcraster_dem,
            'INPUT0': 0,
            'INPUT1': 0,
            'INPUT10': parameters[self.SHARP_DROP],
            'INPUT2': 9999999,
            'INPUT3': 9999999,
            'INPUT4': 9999999,
            'INPUT5': 9999999,
            'INPUT6': 0,
            'INPUT7': drainage_cover,
            'INPUT8': parameters[self.BUFFER_SIZE],
            'INPUT9': parameters[self.SMOOTH_DROP],
            'OUTPUT': parameters[self.OUTPUT]
        }
        burned_dem = processing.run('script:burndem', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        return {
            self.OUTPUT: burned_dem
            }

    def name(self):
        return 'burndrainageindem'

    def displayName(self):
        return 'Burn drainage in DEM with vector layers'

    def group(self):
        return 'PCRaster User Scripts'

    def groupId(self):
        return 'pcrasteruser'

    def createInstance(self):
        return BurnDrainageInDEM()
        
    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """<html><body><p>Burn drainage in DEM with vector layers</p>

            <h2>Parameters</h2>

            <b>Input DEM</b> (required) - DEM in PCRaster format (scalar)
            <b>Drainage layers</b> (required) - Vector layers to burn into the DEM
            <b>Buffer distance</b> (required) - Distance of gradual drop to drainage (map units)
            <b>Smooth drop</b> (required) - Depth of smooth drop (map units)
            <b>Sharp drop</b> (required) - Depth of sharp drop at drainage added to smooth drop (map units)
            <b>Burned DEM</b> (required) - Result burned DEM in PCRaster format (scalar)

            Authors: Nyall Dawson, Hans van der Kwast
            Based on original algorithm DEM Optimization in <a href="http://spatial-analyst.net/ILWIS/htm/ilwisapp/dem_optimization_functionality.htm">ILWIS</a>
            """
        )

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)