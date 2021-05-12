QGIS processing scripts to make PCRaster available in the Processing Toolbox. 

Install PCRaster and QGIS in a conda environment.

1. Use the Anaconda prompt

Create the environment as explained here: https://pcraster.geo.uu.nl/pcraster/4.3.0/documentation/pcraster_project/install.html Basically this command will do the job:

conda create --name pcrasterqgis -c conda-forge python=3.9.2 pcraster qgis

conda activate pcrasterqgis

Now you can use both PCRaster and QGIS. For example open the python prompt in QGIS and import pcraster there.

Video tutorial: https://youtu.be/IeqUhS_IwVY

After setting up the conda environment, you can use the QGIS Resource Sharing plugin to add PCRaster tools to the toolbox. Install the plugin, go to Settings and add: https://github.com/jvdkwast/qgisrepository.git