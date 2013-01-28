from sextante.core.GeoAlgorithm import GeoAlgorithm
import os.path
import os
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from sextante.parameters.ParameterVector import ParameterVector
from sextante.core.QGisLayers import QGisLayers
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.outputs.OutputVector import OutputVector

try: #qgis 1.8 sextante 1.08
    from sextante.ftools import ftools_utils
except:
    from sextante.algs.ftools import ftools_utils
    
    
from sextante.core.SextanteLog import SextanteLog
from sextante.parameters.ParameterTableField import ParameterTableField
from sextante.parameters.ParameterSelection import ParameterSelection
from sextante.parameters.ParameterBoolean import ParameterBoolean
from sextante.parameters.ParameterNumber import ParameterNumber
import numpy as np
from scipy import stats,misc
import matplotlib.pyplot as plt
from osgeo import gdal, osr
from scipy import interpolate
from sextante.core.SextanteUtils import SextanteUtils

class href(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    FIELD = "FIELD"
    PERCENT = "PERCENT"
   
   

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/href.png")

    def processAlgorithm(self, progress):
            currentPath = os.path.dirname(os.path.abspath(__file__))
            perc=self.getParameterValue(href.PERCENT)
            if perc > 100:
                perc=100
            res=50
            
            field = self.getParameterValue(href.FIELD)
            vlayerA = QGisLayers.getObjectFromUri(self.getParameterValue(href.INPUT))
            GEOS_EXCEPT = True
            FEATURE_EXCEPT = True
            vproviderA = vlayerA.dataProvider()
            allAttrsA = vproviderA.attributeIndexes()
            vproviderA.select(allAttrsA)
            fields = { 0 : QgsField("ID", QVariant.Int),
                        1 : QgsField("Area",  QVariant.Double),
                        2 : QgsField("Perim", QVariant.Double),  
                        3 : QgsField(field, QVariant.String) }
            writer = self.getOutputFromName(href.OUTPUT).getVectorWriter(fields, QGis.WKBPolygon, vproviderA.crs())
            inFeat = QgsFeature()
            outFeat = QgsFeature()
            inGeom = QgsGeometry()
            outGeom = QgsGeometry()
            index = vproviderA.fieldNameIndex(field)
            features = QGisLayers.features(vlayerA)
            nFeat = len(features)
            unique = ftools_utils.getUniqueValues(vproviderA, index)
            nFeat = nFeat * len(unique)
            progress_perc=100/len(unique)
            n = 0
            outID = 0
            for i in unique:
                  nElement=0
                  xPoints = []
                  yPoints = []
                  first = True
                  vproviderA.select(allAttrsA)
                  features = QGisLayers.features(vlayerA)
                  for inFeat in features:
                    atMap = inFeat.attributeMap()
                    idVar = atMap[ index ]
                    if idVar.toString().trimmed() == i.toString().trimmed():
                        nElement += 1
                        inGeom = QgsGeometry( inFeat.geometry() )
                        points = ftools_utils.extractPoints( inGeom )
                        xPoints.append(points[0].x())
                        yPoints.append(points[0].y())
                  if len(xPoints) == 0: #number of selected features
                      continue    
                  xmin = min(xPoints) - 0.5*(max(xPoints)-min(xPoints))
                  xmax = max(xPoints) + 0.5*(max(xPoints)-min(xPoints))
                  ymin = min(yPoints) - 0.5*(max(yPoints)-min(yPoints))
                  ymax = max(yPoints) + 0.5*(max(yPoints)-min(yPoints))
                  X,Y = np.mgrid[xmin:xmax:complex(res), ymin:ymax:complex(res)]
                  positions = np.vstack([X.ravel(), Y.ravel()])  
                  values = np.vstack([xPoints,yPoints])
                  # scipy.stats.kde.gaussian_kde -- 
                  # Representation of a kernel-density estimate using Gaussian kernels.
                  kernel = stats.kde.gaussian_kde(values)
                  Z = np.reshape(kernel(positions).T, X.T.shape)
                  
                  raster_name = 'r'+str(n)
                  int = str(((100.0-perc)/2))
                 
                  self.to_geotiff(currentPath+'/'+raster_name, xmin,xmax,ymin,ymax,X,Y, Z) 
                  
                  if SextanteUtils.isWindows():
                      os.system("gdal_contour.exe "+currentPath+"/" +raster_name+" -a values -fl " + int + " " + currentPath+"/c"+str(n)+".shp")
                      commands = ["cmd.exe", "/C ", "gdal_polygonize.bat"]
                  else:
                      os.system("gdal_contour "+currentPath+"/" +raster_name+" -a values -fl " + int + " " + currentPath+"/c"+str(n)+".shp")
                  layer = QgsVectorLayer(currentPath+"/c"+str(n)+".shp", "c"+str(n), "ogr")       
                  
                  provider = layer.dataProvider()
    
                  feat = QgsFeature()
                  allAttrs = provider.attributeIndexes()
                  provider.select(allAttrs)
                  caps = layer.dataProvider().capabilities()
                  fldDesc = provider.fieldNameIndex("values")
                  arrayid=[]
                  polyGeom = []
                  feature_list = []
                  multi_feature = []
                  area = 0
                  perim = 0
                  measure = QgsDistanceArea()
                  while provider.nextFeature( feat ):
                    
                    id = feat.id()
                    attrs = feat.attributeMap()
                    outGeom = feat.geometry().asPolyline()
                    perim=perim + measure.measurePerimeter(QgsGeometry.fromPolygon([outGeom]))
                    area=area + measure.measure(QgsGeometry.fromPolygon([outGeom]))
                    polyGeom.append(outGeom) 
                                
                  outFeat.setGeometry(QgsGeometry.fromPolygon(polyGeom))
                  outFeat.addAttribute( 0, QVariant( outID) )
                  outFeat.addAttribute( 1, QVariant( area ) )
                  outFeat.addAttribute( 2, QVariant( perim ) )
                  outFeat.addAttribute( 3, QVariant( i.toString() ) )
                  writer.addFeature(outFeat)
                  outID+=1
                  layer.dataProvider().deleteFeatures(arrayid)       
                  os.remove(currentPath+"/" +raster_name)
                  
                  if SextanteUtils.isWindows():
                      os.system('del '+currentPath+'/c'+str(n)+'.*')
                  else:
                      os.system('rm '+currentPath+'/c'+str(n)+'.*')
                  
                  
                  n+=1
                  progress.setPercentage(progress_perc * n)    
            del writer
            if not GEOS_EXCEPT:
                      SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Geometry exception while computing convex hull")
            if not FEATURE_EXCEPT:
                      SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Feature exception while computing convex hull")

            
    def defineCharacteristics(self):
        self.name = "Kernel Density Estimation"
        self.group = "Tools"
        self.addParameter(ParameterVector(href.INPUT, "Input layer", ParameterVector.VECTOR_TYPE_POINT))
        self.addParameter(ParameterTableField(href.FIELD, "Group fixes by", href.INPUT))
        self.addParameter(ParameterNumber(href.PERCENT, "Percentage of Utilisation Distribution(UD)", 5, 100, 95))
        self.addOutput(OutputVector(href.OUTPUT, "Kernel Density Estimation"))
        
    
    def to_geotiff(self,fname,xmin,xmax,ymin,ymax,X,Y, Z):
        '''
        saves the kernel as a GEOTIFF image
        '''
        driver = gdal.GetDriverByName("GTiff")
        out = driver.Create(fname, len(X), len(Y), 1, gdal.GDT_Float64)
        #pixel sizes
        xps = (xmax - xmin) / float(len(X))
        yps = (ymax - ymin) / float(len(Y))
        out.SetGeoTransform((xmin, xps, 0, ymin, 0, yps))
        
        Z = Z.clip(0) * 100.0/Z.max()
        
        out.GetRasterBand(1).WriteArray(Z.T)


    
        
    #=========================================================
