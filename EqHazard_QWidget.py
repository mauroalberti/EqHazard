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
        
        plane_azimuth_type = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()
        plane_azimuth_name_field = self.parse_field_choice(dialog.input_plane_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
            
        plane_dip_type = dialog.input_plane_orient_dip_type_QComboBox.currentText()        
        plane_dip_name_field = self.parse_field_choice(dialog.input_plane_dip_srcfld_QComboBox.currentText(), field_undefined_txt)       
                    
        line_azimuth_type = dialog.input_line_orient_azimuth_type_QComboBox.currentText()
        line_azimuth_name_field = self.parse_field_choice( dialog.input_line_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
                    
        line_dip_type = dialog.input_line_orient_dip_type_QComboBox.currentText()        
        line_dip_name_field = self.parse_field_choice( dialog.input_line_dip_srcfld_QComboBox.currentText(), field_undefined_txt)
        
        return point_layer, dict(plane_azimuth_type = plane_azimuth_type,
                                plane_azimuth_name_field = plane_azimuth_name_field,
                                plane_dip_type = plane_dip_type,
                                plane_dip_name_field = plane_dip_name_field,
                                line_azimuth_type = line_azimuth_type,
                                line_azimuth_name_field = line_azimuth_name_field,
                                line_dip_type = line_dip_type,
                                line_dip_name_field = line_dip_name_field)
    

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

        # plane values
                
        plane_QGroupBox = QGroupBox("Planar orientation source fields")
        plane_QGridLayout = QGridLayout()    

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()

        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_plane_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_azimuth_srcfld_QComboBox, 0,1,1,1)       
 
        self.input_plane_orient_dip_type_QComboBox = QComboBox()

        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1,0,1,1) 
        
        self.input_plane_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_dip_srcfld_QComboBox, 1,1,1,1)         

        plane_QGroupBox.setLayout(plane_QGridLayout)              
        layout.addWidget(plane_QGroupBox, 1,0,2,2)
        

        # line values
        
        line_QGroupBox = QGroupBox("Line orientation source fields")
        line_QGridLayout = QGridLayout() 
        
        self.input_line_orient_azimuth_type_QComboBox = QComboBox()

        line_QGridLayout.addWidget(self.input_line_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_line_azimuth_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_azimuth_srcfld_QComboBox, 0,1,1,1)    
        
        self.input_line_orient_dip_type_QComboBox = QComboBox()

        line_QGridLayout.addWidget(self.input_line_orient_dip_type_QComboBox, 1,0,1,1) 
        
        self.input_line_dip_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_dip_srcfld_QComboBox, 1,1,1,1)         
 
        line_QGroupBox.setLayout(line_QGridLayout)              
        layout.addWidget(line_QGroupBox, 3,0,2,2)
         
 
        self.structural_comboxes = [self.input_plane_azimuth_srcfld_QComboBox,
                                    self.input_plane_dip_srcfld_QComboBox,
                                    self.input_line_azimuth_srcfld_QComboBox,
                                    self.input_line_dip_srcfld_QComboBox ]                
                
        self.refresh_struct_point_lyr_combobox()
        
        self.input_layers_QComboBox.currentIndexChanged[int].connect (self.refresh_structural_fields_comboboxes )
        
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



    def refresh_struct_point_lyr_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()        
        
        self.input_layers_QComboBox.addItem( self.layer_choose_msg )
        self.input_layers_QComboBox.addItems( [ layer.name() for layer in self.pointLayers ] ) 
        
        self.reset_structural_field_comboboxes()
         
         
    def reset_structural_field_comboboxes(self):        
        
        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem(self.field_undefined_txt)
            
                     
    def refresh_structural_fields_comboboxes( self ):
        
        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.input_layers_QComboBox.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return
        
        self.point_layer = self.pointLayers[ point_shape_qgis_ndx ]
       
        point_layer_field_list = self.point_layer.dataProvider().fields().toList( ) 
               
        field_names = [field.name() for field in point_layer_field_list]
        
        for structural_combox in self.structural_comboxes:
            structural_combox.addItems(field_names)

    
    
        


