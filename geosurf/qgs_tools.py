
from __future__ import division

from builtins import str

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *


def loaded_layers():
    
    return list(QgsProject.instance().mapLayers().values())

    
def loaded_vector_layers():
 
    return [layer for layer in loaded_layers() if layer.type() == QgsMapLayer.VectorLayer]
    

def loaded_point_layers():

    return [layer for layer in loaded_vector_layers() if layer.geometryType() == QgsWkbTypes.PointGeometry]
    

def get_point_data( pt_layer, fields = [], selected = True ):    
    
    if selected == False or pt_layer.selectedFeatureCount() == 0:
        features = pt_layer.getFeatures()
    else:
        features = pt_layer.selectedFeatures()
            
    provider = pt_layer.dataProvider()    
    field_indices = [ provider.fieldNameIndex( field_name ) for field_name in fields ]

    # retrieve selected features with their geometry and relevant attributes
    rec_values_Lst2 = [] 
    for feature in features:             
        # fetch point geometry
        pt = feature.geometry().asPoint()
        attrs = feature.fields().toList() 
        # creates feature attribute list
        feat_list = [ pt.x(), pt.y() ]
        for field_ndx in field_indices:
            feat_list.append( str( feature.attribute( attrs[ field_ndx ].name() ) ) )
        # add to result list
        rec_values_Lst2.append( feat_list )
       
    field_names = ["x","y"] + fields
     
    return field_names, rec_values_Lst2


def qgs_point_2d( x, y ):
    
    return QgsPointXY(x, y)
        

def project_qgs_point( qgsPt, srcCrs, destCrs ):
    
    return QgsCoordinateTransform(srcCrs, destCrs, QgsProject.instance()).transform(qgsPt)

