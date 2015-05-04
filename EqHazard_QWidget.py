# -*- coding: utf-8 -*-


import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsMapLayerRegistry
from geosurf.qgs_tools import loaded_point_layers, get_point_data


       
class EqHazard_QWidget( QWidget ):
    
    
    
    def __init__( self, canvas, plugin_name ):

        super( EqHazard_QWidget, self ).__init__() 
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name           
        self.setup_gui()

                      
    def setup_gui( self ): 

        self.dialog_layout = QHBoxLayout()
        
        self.dialog_layout.addWidget( self.setup_inputdata() )
        self.dialog_layout.addWidget( self.setup_processing() )        
                                                           
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(self.plugin_name)        
  

    def setup_inputdata(self):
        
        input_QGroupBox = QGroupBox("Input")
        
        layout = QVBoxLayout() 
        
        self.read_input_data_QPushButton = QPushButton(self.tr("Read input file"))  
        self.read_input_data_QPushButton.clicked.connect( self.get_input_data ) 
        layout.addWidget(self.read_input_data_QPushButton )
        
        input_QGroupBox.setLayout(layout)
        
        return input_QGroupBox
  
  
    def setup_processing(self):
        
        processing_QGroupBox = QGroupBox("Processing")
        
        layout = QGridLayout()

        self.plot_data_QPushButton = QPushButton(self.tr("Plot data"))          
        self.plot_data_QPushButton.clicked.connect( self.plot_geodata )         
        layout.addWidget(self.plot_data_QPushButton, 0, 0, 1, 1 )        
                
        processing_QGroupBox.setLayout(layout)
        
        return processing_QGroupBox
    

    def get_input_data( self ):
        
        
        dialog = SourceDataDialog()

        if dialog.exec_():
            try:
                input_data = self.extract_input_data( dialog )
            except:
                self.warn( "Error in input")
                return 
        else:
            self.warn( "Nothing defined")
            return


    def extract_input_data(self, dialog ):
        
        point_layer = dialog.point_layer
        
        field_undefined_txt = dialog.field_undefined_txt

        link_name_field = self.parse_field_choice(dialog.link_field_QComboBox.currentText(), field_undefined_txt)
            

        return point_layer, link_name_field 
    

    def parse_field_choice(self, val, choose_message):
        
        if val == choose_message:
            return None
        else:
            return val


    def process_geodata(self):
        
        pass
         

    def plot_geodata(self, input_data_types, structural_data):
        pass    
        
        
    def info(self, msg):
        
        QMessageBox.information( self,  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  self.plugin_name, msg )
        
        
        
class SourceDataDialog( QDialog ):
    
    
    def __init__(self, parent=None):
                
        super( SourceDataDialog, self ).__init__(parent)
        
        self.setup_gui()
        
        
    def setup_gui(self):        
        
        self.layer_choose_msg = "choose"
        self.field_undefined_txt = "---"
 
        layout = QGridLayout()
                        
        # input layer
        
        layer_QGroupBox = QGroupBox("Input point layer")
        layer_QGridLayout = QGridLayout() 
        
        self.input_layers_QComboBox = QComboBox()
        layer_QGridLayout.addWidget(self.input_layers_QComboBox, 0,0,1,2) 
        
        layer_QGroupBox.setLayout(layer_QGridLayout)              
        layout.addWidget(layer_QGroupBox, 0,0,1,2)          

        # link field
                
        linkfield_QGroupBox = QGroupBox("Link field")
        linkfield_QGridLayout = QGridLayout()    

        self.link_field_QComboBox = QComboBox()

        linkfield_QGridLayout.addWidget(self.link_field_QComboBox, 0,0,1,1)   

        linkfield_QGroupBox.setLayout(linkfield_QGridLayout)              
        layout.addWidget(linkfield_QGroupBox, 1,0,2,2)
             
                
        self.refresh_input_layer_combobox()
        
        self.input_layers_QComboBox.currentIndexChanged[int].connect (self.refresh_link_field_combobox )
        
        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
              
        layout.addLayout( buttonLayout, 5, 0, 1, 2 )
        
        self.setLayout( layout )

        self.connect(okButton, SIGNAL("clicked()"),
                     self,  SLOT("accept()") )
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))
        
        self.setWindowTitle("Define point structural layer")



    def refresh_input_layer_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()        
        
        self.input_layers_QComboBox.addItem( self.layer_choose_msg )
        self.input_layers_QComboBox.addItems( [ layer.name() for layer in self.pointLayers ] ) 
        
        self.reset_link_field_combobox()
         
         
    def reset_link_field_combobox(self):        
        

        self.link_field_QComboBox.clear()
        self.link_field_QComboBox.addItem(self.field_undefined_txt)
            
                     
    def refresh_link_field_combobox( self ):
        
        self.reset_link_field_combobox()

        point_shape_qgis_ndx = self.input_layers_QComboBox.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return
        
        self.point_layer = self.pointLayers[ point_shape_qgis_ndx ]
       
        point_layer_field_list = self.point_layer.dataProvider().fields().toList( ) 
               
        field_names = [field.name() for field in point_layer_field_list]
        
        self.link_field_QComboBox.addItems(field_names)

    
    
        


