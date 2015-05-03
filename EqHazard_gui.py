
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from EqHazard_QWidget import EqHazard_QWidget
import resources



class EqHazard_gui( object ):
    

    def __init__(self, interface):

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()        

        self.plugin_name = "EqHazard"
        

    def initGui(self):
        
        self.EqHazard_QAction = QAction(QIcon(":/plugins/EqHazard/icons/icon.png"), self.plugin_name, self.interface.mainWindow())
        self.EqHazard_QAction.setWhatsThis( "Import and plot of earthquake hazard data" ) 
        self.EqHazard_QAction.triggered.connect( self.open_EqHazard_widget )
        self.interface.addPluginToMenu(self.plugin_name, self.EqHazard_QAction)
        self.interface.addToolBarIcon(self.EqHazard_QAction)

        self.is_EqHazard_widget_open = False
                
        
    def open_EqHazard_widget(self):
        
        if self.is_EqHazard_widget_open:
            self.warn("%s is already open" % (self.plugin_name))
            return

        EqHazard_DockWidget = QDockWidget( self.plugin_name, self.interface.mainWindow() )        
        EqHazard_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        EqHazard_DockWidget.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )        
        self.EqHazard_QWidget = EqHazard_QWidget( self.canvas, self.plugin_name )        
        EqHazard_DockWidget.setWidget( self.EqHazard_QWidget )
        EqHazard_DockWidget.destroyed.connect( self.closeEvent )        
        self.interface.addDockWidget( Qt.BottomDockWidgetArea, EqHazard_DockWidget )
                
        self.is_EqHazard_widget_open = True
        

    def closeEvent(self):
        
        self.is_EqHazard_widget_open = False
                 

    def info(self, msg):
        
        QMessageBox.information( self.interface.mainWindow(),  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self.interface.mainWindow(),  self.plugin_name, msg )
        
                               
    def unload(self):

        self.interface.removeToolBarIcon(self.EqHazard_QAction)        
        self.interface.removePluginMenu( self.plugin_name, self.EqHazard_QAction )
     
        
               

