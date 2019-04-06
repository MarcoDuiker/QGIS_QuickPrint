# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickPrint3
                                 A QGIS plugin
 The QuickPrint Plugin for QGIS3
                              -------------------
        begin                : 2018-01-15
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Marco Duiker MD-kwadraat
        email                : info@md-kwadraat.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import Qt, QSettings, QTranslator, qVersion, QCoreApplication, QRectF, QUrl
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .quick_print3_dialog import QuickPrint3Dialog
from .quick_print3_settings_dialog import QuickPrint3SettingsDialog

import os.path
import time
import sys
import subprocess
import webbrowser

__author__ = 'Marco Duiker MD-kwadraat'
__date__ = 'Februari 2019'

class QuickPrint3:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # get the settings
        self.settings = QSettings()
        self.dateFormatString = self.settings.value("QuickPrint/date_format_string", "{day}-{month}-{year}")
        self.logoImagePath = self.settings.value("QuickPrint/logo_path", "")
        if not self.logoImagePath \
        and os.path.exists(os.path.join(self.plugin_dir, 'img', 'logo.png')):
            self.logoImagePath = os.path.join(self.plugin_dir, 'img', 'logo.png')
        self.textFont = self.settings.value("QuickPrint/text_font", "Arial")
        self.fontSize = int(self.settings.value("QuickPrint/font_size", 100))
        
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QuickPrint3_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QuickPrint3Dialog()
        self.settings_dlg = QuickPrint3SettingsDialog()

        # add some necessary signal and slot communication as well as disable the save button for now  
        self.dlg.cancel_save_button_box.button(QDialogButtonBox.Save).setEnabled(False)

        self.dlg.fileBrowseButton.clicked.connect(self.chooseFile)
        self.dlg.pdfFileNameBox.textChanged.connect(self.pdfFileNameBoxChanged)
        
        self.settings_dlg.fileBrowseButton.clicked.connect(self.choose_logo_file)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QuickPrint')
        
        self.toolbar = self.iface.addToolBar(u'QuickPrint')
        self.toolbar.setObjectName(u'QuickPrint')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """

        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QuickPrint', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:                     # if we use addPluginToMenu, 
            self.iface.addPluginToWebMenu(  # the toolbar is added to the plugins toolbar
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/QuickPrint3/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QuickPrint'),
            callback=self.run,
            parent=self.iface.mainWindow())
            
        icon_path = ':/plugins/QuickPrint3/settings.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Settings'),
            callback=self.run_settings,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)
            
        icon_path = ':/plugins/QuickPrint3/help.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Help'),
            callback=self.help,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QuickPrint'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def getPaperSize(self):
        '''
        Get's paper size from dialog
        '''

        paperSize = 'A4'
        longSide = 297
        shortSide = 210
        if self.dlg.a3Btn.isChecked():
            paperSize = 'A3'
            longSide = 420
            shortSide = 297

        paperOrientation = 'portrait'
        width = shortSide
        height = longSide
        if self.dlg.landschapBtn.isChecked():
            paperOrientation = 'landscape'
            width = longSide
            height = shortSide

        return width, height

    def chooseFile(self):
        '''
        shows file chooser
        '''

        fileName, __ = QFileDialog.getSaveFileName(caption = self.tr(u"save pdf"), directory = '', filter = '*.pdf')
        self.dlg.pdfFileNameBox.setText(fileName)
        
    def pdfFileNameBoxChanged(self, fileName):
        '''
        acts when file name in dialog has changed
        '''

        if os.path.exists(os.path.dirname(fileName)):
            self.dlg.cancel_save_button_box.button(QDialogButtonBox.Save).setEnabled(True)

    def help(self):
        '''
        acts on help button on dialog
        '''

        QDesktopServices().openUrl(QUrl.fromLocalFile(os.path.join("file://",
            self.plugin_dir, 'help/build/html','index.html')))
        #webbrowser.open_new(os.path.join("file://",os.path.abspath(self.plugin_dir), 'help/build/html','index.html')) 

    def choose_logo_file(self):
        '''
        Allows the user to choose a local path for the logo.
        '''
        
        path = QFileDialog.getOpenFileName(
                    caption = self.tr(u"Select Logo image file:"), 
                    directory = self.plugin_dir, 
                    filter = self.tr(u"Images (*.png *.jpg)"))[0]       
        self.settings_dlg.logo_path_ldt.setText(path)
        

    def run_settings(self):
        '''
        method showing the settings dialog and act on the results
        '''
        
        if not self.logoImagePath:
            self.settings_dlg.logo_path_ldt.setPlaceholderText("https://")
        self.settings_dlg.logo_path_ldt.setText(self.logoImagePath)
        self.settings_dlg.date_format_ldt.setText(self.dateFormatString)
        self.settings_dlg.fontComboBox.setCurrentFont(QFont(self.textFont))
        self.settings_dlg.font_size_sld.setValue(int(self.fontSize))

        self.settings_dlg.show()
        
        result = self.settings_dlg.exec_()
        if result:
            path = unicode(self.settings_dlg.logo_path_ldt.text())
            if path[0:4] == 'http':
                # urlEncode?
                pass
            else:
                # make more canonical?
                pass
            self.logoImagePath = path
            self.settings.setValue("QuickPrint/logo_path", self.logoImagePath)
            
            self.dateFormatString = unicode(self.settings_dlg.date_format_ldt.text())
            self.settings.setValue("QuickPrint/date_format_string", self.dateFormatString)
        
            self.textFont = self.settings_dlg.fontComboBox.currentFont().family()
            self.settings.setValue("QuickPrint/text_font", self.textFont)
            
            self.fontSize = self.settings_dlg.font_size_sld.value()
            self.settings.setValue("QuickPrint/font_size", self.fontSize)
            
    def run(self):
        '''
        methods doing most of the work.
        shows the dialog, and acts on the result.
        '''

        self.dlg.show()
        result = self.dlg.exec_()
        if result:

            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            
            font_scale = float(self.fontSize) / 100

            dpi = 600
            # get the users input 
            titel = self.dlg.titelFld.text()
            subTitel = self.dlg.subTitelFld.text()
    
            bronnen = self.dlg.bronnenFld.toPlainText()
            opmerkingen = self.dlg.opmerkingenFld.toPlainText ()

            project = QgsProject.instance()
            l = QgsPrintLayout(project)
            l.initializeDefaults()
            l.setUnits(QgsUnitTypes.LayoutMillimeters)
            page = l.pageCollection().pages()[0]
            
            paperSize = self.getPaperSize()
            page.setPageSize(QgsLayoutSize(paperSize[0],paperSize[1]))

            # add gadgets
            # but first get margins and paper size right
            lm = 10         # left margin
            tm = 30         # upper margin
            bm = 65         # lower margin
            
            refSize = paperSize[0]
            if paperSize[1] < refSize:
                refSize = paperSize[1]

            # add map
            x, y = lm, tm
            w, h = paperSize[0] -  2 * lm, paperSize[1] - bm
            
            theMap = QgsLayoutItemMap(l)
            theMap.updateBoundingRect()
            theMap.setRect(QRectF(x, y, w, h)) 
            theMap.setPos(x,y)
            theMap.setFrameEnabled(True)
            
            # project.mapLayers().values():
            theMap.setLayers(project.mapThemeCollection().masterVisibleLayers())   # remember ANNOTATION!
            theMap.setExtent(self.iface.mapCanvas().extent())
            theMap.attemptSetSceneRect(QRectF(x, y, w, h))
            l.addItem(theMap)
            
            # add title
            titleFont = QFont(self.textFont, int(font_scale * 14))
            titleFont.setBold(True)

            titelLabel = QgsLayoutItemLabel(l)
            titelLabel.setText(titel)
            titelLabel.setPos(lm,10)
            titelLabel.setFont(titleFont)    
            titelLabel.adjustSizeToText()
            l.addItem(titelLabel)

            # add subtitle
            subTitleFont = QFont(self.textFont, int(font_scale * 12))
            subTitleFont.setBold(False)
                
            subTitelLabel = QgsLayoutItemLabel(l)
            subTitelLabel.setText(subTitel)
            subTitelLabel.setPos(lm, 20)
            subTitelLabel.setFont(subTitleFont)	    
            subTitelLabel.adjustSizeToText()
            l.addItem(subTitelLabel)  

            textFont = QFont(self.textFont, int(font_scale * 10))  

            # add logo
            
            if self.logoImagePath:
                try:
                    logo = QgsLayoutItemPicture(l)
                    logo.setPicturePath(self.logoImagePath)
                    logo.attemptSetSceneRect(QRectF((paperSize[0] - paperSize[0] / 3), 0, refSize / 3, refSize / 3 * 756 / 2040 )) 
                    # logo.setFrameEnabled(True)
                    l.addItem(logo)
                except:
                    # failed to add the logo, show message and continue
                    self.iface.messageBar().pushMessage("Warning", self.tr(u"Failed adding logo ") + \
                                                        self.logoImagePath, 
                                                        Qgis.Warning)

            #add date
            dateLabel = QgsLayoutItemLabel(l)
            d = time.localtime()
            #dString = "%d-%d-%d" % (d[2],  d[1],  d[0])
            dString = self.dateFormatString.format(day = d[2], month = d[1], year = d[0])
            dateLabel.setText(dString)
            dateLabel.setFont(textFont)
            dateLabel.adjustSizeToText()
            dateStringWidth = dateLabel.sizeForText().width()
            dateLabel.setPos(paperSize[0] - lm - dateStringWidth -5, (paperSize[1] - bm) + tm + 5)
            l.addItem(dateLabel)
                
            # add scalebar
            scaleBar = QgsLayoutItemScaleBar(l)
            scaleBar.setLinkedMap(theMap)
            scaleBar.applyDefaultSettings()
            scaleBar.applyDefaultSize()
            # scaleBar.setStyle('Line Ticks Down') 
            scaleBar.setNumberOfSegmentsLeft(0)
            scaleBar.setNumberOfSegments (3)
            scaleBar.update()
            scaleBar.setPos(lm + 10, tm + (paperSize[1] - bm) - 20 )
            l.addItem(scaleBar)

            # add attribution
            bronnenLabel = QgsLayoutItemLabel(l)
            bronnenLabel.setText(bronnen)
            bronnenLabel.setFont(textFont)
            bronnenLabel.adjustSizeToText()	        # Doesn't work for multiline stuff, hence:
            bronnenLabel.attemptSetSceneRect(QRectF(lm, (paperSize[1] - bm) + tm + 5, paperSize[0] - lm - dateStringWidth -5 -lm -lm, paperSize[1] - ((paperSize[1] - bm) + tm + 5) - 10 ))    
            l.addItem(bronnenLabel)

            # add remarks
            opmLabel = QgsLayoutItemLabel(l)
            opmLabel.setText(opmerkingen)
            opmLabel.setFont(textFont)
            opmLabel.adjustSizeToText()	            # Doesn't work for multiline stuff, hence:
            opmLabel.attemptSetSceneRect(QRectF(lm, paperSize[1] - 10, paperSize[0] - lm -lm , 400 )) 
            l.addItem(opmLabel)
            
            # export pdf
            exporter =  QgsLayoutExporter(l)
            pdf_settings = exporter.PdfExportSettings() #dpi?
            exporter.exportToPdf(self.dlg.pdfFileNameBox.displayText(), pdf_settings)

            # inform the user about the result
            self.iface.messageBar().pushMessage("Info", self.tr(u"Saved as pdf: ") + \
                                                self.dlg.pdfFileNameBox.displayText(),
                                                Qgis.Info)
            # and if user wants so open the file
            if self.dlg.openAfterSaveBox.isChecked():
                if sys.platform.startswith('linux'):
                    subprocess.call(["xdg-open", self.dlg.pdfFileNameBox.displayText()])
                else:
                    # windows only
                    os.startfile(self.dlg.pdfFileNameBox.displayText())

            QGuiApplication.restoreOverrideCursor()
