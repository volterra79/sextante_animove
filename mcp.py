from sextante.core.GeoAlgorithm import GeoAlgorithm
import os.path
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

class mcp(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    FIELD = "FIELD"
    PERCENT = "PERCENT"
    

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/mcp.png")

    def processAlgorithm(self, progress):
       
        
        perc=self.getParameterValue(mcp.PERCENT)
        field = self.getParameterValue(mcp.FIELD)
        vlayerA = QGisLayers.getObjectFromUri(self.getParameterValue(mcp.INPUT))
        GEOS_EXCEPT = True
        FEATURE_EXCEPT = True
        vproviderA = vlayerA.dataProvider()
        allAttrsA = vproviderA.attributeIndexes()
        try:
                vproviderA.select(allAttrsA)
        except:
                pass
        try:
                fields = { 0 : QgsField("ID", QVariant.String),
                            1 : QgsField("Area",  QVariant.Double),
                            2 : QgsField("Perim", QVariant.Double)  
                          }
                writer = self.getOutputFromName(mcp.OUTPUT).getVectorWriter(fields, QGis.WKBPolygon, vproviderA.crs())
        except:
                fields = [QgsField("ID", QVariant.String),
                         QgsField("Area",  QVariant.Double),
                         QgsField("Perim", QVariant.Double) 
                         ]
                writer = self.getOutputFromName(mcp.OUTPUT).getVectorWriter(fields, QGis.WKBPolygon, vproviderA.crs())
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()
        nElement = 0
        index = vproviderA.fieldNameIndex(field)
        features = QGisLayers.features(vlayerA)
        nFeat = len(features)
        unique = ftools_utils.getUniqueValues(vproviderA, index)
        nFeat = nFeat * len(unique)
        progress_perc=100/len(unique)
        n = 0
        for i in unique:
             
              nElement=0
              hull = []
              cx = 0.00 #x of mean coodinate
              cy = 0.00 #y of mean coordinate
              first = True
              nf = 0
              try:
                  vproviderA.select(allAttrsA)
              except:
                  pass
              try:
                  while vproviderA.nextFeature(inFeat):
                      atMap = inFeat.attributeMap()
                      idVar = atMap[ index ]
                      if idVar.toString().trimmed() == i.toString().trimmed():
                         inGeom = QgsGeometry( inFeat.geometry() )
                         points = ftools_utils.extractPoints( inGeom )
                         cx += points[0].x()
                         cy += points[0].y()
                         nf+=1
              except:
                  features = QGisLayers.features(vlayerA)
                  for feat in features:
                      atMap = feat.attributes()
                      idVar = atMap[ index ]
                      if idVar.toString().trimmed() == i.toString().trimmed():
                         inGeom = QgsGeometry( feat.geometry() )
                         points = ftools_utils.extractPoints( inGeom )
                         cx += points[0].x()
                         cy += points[0].y()
                         nf+=1
                      
              cx=(cx / nf)
              cy=(cy / nf)
              meanPoint = QgsPoint(cx, cy)
              distArea = QgsDistanceArea()
              dist={}
              features = QGisLayers.features(vlayerA)
              for inFeat in features:
                try:  
                    atMap = inFeat.attributeMap()
                except:
                    atMap = inFeat.attributes()
                idVar = atMap[ index ]
                if idVar.toString().trimmed() == i.toString().trimmed():
                  if first:
                    first = False
                  nElement += 1
                  inGeom = QgsGeometry( inFeat.geometry() )
                  dis_meas = distArea.measureLine(meanPoint, inGeom.asPoint())
                  dist[dis_meas]= inGeom
                  if perc == 100:
                      points = ftools_utils.extractPoints( inGeom )
                      hull.extend( points )
              if perc <> 100:
                  if perc > 100:
                      perc = 100
                      SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Please insert a valid percentage (0-100%)")
             
                  hull=self.percpoints(perc,dist,nElement)
                  
              if len( hull ) >= 3:
                nfeat = len(hull) * perc / 100
                tmpGeom = QgsGeometry( outGeom.fromMultiPoint( hull ) )
                try:
                  outGeom = tmpGeom.convexHull()
                  outFeat.setGeometry( outGeom )
                  measure = QgsDistanceArea()
                  perim=measure.measurePerimeter(outGeom)
                  area=measure.measure(outGeom)
                  try:
                      outFeat.addAttribute( 0, QVariant( i.toString() ) )
                      outFeat.addAttribute( 1, QVariant( area ) )
                      outFeat.addAttribute( 2, QVariant( perim ) )
                  except:
                      outFeat.setAttributes([QVariant(i.toString()),QVariant(area),QVariant(perim)])
                  writer.addFeature( outFeat )
                  
                  
                except:
                  GEOS_EXCEPT = False
                  continue
              n+=1
              progress.setPercentage(progress_perc*n)
            
        del writer

        if not GEOS_EXCEPT:
            SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Geometry exception while computing convex hull")
        if not FEATURE_EXCEPT:
            SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Feature exception while computing convex hull")

    def defineCharacteristics(self):
        self.name = "Minimun Convex Polygon"
        self.group = "Tools"
        self.addParameter(ParameterVector(mcp.INPUT, "Input layer", ParameterVector.VECTOR_TYPE_POINT))
        self.addParameter(ParameterTableField(mcp.FIELD, "Field", mcp.INPUT))
        self.addParameter(ParameterNumber(mcp.PERCENT, "Percent of fixes", 5, 100, 95))
        self.addOutput(OutputVector(mcp.OUTPUT, "Minimun Convex Polygon"))
        
    def percpoints(self,percent,list_distances,l):
        
        l=(l*percent)/100
        hull=[]
        n=1
        for k in sorted(list_distances.keys()):
               if n < l:
                   points = ftools_utils.extractPoints( list_distances[k])
                   hull.extend( points )
                   n+=1
               else:
                   return hull 
                      
        return hull          
        
        
    #=========================================================
