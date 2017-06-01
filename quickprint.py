# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickPrint
                                 A QGIS plugin
 Create a quick print with a minimum of fuzz
                              -------------------
        begin                : 2014-05-28
        copyright            : (C) 2017 by Marco Duiker (MD-kwadraat)
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis import utils
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from quickprintdialog import QuickPrintDialog
# Import the rest of the needed modules
import os.path 
import time
import sys
import subprocess


class QuickPrint:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'quickprint2_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QuickPrintDialog()
        
        # add some necessary signal and slot communication as well as disable the save button for now  
        self.dlg.cancel_save_button_box.button(QDialogButtonBox.Save).setEnabled(False)
        QObject.connect(self.dlg.fileBrowseButton, SIGNAL("clicked()"), self.chooseFile)
        QObject.connect(self.dlg.pdfFileNameBox, SIGNAL("textChanged(QString)"), self.pdfFileNameBoxChanged)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/quickprint/icon.png"),
            u"QuickPrint", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&QuickPrint", self.action)

        # help
        self.helpAction = QAction(QIcon(":/plugins/quickprint/help.png"), 
                             "Help", self.iface.mainWindow())
        self.helpAction.triggered.connect(self.help)
        self.helpAction.setWhatsThis("Help")
        self.iface.addPluginToMenu(u"&QuickPrint", self.helpAction)
        # QObject.connect(self.helpAction, SIGNAL("activated()"), self.help)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&QuickPrint", self.action)
        self.iface.removeToolBarIcon(self.action)

    def getPaperSize(self):
        # Get the paper size

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
        fileName = QFileDialog.getSaveFileName(caption = "save pdf", directory = '', filter = '*.pdf')
        self.dlg.pdfFileNameBox.setText(fileName)
        
    def pdfFileNameBoxChanged(self, fileName):
        if os.path.exists(os.path.dirname(fileName)):
            self.dlg.cancel_save_button_box.button(QDialogButtonBox.Save).setEnabled(True)

    def help(self):
        #  utils.showPluginHelp()      # this is not working properly
        QDesktopServices().openUrl(QUrl(os.path.join("file://",self.plugin_dir, 'help/build/html','index.html'),QUrl.TolerantMode))

    def run(self):
        self.dlg.show()
        result = self.dlg.exec_()
        
        if result:
            dpi = 600

            # get the users input 
            titel = self.dlg.titelFld.text()
            subTitel = self.dlg.subTitelFld.text()
    
            bronnen = self.dlg.bronnenFld.toPlainText()
            opmerkingen = self.dlg.opmerkingenFld.toPlainText ()

            # define maprenderer
            mapRenderer = self.iface.mapCanvas().mapRenderer()
            c = QgsComposition(mapRenderer)
            c.setPlotStyle(QgsComposition.Print)

            paperSize = self.getPaperSize()
            c.setPaperSize(paperSize[0],paperSize[1])
            c.setPrintResolution(dpi)

            # add gadgets
            # but first get margins and paper size right
            lm = 10         # left margin
            tm = 30         # upper margin
            bm = 65         # lower margin
            
            refSize = c.paperWidth()
            if c.paperHeight() < refSize:
                refSize = c.paperHeight()

            # add map
            x, y = lm, tm
            w, h = c.paperWidth() -  2 * lm, c.paperHeight() - bm
            composerMap = QgsComposerMap(c, x, y, w, h)
            composerMap.setFrameEnabled(True)
            c.addItem(composerMap)
            
            # add title
            titleFont = QFont("Arial", 14)
            titleFont.setBold(True)

            titelLabel = QgsComposerLabel(c)
            titelLabel.setText(titel)
            titelLabel.setItemPosition(lm,10)
            titelLabel.setFont(titleFont)    
            titelLabel.adjustSizeToText()
            c.addItem(titelLabel)

            # add subtitle
            subTitleFont = QFont("Arial", 12)
            subTitleFont.setBold(False)
                
            subTitelLabel = QgsComposerLabel(c)
            subTitelLabel.setText(subTitel)
            subTitelLabel.setItemPosition(lm, 20)
            subTitelLabel.setFont(subTitleFont)	    
            subTitelLabel.adjustSizeToText()
            c.addItem(subTitelLabel)  

            textFont = QFont("Arial", 10)  

            # add logo
            logoImagePath = os.path.join(self.plugin_dir, 'img', 'logo.png')
            if os.path.exists(logoImagePath) and os.path.isfile(logoImagePath):
                try:
                    logo = QgsComposerPicture(c)
                    logo.setPictureFile(logoImagePath)
                    logo.setSceneRect(QRectF((c.paperWidth() - c.paperWidth() / 3), 0, refSize / 3, refSize / 3 * 756 / 2040 )) 
                    logo.setItemPosition(c.paperWidth() - refSize / 3, 0)
                    # logo.setFrameEnabled(True)
                    c.addItem(logo)
                except:
                    # failed to add the logo, just continue
                    pass

            #add date
            dateLabel = QgsComposerLabel(c)
            d = time.localtime()
            dString = "%d-%d-%d" % (d[2],  d[1],  d[0])
            dateLabel.setText(dString)
            dateLabel.setFont(textFont)
            dateLabel.adjustSizeToText()
            dateStringWidth = dateLabel.textWidthMillimeters(textFont,dString)
            dateLabel.setItemPosition(c.paperWidth() - lm - dateStringWidth -5, (c.paperHeight() - bm) + tm + 5)
            c.addItem(dateLabel)
                
            # add scalebar
            scaleBar = QgsComposerScaleBar(c)
            scaleBar.setComposerMap(composerMap)
            scaleBar.setItemPosition(lm + 10, tm + (c.paperHeight() - bm) - 20 )
            scaleBar.applyDefaultSettings()
            scaleBar.applyDefaultSize()
            # scaleBar.setStyle('Line Ticks Down') 
            scaleBar.setNumSegmentsLeft(0)
            scaleBar.setNumSegments(3)
            scaleBar.adjustBoxSize()
            c.addItem(scaleBar)

            # add attribution
            bronnenLabel = QgsComposerLabel(c)
            bronnenLabel.setText(bronnen)
            bronnenLabel.setSceneRect(QRectF(lm, (c.paperHeight() - bm) + tm + 5, c.paperWidth() - lm - dateStringWidth -5 -lm -lm, c.paperHeight() - ((c.paperHeight() - bm) + tm + 5) - 10 ))    
            bronnenLabel.setFont(textFont)
            # bronnenLabel.setFrameEnabled(True)
            # bronnenLabel.adjustSizeToText()   This one is wrong when using linebreaks in string
            c.addItem(bronnenLabel)

            # add remarks
            opmLabel = QgsComposerLabel(c)
            opmLabel.setText(opmerkingen)
            opmLabel.setSceneRect(QRectF(lm, c.paperHeight() - 10, c.paperWidth() - lm -lm , 400 )) 
            opmLabel.setFont(textFont)
            # opmLabel.setFrameEnabled(True)
            # opmLabel.adjustSizeToText()    This one is wrong when using linebreaks in string
            c.addItem(opmLabel)

            # initialize renderer and do some pre-render settings
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(self.dlg.pdfFileNameBox.displayText());
            
            printer.setPaperSize(QSizeF(c.paperWidth(), c.paperHeight()), QPrinter.Millimeter)
            printer.setFullPage(True)
            printer.setColorMode(QPrinter.Color)
            printer.setResolution(c.printResolution())
            paperRectMM = printer.pageRect(QPrinter.Millimeter)
            paperRectPixel = printer.pageRect(QPrinter.DevicePixel)

            # now render
            pdfPainter = QPainter(printer)
            c.render(pdfPainter, paperRectPixel, paperRectMM)
            pdfPainter.end()
            
            # inform the user about the result
            self.iface.messageBar().pushMessage("Info", "Saved as pdf: %s" % self.dlg.pdfFileNameBox.displayText() ,self.iface.messageBar().INFO)
            # and if user wants so open the file
            if self.dlg.openAfterSaveBox.isChecked():
                if sys.platform.startswith('linux'):
                    subprocess.call(["xdg-open", self.dlg.pdfFileNameBox.displayText()])
                else:
                    # windows only
                    os.startfile(self.dlg.pdfFileNameBox.displayText())

