Note that the PCRaster Processing Tools are now available through the official QGIS Plugins repository

See https://jvdkwast.github.io/qgis-processing-pcraster/ for more info

QGIS processing scripts to make PCRaster available in the Processing Toolbox. 

Install PCRaster and QGIS in a conda environment.

1. Use the Anaconda prompt

Create the environment as explained here: https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_project/install.html Basically this command will do the job:

conda create --name pcrasterqgis -c conda-forge python=3.9.2 pcraster qgis

conda activate pcrasterqgis

2. Now you can use both PCRaster and QGIS. For example open the python prompt in QGIS and import pcraster there. Type qgis to start QGIS.


3. After setting up the conda environment, you can use the QGIS Resource Sharing plugin to add PCRaster tools to the toolbox. Install the plugin, go to Settings and add: https://github.com/jvdkwast/qgisrepository.git

Video tutorial for geting started: https://youtu.be/6uSvW6PUiMA
Playlist with examples: https://youtube.com/playlist?list=PLeuKJkIxCDj2xbV45C45wz3N89FvmTuSu
