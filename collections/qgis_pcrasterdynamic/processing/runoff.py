from pcraster import *
from pcraster.framework import *

class RunoffModel(DynamicModel):
  def __init__(self, cloneMap,rainstationsMap,InfilCapTable,soilMap,DEM,rainTimeSeries,rainfallOutput,runoffOutputStack):
    DynamicModel.__init__(self)
    setclone(cloneMap)
    self.rainstat = rainstationsMap
    self.InfilCapTable = InfilCapTable
    self.soilMap = soilMap
    self.DEM = DEM
    self.rainTimeSeries = rainTimeSeries
    self.rainfallOutput = rainfallOutput
    self.runoffOutputStack = runoffOutputStack

  def initial(self):
    # coverage of meteorological stations for the whole area
    self.rainZones = spreadzone(self.rainstat, scalar(0), scalar(1))

    # create an infiltration capacity map (mm/6 hours), based on the
    # soil map
    self.infiltrationCapacity = lookupscalar(self.InfilCapTable, self.soilMap)
    self.report(self.infiltrationCapacity, "infilcap")

    # generate the local drain direction map on basis of the elevation map
    self.ldd = lddcreate(self.DEM, 1e31, 1e31, 1e31, 1e31)
    self.report(self.ldd, "ldd")

    # initialise timeoutput
    #self.runoffTss = TimeoutputTimeseries(self.runoffTimeSeries, self, self.samplesMap, noHeader=False)

  def dynamic(self):
    # calculate and report maps with rainfall at each timestep (mm/6 hours)
    surfaceWater = timeinputscalar(self.rainTimeSeries, self.rainZones)
    self.report(surfaceWater, self.rainfallOutput)

    # compute both runoff and actual infiltration
    runoff = accuthresholdflux(self.ldd, surfaceWater,\
         self.infiltrationCapacity)
    infiltration = accuthresholdstate(self.ldd, surfaceWater,\
         self.infiltrationCapacity)

    # output runoff, converted to m3/s, at each timestep
    logRunOff = runoff / scalar(216000)
    self.report(logRunOff, self.runoffOutputStack)
    # sampling timeseries for given locations
    #self.runoffTss.sample(logRunOff)
