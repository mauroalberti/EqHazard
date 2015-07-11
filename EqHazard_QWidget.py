# -*- coding: utf-8 -*-

from __future__ import division

import os
from math import ceil, floor

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsMapLayerRegistry

from geosurf.qgs_tools import loaded_point_layers, get_point_data
from geosurf.utils import is_number
from mpl.mpl_widget import MplMainWidget, plot_line


       
class EqHazard_QWidget( QWidget ):
    
      
    
    def __init__( self, canvas, plugin_name ):

        super( EqHazard_QWidget, self ).__init__() 
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name 
        
        self.input_field_undefined_txt = "---"
        
        self.plot_undefined_choice_txt = "not defined"
        self.plot_density_choice_txt = "density"
        self.plot_velocities_choice_txt = "velocities"
        self.plot_Qvalues_choice_txt = "Q values"
                
        self.config_plot_options = [self.plot_undefined_choice_txt,
                                   self.plot_density_choice_txt,
                                   self.plot_velocities_choice_txt,
                                   self.plot_Qvalues_choice_txt]
        
        self.thickness_field_name = "thk (km)"
        self.density_field_name = "rho"
        self.velocity_p_field_name = "Vp (km/s)"
        self.velocity_s_field_name = "Vs (km/s)"
        self.q_p_field_name = "Qp"                
        self.q_s_field_name = "Qs"  
        self.depth_field_name = "depth (km)"
        self.layer_field_name = "layer"
        
        self.time_field_name = "time"
        self.strongmotion_velocity_field_name = "velocity"
                
        self.layerinfo_input_field_names = [self.thickness_field_name,
                                  self.density_field_name,
                                  self.velocity_p_field_name,
                                  self.velocity_s_field_name,
                                  self.q_p_field_name,
                                  self.q_s_field_name,
                                  self.depth_field_name,
                                  self.layer_field_name]
        
        self.strongmotion_input_field_names = [self.time_field_name,
                                               self.strongmotion_velocity_field_name]
        
        
        self.plot_configs_ok = False
        
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
        self.read_input_data_QPushButton.clicked.connect( self.get_input_data_def ) 
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
    

    def get_input_data_def( self ):
                 
        def extract_input_info_data(dialog ):
            
            point_layer = dialog.point_layer        
            link_name_field = dialog.link_field_QComboBox.currentText()
                        
            if dialog.choice_layerinfo_input_QRadioButton.isChecked():            
                input_data_type = "layer info"
            elif dialog.choice_strongmotion_input_QRadioButton.isChecked():
                input_data_type = "strong motion"
            else:
                input_data_type = ""
              
            return point_layer, link_name_field, input_data_type    

        
        if len(loaded_point_layers()) == 0:
            self.warn("No point layer loaded")
            return
        
        dialog = InputLayerDialog(self.input_field_undefined_txt)

        if dialog.exec_():
            try:
                self.point_layer, self.link_name_field, self.input_data_type = extract_input_info_data( dialog )
                assert self.link_name_field != self.input_field_undefined_txt
                assert self.input_data_type in ("layer info", "strong motion")
            except:
                self.warn( "Input error")
                return 
        else:
            self.warn( "Nothing defined")
            return
        
        
        self.get_config_params()
            
            
    def get_config_params(self):        
        
        def extract_plot_layerinfo_config(dialog):
            
            bottom_variables = dialog.y_axis_label.currentText()
            top_variables = dialog.top_variables_QComboBox.currentText()       
            
            return bottom_variables, top_variables
        
        def extract_plot_strongmotion_config(dialog):
            
            y_axis_measure_type_label = dialog.y_axis_measure_type_label_QLineEdit.text()
            y_axis_measure_unit_label = dialog.y_axis_measure_unit_label_QLineEdit.text()            
            
            return y_axis_measure_type_label, y_axis_measure_unit_label
        
    
        if self.input_data_type == "layer info":
            dialog = PlotConfigDialog( self.config_plot_options )
        elif self.input_data_type == "strong motion":            
            dialog = StrongMotionConfigDialog()
        
        if dialog.exec_():
            if self.input_data_type == "layer info":
                try:
                    self.bottom_variables, self.top_variables = extract_plot_layerinfo_config(dialog)
                except:
                    self.warn("Error in plot configuration")
                    return
            elif self.input_data_type == "strong motion":  
                try:
                    self.y_axis_measure_type_label, self.y_axis_measure_unit_label = extract_plot_strongmotion_config(dialog)
                except:
                    self.warn("Error in plot configuration")
                    return                
                 
        else:
            self.warn("Undefined configuration")
            return
 
        if self.input_data_type == "layer info":       
            if self.bottom_variables == self.plot_undefined_choice_txt and \
               self.top_variables == self.plot_undefined_choice_txt:
                self.warn("No choice for plot configuration")
                self.plot_configs_ok = False
            elif self.bottom_variables == self.top_variables:
                self.warn("Choose different variables")
                self.plot_configs_ok = False            
            else:
                self.plot_configs_ok = True
    

    def read_hazard_input_file(self, file_path):
        
        def parse_hazard_input_data(in_data_list2):
            
            data_dict = {} # a dictionary that will contain the lists of values for each field
            
            for fld_name in fld_names:
                data_dict[fld_name] = []
            
            for rec_vals in in_data_list2:
                assert len(fld_names) == len(rec_vals)
                for fld_name, val in zip(fld_names, rec_vals):
                    data_dict[fld_name].append(float(val))
                    
            return data_dict


        def extract_number_start_ndx(indata_raw):
            
            for n, indata_row in enumerate(indata_raw):
                indata_vals = indata_row.split()
                are_numbers = map(is_number, indata_vals)
                if reduce(lambda a, b: a and b, are_numbers):
                    return n
            
        try:
            with open(file_path, "r") as ifile:
                indata_raw = ifile.readlines()
        except:
            self.warn("Unable to read input file: %s" % (file_path))
            return None        

        ifile_skip_lines = extract_number_start_ndx(indata_raw)
        in_data_vals = indata_raw[ifile_skip_lines:]
        
        if self.input_data_type == "layer info":
            fld_names = self.layerinfo_input_field_names
        elif self.input_data_type == "strong motion":
            fld_names = self.strongmotion_input_field_names        
        else:
            self.warn("Uncorrect plot type")
            return None              
   
                
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
                       

    def plot_geodata(self):
        
        def extract_data_names(ifile_paths):
            
            return [ifile_path.split(os.sep)[-1].split(".")[0] for ifile_path in ifile_paths]
    
        def get_subplot_code(n_recs, n_rec):
    
            n_rows = (n_recs + 1) / 2
            n_cols = 2
            
            subplot_code = int("%d%d%d" % (n_rows, n_cols, n_rec))
            return subplot_code
            
        try:
            point_layer, link_name_field, input_data_type = self.point_layer, self.link_name_field, self.input_data_type
        except:
            self.warn("Input data are not defined")
            return

        _, rec_values_Lst2 = get_point_data( point_layer, [link_name_field])
        ifile_paths = [rec_values[-1] for rec_values in rec_values_Lst2]
                
        geodata = []
        for ifile_path in ifile_paths:
            geodata_rec = self.read_hazard_input_file(ifile_path)
            if geodata_rec is None:
                return
            else:
                geodata.append(geodata_rec)
                
        assert len(geodata) > 0
        
        geodata_names = extract_data_names(ifile_paths)        
        
        plot_window = MplMainWidget()  # create plot window

        if input_data_type == "layer info":
            
            if not self.plot_configs_ok:
                self.warn("Undefined plot configurations")
                return
            else:
                bottom_variables, top_variables = self.bottom_variables, self.top_variables
                   
            # plot profiles
            for n, (geodata_unit, geodata_name) in enumerate(zip(geodata,geodata_names)): 
                subplot_code = get_subplot_code(len(geodata), n+1)
                 
                self.plot_layerinfo_data_unit(plot_window, 
                                               bottom_variables,
                                               top_variables, 
                                               geodata_unit,
                                               geodata_name, 
                                               subplot_code)
                
        elif input_data_type == "strong motion":
            
            # plot profiles
            for n, (geodata_unit, geodata_name) in enumerate(zip(geodata,geodata_names)): 
                subplot_code = get_subplot_code(len(geodata), n+1)
                
                self.plot_strongmotion_data_unit(plot_window,
                                               geodata_unit,
                                               geodata_name, 
                                               subplot_code)                
                
        else:
            
            self.warn("Uncorrect data type")
            return
        
            
        plot_window.canvas.draw() 
        
        self.plot_windows.append( plot_window )

        
    def plot_layerinfo_data_unit(self, plot_window, variables_x_btm, variables_x_top, geodata_unit, geodata_name, subplot_code):
    
        def get_data_range_int(data_list):
            
            if data_list is None:
                return None
            elif data_list == []:
                return None
            else:
                return 0, ceil(max(data_list))
            
        def variable_label(variable_x):
    
            density_label = "density [g/cm3]"
            velocity_label = "v [km/s]"
            Q_vals_label = "Q value"
                    
            if variable_x == self.plot_density_choice_txt:
                return density_label
            elif variable_x == self.plot_velocities_choice_txt:
                return velocity_label
            elif variable_x == self.plot_Qvalues_choice_txt:
                return Q_vals_label
            elif variable_x == self.plot_undefined_choice_txt:        
                return ""   
                
        def extract_values_range(variable_x, geodata_unit):
                    
            if variable_x == self.plot_density_choice_txt:
                return get_data_range_int( geodata_unit[self.density_field_name] )
            elif variable_x == self.plot_velocities_choice_txt:
                return get_data_range_int( geodata_unit[self.velocity_p_field_name] + geodata_unit[self.velocity_s_field_name])
            elif variable_x == self.plot_Qvalues_choice_txt:
                return get_data_range_int( geodata_unit[self.q_p_field_name] + geodata_unit[self.q_s_field_name])
            elif variable_x == self.plot_undefined_choice_txt:        
                return None
 
        def variable_legend_label(variable_x):
    
            density_legend = ["density"]
            velocity_legend = ["Vp", "Vs"]
            Q_vals_legend = ["Qp", "Qs"]
                    
            if variable_x == self.plot_density_choice_txt:
                return density_legend
            elif variable_x == self.plot_velocities_choice_txt:
                return velocity_legend
            elif variable_x == self.plot_Qvalues_choice_txt:
                return Q_vals_legend
            elif variable_x == self.plot_undefined_choice_txt:        
                return []  
          
        def create_plot_lines(axes, geodata_unit, variables, colors):
            
            def extract_values(geodata_unit, variables):
                
                if variables == self.plot_density_choice_txt:
                    return [geodata_unit[self.density_field_name]]
                elif variables == self.plot_velocities_choice_txt:
                    return [geodata_unit[self.velocity_p_field_name], geodata_unit[self.velocity_s_field_name]]
                elif variables == self.plot_Qvalues_choice_txt:
                    return [geodata_unit[self.q_p_field_name], geodata_unit[self.q_s_field_name]]  
                else:
                    return []  
            
            var_values = extract_values(geodata_unit, variables)
            variable_y = geodata_unit[self.depth_field_name]   
            lines = []
            for variable_x, color in zip(var_values, colors):
                lines.append( plot_line(axes,
                             variable_x, 
                             variable_y, 
                             color,
                             drawstyle = "steps-pre") )

            return lines   
            
        def create_axes(subplot_code, plot_window, geodata_name, plot_x_range, plot_y_range ):
    
            axes = plot_window.canvas.fig.add_subplot( subplot_code )
            
            y_min, y_max = plot_y_range
            axes.set_ylim( y_min, y_max )        
            if plot_x_range is not None:
                x_min, x_max = plot_x_range
                axes.set_xlim( x_min, x_max )
    
            axes.set_title(geodata_name,  y=1.40)
            axes.grid(True)
                               
            return axes
                    
        depth_label = "depth [km]"
        
        var_x_btm_label = variable_label( variables_x_btm)
        var_x_top_label = variable_label( variables_x_top)
        
        plot_x_btm_range = extract_values_range(variables_x_btm, geodata_unit)          
        plot_x_top_range = extract_values_range(variables_x_top, geodata_unit)
        
        plot_y_range = get_data_range_int(geodata_unit[self.depth_field_name]) 
            
        btm_axes = create_axes( subplot_code,
                              plot_window, 
                              geodata_name,
                              plot_x_btm_range, 
                              plot_y_range  )             
              
        btm_axes.set_xlabel(var_x_btm_label)
        btm_axes.set_ylabel(depth_label) 

        btm_axes.invert_yaxis()         
        plot_window.canvas.fig.tight_layout(pad=0.1, w_pad=0.05, h_pad=1.0)
        
        colors_x_btm = ["orange", "green"]
        bottom_lines = create_plot_lines(btm_axes, geodata_unit, variables_x_btm, colors_x_btm)

 
        if plot_x_top_range is not None:
            top_axes = btm_axes.twiny()
            top_axes.set_xlim( *plot_x_top_range )
            top_axes.set_xlabel(var_x_top_label)
            colors_x_top = ["red", "blue"]
            top_lines = create_plot_lines(top_axes, geodata_unit, variables_x_top, colors_x_top)


        var_x_btm_legend_label = variable_legend_label( variables_x_btm)
        var_x_top_legend_label = variable_legend_label( variables_x_top) 
 
        if plot_x_top_range is None:
            plot_window.canvas.fig.legend(bottom_lines, var_x_btm_legend_label)
        else:
            plot_window.canvas.fig.legend(bottom_lines + top_lines, var_x_btm_legend_label + var_x_top_legend_label)            
    
    
    def plot_strongmotion_data_unit(self, plot_window, geodata_unit, geodata_name, subplot_code):        
    
        def get_data_range_int(data_list):
            
            if data_list is None:
                return None
            elif data_list == []:
                return None
            else:
                return floor(min(data_list)), ceil(max(data_list))
 
        def get_data_range_float(data_list):
            
            if data_list is None:
                return None
            elif data_list == []:
                return None
            else:                
                return floor(min(data_list)*10)/10, ceil(max(data_list)*10)/10
            
        def create_plot_line(axes, geodata_unit):
            
            variable_x = geodata_unit[self.time_field_name]  
            variable_y = geodata_unit[self.strongmotion_velocity_field_name]  
            plot_line(axes,
                     variable_x, 
                     variable_y, 
                     "blue")
            
        def create_axes(subplot_code, plot_window, geodata_name, plot_time_range, plot_velocity_range):
    
            axes = plot_window.canvas.fig.add_subplot(subplot_code)

            x_min, x_max = plot_time_range
            axes.set_xlim( x_min, x_max )
                        
            y_min, y_max = plot_velocity_range
            axes.set_ylim( y_min, y_max )        
    
            axes.set_title(geodata_name,  y=1.40)
            axes.grid(True)
                               
            return axes
                    
        time_label = "time [sec]"        
        y_axis_label = self.y_axis_measure_type_label + " [" + self.y_axis_measure_unit_label + "]"

        plot_time_range = get_data_range_int(geodata_unit[self.time_field_name])       
        plot_velocity_range = get_data_range_float( geodata_unit[self.strongmotion_velocity_field_name] )  
 
        plot_axes = create_axes( subplot_code,
                              plot_window, 
                              geodata_name,
                              plot_time_range,
                              plot_velocity_range)             
              
        plot_axes.set_xlabel(time_label)
        plot_axes.set_ylabel(y_axis_label) 
      
        plot_window.canvas.fig.tight_layout(pad=0.1, w_pad=0.05, h_pad=1.0)

        create_plot_line(plot_axes, geodata_unit)
         
        
    def info(self, msg):
        
        QMessageBox.information( self,  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  self.plugin_name, msg )
        
        
        
class InputLayerDialog( QDialog ):
    
    
    def __init__(self, input_field_undefined_txt, parent=None):
                
        super( InputLayerDialog, self ).__init__(parent)
        
        self.field_undefined_txt = input_field_undefined_txt
        
        self.setup_gui()
        
        
    def setup_gui(self):        
        
        self.layer_choose_msg = "choose"
 
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

        linkfield_QGridLayout.addWidget(self.link_field_QComboBox, 0,0,1,2)   
        
        self.choice_layerinfo_input_QRadioButton = QRadioButton("Layer info")
        self.choice_layerinfo_input_QRadioButton.setChecked(True)

        linkfield_QGridLayout.addWidget(self.choice_layerinfo_input_QRadioButton, 1,0,1,1)   
        
        self.choice_strongmotion_input_QRadioButton = QRadioButton("Strong motion")
        linkfield_QGridLayout.addWidget(self.choice_strongmotion_input_QRadioButton, 1,1,1,1)          
        

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
        
        self.setWindowTitle("Source layer")



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

   
    
  

class PlotConfigDialog( QDialog ):
    
        
            
    def __init__(self, config_plot_options, parent=None):
                
        super( PlotConfigDialog, self ).__init__(parent)
        
        self.config_plot_options = config_plot_options
        
        self.setup_gui()
        
        
    def setup_gui(self):        
        
 
        layout = QGridLayout()
                        
        # plot variables
        
        variables_QGroupBox = QGroupBox("Variables to plot")
        variables_QGridLayout = QGridLayout() 

        variables_QGridLayout.addWidget(QLabel("Variable(s)"), 0,0,1,1)         
        self.y_axis_label = QComboBox()
        variables_QGridLayout.addWidget(self.y_axis_label, 0,1,1,1) 
  
        variables_QGridLayout.addWidget(QLabel("Additional variable(s)"), 1,0,1,1)         
        self.top_variables_QComboBox = QComboBox()
        variables_QGridLayout.addWidget(self.top_variables_QComboBox, 1,1,1,1) 
              
        variables_QGroupBox.setLayout(variables_QGridLayout)              
        layout.addWidget(variables_QGroupBox, 0,0,1,2)          
   
        self.populate_config_plot_combobox()
        
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
        
        self.setWindowTitle("Plot variables")



    def populate_config_plot_combobox(self):
        
        self.y_axis_label.insertItems(0, self.config_plot_options[1:])
        self.top_variables_QComboBox.insertItems(0, self.config_plot_options) 
              


class StrongMotionConfigDialog( QDialog ):
    
            
    def __init__(self, parent=None):
                
        super( StrongMotionConfigDialog, self ).__init__(parent)
        
        self.setup_gui()
        
        
    def setup_gui(self):        
        
        default_measure_type_label = "velocity"
        default_measure_unit_label = "km/sec"
        
        layout = QGridLayout()
                        
        # plot variables
        
        axeslabel_QGroupBox = QGroupBox("Y axis labels")
        axeslabel_QGridLayout = QGridLayout() 

        axeslabel_QGridLayout.addWidget(QLabel("y-axis measure type"), 0,0,1,1)         
        self.y_axis_measure_type_label_QLineEdit = QLineEdit(default_measure_type_label)
        axeslabel_QGridLayout.addWidget(self.y_axis_measure_type_label_QLineEdit, 0,1,1,1) 

        axeslabel_QGridLayout.addWidget(QLabel("y-axis measure unit"), 1,0,1,1)         
        self.y_axis_measure_unit_label_QLineEdit = QLineEdit(default_measure_unit_label)
        axeslabel_QGridLayout.addWidget(self.y_axis_measure_unit_label_QLineEdit, 1,1,1,1)           
              
        axeslabel_QGroupBox.setLayout(axeslabel_QGridLayout)              
        layout.addWidget(axeslabel_QGroupBox, 0,0,1,2)          
        
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
        
        self.setWindowTitle("Axes labels")

              


        
        


