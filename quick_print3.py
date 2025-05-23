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
from PyQt5.QtCore import Qt, QTranslator, qVersion, \
                         QCoreApplication, QRectF, QUrl
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
        self.settings = QgsSettings()
        self.dateFormatString = self.settings.value(
                "QuickPrint/date_format_string", "{day}-{month}-{year}")
        self.logoImagePath = self.settings.value("QuickPrint/logo_path", "")
        self.northArrowImagePath = self.settings.value("QuickPrint/north_arrow_path", "")
        if not self.northArrowImagePath :
            self.northArrowImagePath = os.path.join(self.plugin_dir, "north-arrow.svg")
        if not self.logoImagePath \
        and os.path.exists(os.path.join(self.plugin_dir, 'img', 'logo.png')):
            self.logoImagePath = os.path.join(self.plugin_dir, 'img', 'logo.png')
        self.textFont = self.settings.value("QuickPrint/text_font", "Arial")
        self.fontSize = int(self.settings.value("QuickPrint/font_size", 100))
        self.paper_size_standard = self.settings.value(
                "QuickPrint/paper_size_standard", "DIN")
        self.default_bronnen = self.settings.value("QuickPrint/attribution", self.tr("Attribution:"))
        self.default_opmerking = self.settings.value("QuickPrint/remark", "")
        
        # initialize locale
        locale = QgsSettings().value('locale/userLocale')[0:2]
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

        # add some necessary signal and slot communication as well 
        # as disable the save button for now  
        self.dlg.cancel_save_button_box.button(QDialogButtonBox.Save).setEnabled(False)
        
        self.dlg.file_name_qfw.setFilter('*.pdf,*.png')
        self.dlg.file_name_qfw.fileChanged.connect(self.fileNameBoxChanged)
        
        self.dlg.preview_gbx.collapsedStateChanged.connect(self.preview_toggled)
        
        #update the preview when the mapcanvas has changed or the
        #dialog is resized or changed
        self.iface.mapCanvas().renderComplete.connect(self.update_preview)
        self.dlg.preview_lbl.resizeEvent = self.update_preview
        self.dlg.logo_cbx.stateChanged.connect(self.update_preview)
        self.dlg.northarrow_cbx.stateChanged.connect(self.update_preview)
        self.dlg.a4Btn.toggled.connect(self.update_preview)
        self.dlg.portretBtn.toggled.connect(self.update_preview)
        self.dlg.titelFld.textChanged.connect(self.update_preview)
        self.dlg.subTitelFld.textChanged.connect(self.update_preview)
        self.dlg.bronnenFld.textChanged.connect(self.update_preview)
        self.dlg.opmerkingenFld.textChanged.connect(self.update_preview)
        
        # settings
        self.settings_dlg.fileBrowseButton.clicked.connect(self.choose_logo_file)
        self.settings_dlg.fileBrowseButton_2.clicked.connect(self.choose_north_arrow_file)
        
        # change the labels according to paper size standard
        if self.paper_size_standard == "DIN":
            self.dlg.a4Btn.setText("A4")
            self.dlg.a3Btn.setText("A3")
        else:
            self.dlg.a4Btn.setText("ANSI-A")
            self.dlg.a3Btn.setText("ANSI-B")

        # apply default remark and attribution if necessary
        if not self.dlg.bronnenFld.toPlainText():
            self.dlg.bronnenFld.setPlainText(self.default_bronnen)
        if not self.dlg.opmerkingenFld.toPlainText():
            self.dlg.opmerkingenFld.setPlainText(self.default_opmerking)

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
            self.iface.addPluginToWebMenu(  # toolbar is added to plugins toolbar
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

        # paperSize = 'A4'
        longSide = 297
        shortSide = 210
        if self.paper_size_standard == "ANSI":
            longSide = 279
            shortSide = 216
        if self.dlg.a3Btn.isChecked():
            # paperSize = 'A3'
            longSide = 420
            shortSide = 297
            if self.paper_size_standard == "ANSI":
                longSide = 432
                shortSide = 279

        # paperOrientation = 'portrait'
        width = shortSide
        height = longSide
        if self.dlg.landschapBtn.isChecked():
            # paperOrientation = 'landscape'
            width = longSide
            height = shortSide

        return width, height
        
    def fileNameBoxChanged(self, fileName):
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
        #webbrowser.open_new(os.path.join("file://",
        #   os.path.abspath(self.plugin_dir), 'help/build/html','index.html')) 

    def choose_logo_file(self):
        '''
        Allows the user to choose a local path for the logo.
        '''
        
        path = QFileDialog.getOpenFileName(
                    caption = self.tr(u"Select Logo image file:"), 
                    directory = self.plugin_dir, 
                    filter = self.tr(u"Images (*.png *.jpg)"))[0]       
        self.settings_dlg.logo_path_ldt.setText(path)
        
    def choose_north_arrow_file(self):
        '''
        Allows the user to choose a local path for the north arrow.
        '''
        
        path = QFileDialog.getOpenFileName(
                caption = self.tr(u"Select north arrow image file:"), 
                directory = self.plugin_dir, 
                filter = self.tr(u"Images (*.png *.jpg *.svg)"))[0]       
        self.settings_dlg.north_arrow_path_ldt.setText(path)
        

    def run_settings(self):
        '''
        method showing the settings dialog and act on the results
        '''
        
        if not self.logoImagePath:
            self.settings_dlg.logo_path_ldt.setPlaceholderText("https://")
        if not self.northArrowImagePath:
            self.settings_dlg.north_arrow_path_ldt.setPlaceholderText("https://")
        self.settings_dlg.logo_path_ldt.setText(self.logoImagePath)
        self.settings_dlg.north_arrow_path_ldt.setText(self.orthArrowImagePath)
        
        self.settings_dlg.date_format_ldt.setText(self.dateFormatString)
        self.settings_dlg.fontComboBox.setCurrentFont(QFont(self.textFont))
        self.settings_dlg.font_size_sld.setValue(int(self.fontSize))
        self.settings_dlg.default_attribition_tbx.setPlainText(self.default_bronnen)
        self.settings_dlg.default_remark_ldt.setPlainText(self.default_opmerking)
        if self.paper_size_standard == "DIN":
            self.settings_dlg.paper_size_din_rbn.setChecked(True)
        else:
            self.settings_dlg.paper_size_ansi_rbn.setChecked(True)

        self.settings_dlg.show()
        
        result = self.settings_dlg.exec_()
        if result:
            # logo
            path = unicode(self.settings_dlg.logo_path_ldt.text())
            if path[0:4] == 'http':
                # urlEncode?
                pass
            else:
                # make more canonical?
                pass
            self.logoImagePath = path
            self.settings.setValue("QuickPrint/logo_path", self.logoImagePath)
            if not self.logoImagePath:
                self.dlg.logo_cbx.setChecked(False)
                self.dlg.logo_cbx.setEnabled(False)
            
            # north arrow
            path = unicode(self.settings_dlg.north_arrow_path_ldt.text())
            if path[0:4] == 'http':
                # urlEncode?
                pass
            else:
                # make more canonical?
                pass
            self.logoImagePath = path
            self.settings.setValue("QuickPrint/north_arrow_path", self.northArrowImagePath)    

            self.dateFormatString = unicode(self.settings_dlg.date_format_ldt.text())
            self.settings.setValue("QuickPrint/date_format_string", self.dateFormatString)
        
            self.textFont = self.settings_dlg.fontComboBox.currentFont().family()
            self.settings.setValue("QuickPrint/text_font", self.textFont)
            
            self.fontSize = self.settings_dlg.font_size_sld.value()
            self.settings.setValue("QuickPrint/font_size", self.fontSize)

            self.default_bronnen = self.settings_dlg.default_attribition_tbx.toPlainText()
            self.settings.setValue("QuickPrint/attribution", self.default_bronnen )
            self.default_opmerking =  self.settings_dlg.default_remark_ldt.toPlainText()
            self.settings.setValue("QuickPrint/remark", self.default_opmerking)

            if self.settings_dlg.paper_size_din_rbn.isChecked():
                self.paper_size_standard = "DIN"
                self.dlg.a4Btn.setText("A4")
                self.dlg.a3Btn.setText("A3")
            else:
                self.paper_size_standard = "ANSI"
                self.dlg.a4Btn.setText("ANSI-A")
                self.dlg.a3Btn.setText("ANSI-B")
            self.settings.setValue("QuickPrint/paper_size_standard", 
                self.paper_size_standard)
                
    def preview_toggled(self, state = None):
        """
        Resize dialog when preview is hidden
        """
        
        self.dlg.adjustSize()

    def update_preview(self, size = None):
        """
        Shows the preview
        """
        
        if self.dlg.isVisible() \
        and not self.dlg.freeze_cbx.isChecked() \
        and not self.dlg.preview_gbx.isCollapsed():
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            l = self.get_print_layout()
            exporter = QgsLayoutExporter(l)
            previewImage = exporter.renderPageToImage(page = 0)              
            img = QPixmap(previewImage).scaled(
                self.dlg.preview_lbl.width(), 
                self.dlg.preview_lbl.height(), 
                QtCore.Qt.KeepAspectRatio)
            self.dlg.preview_lbl.setPixmap(img)
            QGuiApplication.restoreOverrideCursor()
                    
    def get_print_layout(self):
        '''
        Creates print layout for either a preview or an export
        '''
        
        font_scale = float(self.fontSize) / 100

        dpi = 600
        # get the users input 
        titel = self.dlg.titelFld.text()
        subTitel = self.dlg.subTitelFld.text()

        bronnen = self.dlg.bronnenFld.toPlainText()
        opmerkingen = self.dlg.opmerkingenFld.toPlainText()

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
        if self.dlg.logo_cbx.isChecked():
            try:
                logo = QgsLayoutItemPicture(l)
                logo.setPicturePath(self.logoImagePath)
                logo.attemptSetSceneRect(QRectF((paperSize[0] - paperSize[0] / 3), 0, refSize / 3, refSize / 3 * 756 / 2040 )) 
                # logo.setFrameEnabled(True)
                l.addItem(logo)
            except:
                # failed to add the logo, show message and continue
                self.iface.messageBar().pushMessage(
                    "Warning", self.tr(u"Failed adding logo ") + \
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
        scaleBar.setStyle('Line Ticks Down') 
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
        
        # add north arrow
        if self.dlg.northarrow_cbx.isChecked():
            
            north = QgsLayoutItemPicture(l)
            north.setLinkedMap(theMap)
            north.setPicturePath(self.northArrowImagePath)
            l.addLayoutItem(north)
            
            north_arrow_size = 23
            north.attemptResize(QgsLayoutSize(north_arrow_size, north_arrow_size,QgsUnitTypes.LayoutMillimeters))
            
            # bottom right
            # north.setPos(paperSize[0] - lm - north_arrow_size, tm + (paperSize[1] - bm) - north_arrow_size )
            # top right
            north.setPos(paperSize[0] - lm - north_arrow_size, tm)
        
        return l
        
    def run(self):
        '''
        methods doing most of the work.
        shows the dialog, and acts on the result.
        '''

        if not self.logoImagePath:
            self.dlg.logo_cbx.setChecked(False)
            self.dlg.logo_cbx.setEnabled(False)
            
        self.dlg.show()
        self.preview_toggled()
        self.update_preview()
        
        result = self.dlg.exec_()
        if result:
            
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            
            l = self.get_print_layout()
            exporter = QgsLayoutExporter(l)
            
            export_name = self.dlg.file_name_qfw.filePath()
            
            if export_name[-4:].lower() == '.pdf':
                # export pdf
                pdf_settings = exporter.PdfExportSettings() #dpi?
                exporter.exportToPdf(export_name, pdf_settings)
                
            if export_name[-4:].lower() == '.png':
                img_settings = exporter.ImageExportSettings()
                exporter.exportToImage(export_name, img_settings)

            # inform the user about the result
            if os.path.exists(export_name):
                self.iface.messageBar().pushMessage("Info", self.tr(u"Saved: ") + \
                                                    export_name,
                                                    Qgis.Info)
                # and if user wants so open the file
                if self.dlg.openAfterSaveBox.isChecked():
                    if hasattr(os, 'startfile'):
                        # windows only
                        os.startfile(export_name)
                    else:
                        subprocess.call(["xdg-open", export_name])
            else:
                self.iface.messageBar().pushMessage(
                    "Warning", self.tr(u"Failed saving file ") + \
                    export_name, 
                    Qgis.Warning)

            QGuiApplication.restoreOverrideCursor()
