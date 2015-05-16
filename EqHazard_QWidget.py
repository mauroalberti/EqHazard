# -*- coding: utf-8 -*-


import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsMapLayerRegistry
from geosurf.qgs_tools import loaded_point_layers, get_point_data

from mpl.mpl_widget import MplMainWidget, plot_line


       
class EqHazard_QWidget( QWidget ):
    
    layer_info_types = [("thk (km)", "float"), 
                        ("rho", "float"), 
                        ("Vp (km/s)", "float"), 
                        ("Vs (km/s)", "float"), 
                        ("Qp", "float"), 
                        ("Qs", "float"), 
                        ("depth (km)", "float"), 
                        ("layer", "int")]
    
    
    def __init__( self, canvas, plugin_name ):

        super( EqHazard_QWidget, self ).__init__() 
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name    
        
        self.plot_windows = []
               
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
        
        if len(loaded_point_layers()) == 0:
            self.warn("No point layer loaded")
            return
        
        dialog = SourceDataDialog()

        if dialog.exec_():
            try:
                self.point_layer, self.link_name_field = self.extract_input_data( dialog )
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
         

    def plot_geodata(self):
        
        try:
            point_layer, link_name_field = self.point_layer, self.link_name_field
        except:
            self.warn("Input data are not defined")
            return
        
        _, rec_values_Lst2 = get_point_data( point_layer, [link_name_field])
        ifile_paths = [rec_values[-1] for rec_values in rec_values_Lst2]
        
        geodata = [self.read_hazard_input_file(ifile_path) for ifile_path in ifile_paths]

        # create plot window
        plot_window = MplMainWidget()  
        
        for n, geodata_unit in enumerate(geodata): 
            subplot_code = self.get_subplot_code(len(geodata), n+1) 
            self.plot_geodata_unit(plot_window, geodata_unit, subplot_code)
            
        plot_window.canvas.draw() 
        
        self.plot_windows.append( plot_window )


    def get_subplot_code(self, n_recs, n_rec):

        n_rows = (n_recs + 1) / 2
        n_cols = 2
        
        subplot_code = int("%d%d%d" % (n_rows, n_cols, n_rec))
        return subplot_code
        
        
    def read_hazard_input_file(self, file_path):
        
        def parse_hazard_input_data(in_data_list2):
            
            data_dict = {} # a dict that will contain the lists of values for each field
            
            for fld_name in fld_names:
                data_dict[fld_name] = []
            
            for rec_vals in in_data_list2:
                assert len(fld_names) == len(rec_vals)
                for fld_name, val in zip(fld_names, rec_vals):
                    data_dict[fld_name].append(float(val))
                    
            return data_dict

        
        with open(file_path, "r") as ifile:
            in_data = ifile.readlines()
          
        ifile_skip_lines = 3  
        in_data_vals = in_data[ifile_skip_lines:]
        
        fld_names = [rec[0] for rec in EqHazard_QWidget.layer_info_types]
        flds_num = len(fld_names)
        in_data_list2 = []        
        for n, in_data_val in enumerate(in_data_vals):
            rec_vals = in_data_val.split()
            if len(rec_vals) != flds_num:
                self.warn("Rec # %d in file %s has only %d values instead of %d required" % \
                          (ifile_skip_lines + n + 1,
                          file_path,
                          len(rec_vals),
                          flds_num))
                return None
            in_data_list2.append(rec_vals)
            
        if len(in_data_list2) == 0:
                self.warn("No recs found in file %s" % (file_path))
                return None            
        else:
            return parse_hazard_input_data(in_data_list2)
                

    def create_axes(self, subplot_code, plot_window, plot_x_range, plot_y_range ):

            x_min, x_max = plot_x_range
            print x_min, x_max
            y_min, y_max = plot_y_range
            print y_min, y_max
            axes = plot_window.canvas.fig.add_subplot( subplot_code )
            axes.set_xlim( x_min, x_max )
            axes.set_ylim( y_min, y_max )

            axes.grid(True)
                       
            return axes
        
        
    def plot_geodata_unit(self, plot_window, geodata_unit, subplot_code):
        
        plot_x_range = self.get_data_range(geodata_unit["depth (km)"])
        plot_v_range = self.get_data_range(geodata_unit["Vp (km/s)"] + geodata_unit["Vs (km/s)"])
        axes = self.create_axes( subplot_code,
                                  plot_window, 
                                  plot_x_range, 
                                  plot_v_range  )        

        return axes
       
        
    def get_data_range(self, data_list):
        
        return 0, (max(data_list)/10 + 1)*10
        
                
        
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
        
        self.input_layers_QComboBox.currentIndexChanged[int].connect(self.refresh_link_field_combobox )
        
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

    
    
        


