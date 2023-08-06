"""
Model exported as python.
Name : Stream and Catchment Delineation
Group : Hydrology
With QGIS : 32809
"""

from pcraster import (
    readmap,
    setclone,
    lddcreate,
    catchment,
    streamorder,
    areamaximum,
    spreadmaxzone,
    ifthen,
    cover,
    boolean,
    accuflux,
    ordinal,
    report
)

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterExtent,
    QgsProcessingParameterPoint,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterCrs,
    QgsProcessingParameterString,
    QgsProcessingParameterFile)

import os, re, csv


class StreamAndCatchmentDelineation(QgsProcessingAlgorithm):

    INPUT_DEM = 'INPUT_DEM'
    INPUT_EXTENT = 'INPUT_EXTENT'
    INPUT_OUTLET = 'INPUT_OUTLET'
    INPUT_THRESHOLD = 'INPUT_THRESHOLD'
    INPUT_TOLERANCE = 'INPUT_TOLERANCE'
    INPUT_CRS = 'INPUT_CRS'
    INPUT_KEY = 'INPUT_KEY'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    OUTPUT_CATCHMENT = 'OUTPUT_CATCHMENT'
    OUTPUT_STREAMS = 'OUTPUT_STREAMS'
    OUTPUT_DEM = 'OUTPUT_DEM'
    OUTPUT_FLOWDIRECTION = 'OUTPUT_FLOWDIRECTION'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterEnum(self.INPUT_DEM, 'Select DEM to download', 
                            options=['SRTM 90m','SRTM 30m','SRTM GL1 Ellipsoidal 30m','ALOS World 3D 30m','ALOS World 3D Ellipsoidal 30m','Global Bathymetry SRTM15+ V2.1','Copernicus Global DSM 90m','Copernicus Global DSM 30m','NASADEM Global DEM','EU DTM 30m', 'GEDI L3 1km'], 
                            allowMultiple=False, defaultValue=[1]
                            )
                          )
        self.addParameter(QgsProcessingParameterString(self.INPUT_KEY, 'OpenTopography API Key', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterExtent(self.INPUT_EXTENT, 'Study area extent', defaultValue=None))
        self.addParameter(QgsProcessingParameterPoint(self.INPUT_OUTLET, 'Select outlet point on map', defaultValue=''))
        self.addParameter(QgsProcessingParameterNumber(self.INPUT_THRESHOLD, 'Strahler order threshold', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=5))
        self.addParameter(QgsProcessingParameterNumber(self.INPUT_TOLERANCE, 'Snapping tolerance (map units)', type=QgsProcessingParameterNumber.Double, defaultValue=250))
        self.addParameter(QgsProcessingParameterCrs(self.INPUT_CRS, 'Output CRS', defaultValue='EPSG:3857'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_CATCHMENT, 'Output catchment polygon', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_STREAMS, 'Output streams', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_DEM, 'Output DEM', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_FOLDER, 'Output folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_FLOWDIRECTION, 'Output Flow Direction raster', createByDefault=True, defaultValue=None))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(12, model_feedback)
        results = {}
        outputs = {}

        output_folder = self.parameterAsFile(parameters, self.OUTPUT_FOLDER, context)
        
        # Create PCRaster layer from point
        input_string = self.parameterAsString(parameters, self.INPUT_OUTLET, context)
        
        # Regular expression pattern to extract x, y coordinates
        pattern = r'([\d.]+),([\d.]+)'
        
        # Find coordinates using regex
        match = re.search(pattern, input_string)
        
        if match:
            x_coordinate = match.group(1)
            y_coordinate = match.group(2)
        
            # Write coordinates to CSV file
            with open('{}'.format(os.path.join(output_folder,"coordinates.csv")), 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([x_coordinate, y_coordinate, '1'])

            feedback.pushInfo("Coordinates written to {}".format(os.path.join(output_folder,"coordinates.csv")))
        else:
            feedback.pushInfo("Coordinates not found in the input string.")

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # OpenTopography DEM Downloader
        feedback.pushInfo("Downloading DEM...")
        alg_params = {
            'API_key': parameters[self.INPUT_KEY],
            'DEMs': parameters[self.INPUT_DEM],
            'Extent': parameters[self.INPUT_EXTENT],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['OpentopographyDemDownloader'] = processing.run('OTDEMDownloader:OpenTopography DEM Downloader', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Warp (reproject)
        feedback.pushInfo("Reprojecting DEM...")
        alg_params = {
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': outputs['OpentopographyDemDownloader']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': -9999,
            'OPTIONS': '',
            'RESAMPLING': 0,  # Nearest Neighbour
            'SOURCE_CRS': None,
            'TARGET_CRS': parameters[self.INPUT_CRS],
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': 30,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WarpReproject'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Convert DEM to PCRaster Format
        feedback.pushInfo("Converting DEM to PCRaster format...")
        alg_params = {
            'INPUT': outputs['WarpReproject']['OUTPUT'],
            'INPUT2': 3,  # Scalar
            'OUTPUT': parameters[self.OUTPUT_DEM]
        }
        outputs['ConvertDemToPcrasterFormat'] = processing.run('pcraster:converttopcrasterformat', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Calculate flow direction
        feedback.pushInfo("Calculating flow direction (this can take some time!)...")
        output_dem = self.parameterAsRasterLayer(parameters, self.OUTPUT_DEM, context)
        setclone(output_dem.dataProvider().dataSourceUri())
        DEM = readmap(output_dem.dataProvider().dataSourceUri())
        FlowDirection = lddcreate(DEM,1e31,1e31,1e31,1e31)
        output_ldd = self.parameterAsOutputLayer(parameters, self.OUTPUT_FLOWDIRECTION, context)
        report(FlowDirection,output_ldd)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}


        # Calculate Strahler orders
        feedback.pushInfo("Calculating Strahler orders...")
        StrahlerOrders = streamorder(FlowDirection)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Select Strahler orders >= threshold
        feedback.pushInfo("Deriving stream network raster...")
        input_threshold = self.parameterAsInt(parameters,self.INPUT_THRESHOLD,context)
        river = ifthen(StrahlerOrders >= ordinal(input_threshold), StrahlerOrders)
        report(river,os.path.join(output_folder,"river.map"))

        # import outlet to PCRaster
        feedback.pushInfo("Snapping outlet to stream...")
        cmd = "col2map -B {} {} --clone {}".format(os.path.join(output_folder, "coordinates.csv"),os.path.join(output_folder, "outlet.map"),os.path.join(output_folder, "river.map"))
        os.system(cmd)

        OutletOrigin = readmap(os.path.join(output_folder,"outlet.map"))
        Tolerance = self.parameterAsDouble(parameters,self.INPUT_TOLERANCE,context)
        Outletbuffer = spreadmaxzone(OutletOrigin,0,1,Tolerance)
        report(Outletbuffer,os.path.join(output_folder,"outletbuffer.map"))
        FlowAccum = accuflux(FlowDirection,1)
        LocalMax = areamaximum(FlowAccum,Outletbuffer)
        OutletSnapped = ifthen(FlowAccum == LocalMax, boolean(1))
        report(OutletSnapped,os.path.join(output_folder,"outletsnapped.map"))
        
        feedback.pushInfo("Delineating catchment raster...")
        catchmentraster = catchment(FlowDirection,OutletSnapped)
        report(catchmentraster,os.path.join(output_folder,"catchment.map"))
        

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        results[self.OUTPUT_DEM] = outputs['ConvertDemToPcrasterFormat']['OUTPUT']
        
        # Thin river raster
        feedback.pushInfo("Thinning the stream network raster...")
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'input': os.path.join(output_folder,"river.map"),
            'iterations': 200,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        
        outputs['ThinRiverRaster'] = processing.run('grass7:r.thin', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Convert river raster to line vector
        feedback.pushInfo("Vectorizing the stream network...")
        alg_params = {
            '-b': False,
            '-s': False,
            '-t': False,
            '-v': True,
            '-z': False,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,  # auto
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'column': 'value',
            'input': outputs['ThinRiverRaster']['output'],
            'type': 0,  # line
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertRiverRasterToLineVector'] = processing.run('grass7:r.to.vect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Assign projection
        alg_params = {
            'CRS': parameters[self.INPUT_CRS],
            'INPUT': outputs['ConvertRiverRasterToLineVector']['output'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AssignProjection'] = processing.run('native:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['AssignProjection']['OUTPUT'],
            'METHOD': 1,  # Structure
            'OUTPUT': parameters[self.OUTPUT_STREAMS]
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OutputStreams'] = outputs['FixGeometries']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Polygonize catchment raster
        feedback.pushInfo("Polygonizing the catchment boundary...")
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': os.path.join(output_folder,"catchment.map"),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonizeCatchmentRaster'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '"DN" = 1',
            'INPUT': outputs['PolygonizeCatchmentRaster']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        # Assign projection
        alg_params = {
            'CRS': parameters[self.INPUT_CRS],
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT':parameters[self.OUTPUT_CATCHMENT]
        }
        outputs['AssignProjection'] = processing.run('native:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OutputCatchmentPolygon'] = outputs['AssignProjection']['OUTPUT']
        
        return results

    def name(self):
        return 'Stream and Catchment Delineation'

    def displayName(self):
        return 'Stream and Catchment Delineation'

    def group(self):
        return 'PCRaster User Scripts'

    def groupId(self):
        return 'pcrasteruser'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Calculate streams and catchment boundary for a given extent and outlet. Make sure you have installed the PCRaster Tools plugin and the OpenTopography DEM Downloader plugin</p></body></html></p>
<h2>Input parameters</h2>
<h3>Select DEM to download</h3>
<p>Choose the DEM that you want to dowload from <a href=https://opentopography.org/>OpenTopography</a></p>
<h3>OpenTopography API Key</h3>
<p>Get your key from https://opentopography.org/</p>
<h3>Study area extent</h3>
<p>Extent that will be used to download the DEM</p>
<h3>Select outlet point on map</h3>
<p>Click on an outlet in the map canvas</p>
<h3>Strahler order threshold</h3>
<p>Threshold to determine the streams. Larger means less streams.</p>
<h3>Snapping tolerance(map units)</h3>
<p>Search buffer for snapping to the drainage</p>
<h3>Output CRS</h3>
<p>Output projection. <b>Make sure you have set your project to the same projection!</b></p>
<h3>Output folder</h3>
<p>Folder to store intermediate outputs</p>
<br><p align="right">Algorithm author: Hans van der Kwast</p><p align="right">Help author: Hans van der Kwast</p><p align="right">Algorithm version: 1.0</p></body></html>"""

    def createInstance(self):
        return StreamAndCatchmentDelineation()
