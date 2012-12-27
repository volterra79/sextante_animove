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
from sextante.ftools import ftools_utils
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
    USE_SELECTED = "USE_SELECTED"
   

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/icons/mcp.png")

    def processAlgorithm(self, progress):
       
        useSelection = self.getParameterValue(mcp.USE_SELECTED)
        perc=self.getParameterValue(mcp.PERCENT)
        field = self.getParameterValue(mcp.FIELD)
        vlayerA = QGisLayers.getObjectFromUri(self.getParameterValue(mcp.INPUT))
        GEOS_EXCEPT = True
        FEATURE_EXCEPT = True
        vproviderA = vlayerA.dataProvider()
        allAttrsA = vproviderA.attributeIndexes()
        vproviderA.select(allAttrsA)
        fields = { 0 : QgsField("ID", QVariant.Int),
                    1 : QgsField("Area",  QVariant.Double),
                    2 : QgsField("Perim", QVariant.Double),  
                    3 : QgsField(field, QVariant.String) }
        writer = self.getOutputFromName(mcp.OUTPUT).getVectorWriter(fields, QGis.WKBPolygon, vproviderA.crs())
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()
        nElement = 0
        index = vproviderA.fieldNameIndex(field)
        # there is selection in input layer
        if useSelection:
          nFeat = vlayerA.selectedFeatureCount()
          selectionA = vlayerA.selectedFeatures()
          
          unique = ftools_utils.getUniqueValues( vproviderA, index )
          nFeat = nFeat * len( unique )
          #faccio loop per ogni valore unico di quel campo
          outID=0
          for i in unique:
             
              nElement=0
              hull = []
              first = True
           
              #####calcolo il punto medio
              
              cx = 0.00
              cy = 0.00
              n = 0
              #vproviderA.rewind()
              while vproviderA.nextFeature(inFeat):
                  atMap = inFeat.attributeMap()
                  idVar = atMap[ index ]
                  if idVar.toString().trimmed() == i.toString().trimmed():
                      geom = QgsGeometry(inFeat.geometry())
                      geom= geom.asPoint()
                      n+=1
           
                      cx += geom.x()
                      cy += geom.y()
              cx=(cx / n)
              cy=(cy / n)
              meanPoint = QgsPoint(cx, cy)
              distArea = QgsDistanceArea()
              
              #data.append(str(float(dist)))
              #########################
              dist={}
              for inFeat in selectionA:
                atMap = inFeat.attributeMap()
                idVar = atMap[ index ]
                if idVar.toString().trimmed() == i.toString().trimmed():
                  if first:
                    #outID = idVar
                    first = False
                  nElement += 1
                  inGeom = QgsGeometry( inFeat.geometry() )
                  dis_meas = distArea.measureLine(meanPoint, inGeom.asPoint())
                  dist[dis_meas]= inGeom
                  if perc == 100:
                      points = ftools_utils.extractPoints( inGeom )
                      hull.extend( points )
                
                progress.setPercentage(int(nElement/nFeat * 100))
              if perc <> 100:
                  if perc > 100:
                      perc = 100
                      SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Please insert a valid percentage (0-100%)")
             
                  hull=self.percpoints(perc,dist,nElement)
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
                  outFeat.addAttribute( 0, QVariant( outID ) )
                  outFeat.addAttribute( 1, QVariant( area ) )
                  outFeat.addAttribute( 2, QVariant( perim ) )
                  outFeat.addAttribute( 3, QVariant( i.toString() ) )
                  writer.addFeature( outFeat )
                  outID+=1
                except:
                  GEOS_EXCEPT = False
                  continue
          
           
        # there is no selection in input layer
        else:
          
          rect = vlayerA.extent()
          nFeat = vproviderA.featureCount()
          outfeatMean = QgsFeature()
          unique = ftools_utils.getUniqueValues( vproviderA, index )
          nFeat = nFeat * len( unique )
          outID = 0
          for i in unique:
              
              nElement=0
              dist={}
              hull = []
              first = True
              #vproviderA.rewind()
              vproviderA.select( allAttrsA )#, rect )
             
              
              #####calcolo il punto medio
              
              cx = 0.00
              cy = 0.00
              n = 0
              while vproviderA.nextFeature(inFeat):
                  atMap = inFeat.attributeMap()
                  idVar = atMap[ index ]
                  if idVar.toString().trimmed() == i.toString().trimmed():
                      geom = QgsGeometry(inFeat.geometry())
                      geom= geom.asPoint()
                      n+=1
           
                      cx += geom.x()
                      cy += geom.y()
              vproviderA.rewind()
              cx=(cx / n)
              cy=(cy / n)
              meanPoint = QgsPoint(cx, cy)
              distArea = QgsDistanceArea()
              #########################
              nElement=0
              
              while vproviderA.nextFeature( inFeat ):
                atMap = inFeat.attributeMap()
                idVar = atMap[ index ]
                if idVar.toString().trimmed() == i.toString().trimmed():
                  if first:
                    #outID = idVar
                    first = False
                  nElement += 1
                  inGeom = QgsGeometry( inFeat.geometry() )
                  dis_meas = distArea.measureLine(meanPoint, inGeom.asPoint())
                  dist[dis_meas]= inGeom
                  #points = ftools_utils.extractPoints( inGeom )
                  if perc == 100:
                      
                      points = ftools_utils.extractPoints( inGeom )
                      hull.extend( points )
                
                    
                
                progress.setPercentage(int(nElement/nFeat * 100))
              if perc <> 100:
                  if perc > 100:
                      perc = 100
                      SextanteLog.addToLog(SextanteLog.LOG_WARNING, "(0-100%)")
                  hull=self.percpoints(perc,dist,nElement)
                  
              if len( hull ) >= 3:
                  
                  tmpGeom = QgsGeometry( outGeom.fromMultiPoint( hull ) )
                  try:
                      outGeom = tmpGeom.convexHull()
                      outFeat.setGeometry( outGeom )
                      measure = QgsDistanceArea()
                      perim=measure.measurePerimeter(outGeom)
                      area=measure.measure(outGeom)
                      outFeat.addAttribute( 0, QVariant( outID ) )
                      outFeat.addAttribute( 1, QVariant( area ) )
                      outFeat.addAttribute( 2, QVariant( perim ) )
                      outFeat.addAttribute( 3, QVariant( i.toString() ) )
                      writer.addFeature( outFeat )
                      outID+=1
                  except:
                      
                      GEOS_EXCEPT = False
                      continue
              
          
        del writer

        if not GEOS_EXCEPT:
            SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Geometry exception while computing convex hull")
        if not FEATURE_EXCEPT:
            SextanteLog.addToLog(SextanteLog.LOG_WARNING, "Feature exception while computing convex hull")

    def defineCharacteristics(self):
        self.name = "Minimun Convex Poplygon"
        self.group = "Tools"
        self.addParameter(ParameterVector(mcp.INPUT, "Input layer", ParameterVector.VECTOR_TYPE_POINT))
        self.addParameter(ParameterTableField(mcp.FIELD, "Field", mcp.INPUT))
        self.addParameter(ParameterNumber(mcp.PERCENT, "Percent of fixes", 5, 100, 95))
        self.addParameter(ParameterBoolean(mcp.USE_SELECTED, "Use selected features", False))
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
