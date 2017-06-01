# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_quickprint.ui'
#
# Created: Wed May 17 11:14:41 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!


from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QuickPrint(object):
    def setupUi(self, QuickPrint):
        QuickPrint.setObjectName(_fromUtf8("QuickPrint"))
        QuickPrint.resize(400, 465)
        self.cancel_save_button_box = QtGui.QDialogButtonBox(QuickPrint)
        self.cancel_save_button_box.setGeometry(QtCore.QRect(160, 420, 211, 32))
        self.cancel_save_button_box.setOrientation(QtCore.Qt.Horizontal)
        self.cancel_save_button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.cancel_save_button_box.setObjectName(_fromUtf8("cancel_save_button_box"))
        self.titelFld = QtGui.QLineEdit(QuickPrint)
        self.titelFld.setGeometry(QtCore.QRect(30, 40, 341, 27))
        self.titelFld.setObjectName(_fromUtf8("titelFld"))
        self.subTitelFld = QtGui.QLineEdit(QuickPrint)
        self.subTitelFld.setGeometry(QtCore.QRect(30, 80, 341, 27))
        self.subTitelFld.setObjectName(_fromUtf8("subTitelFld"))
        self.groupBox = QtGui.QGroupBox(QuickPrint)
        self.groupBox.setGeometry(QtCore.QRect(30, 110, 111, 81))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.a4Btn = QtGui.QRadioButton(self.groupBox)
        self.a4Btn.setGeometry(QtCore.QRect(10, 30, 104, 22))
        self.a4Btn.setChecked(True)
        self.a4Btn.setObjectName(_fromUtf8("a4Btn"))
        self.a3Btn = QtGui.QRadioButton(self.groupBox)
        self.a3Btn.setGeometry(QtCore.QRect(10, 50, 104, 22))
        self.a3Btn.setObjectName(_fromUtf8("a3Btn"))
        self.formaatLbl = QtGui.QLabel(self.groupBox)
        self.formaatLbl.setGeometry(QtCore.QRect(10, 10, 58, 17))
        self.formaatLbl.setObjectName(_fromUtf8("formaatLbl"))
        self.bronnenFld = QtGui.QPlainTextEdit(QuickPrint)
        self.bronnenFld.setGeometry(QtCore.QRect(30, 200, 341, 61))
        self.bronnenFld.setObjectName(_fromUtf8("bronnenFld"))
        self.opmerkingenLbl = QtGui.QLabel(QuickPrint)
        self.opmerkingenLbl.setGeometry(QtCore.QRect(30, 280, 171, 17))
        self.opmerkingenLbl.setObjectName(_fromUtf8("opmerkingenLbl"))
        self.groupBox_2 = QtGui.QGroupBox(QuickPrint)
        self.groupBox_2.setGeometry(QtCore.QRect(259, 110, 111, 81))
        self.groupBox_2.setTitle(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.orientatieLbl = QtGui.QLabel(self.groupBox_2)
        self.orientatieLbl.setGeometry(QtCore.QRect(10, 10, 61, 16))
        self.orientatieLbl.setObjectName(_fromUtf8("orientatieLbl"))
        self.portretBtn = QtGui.QRadioButton(self.groupBox_2)
        self.portretBtn.setGeometry(QtCore.QRect(10, 30, 104, 22))
        self.portretBtn.setChecked(True)
        self.portretBtn.setObjectName(_fromUtf8("portretBtn"))
        self.landschapBtn = QtGui.QRadioButton(self.groupBox_2)
        self.landschapBtn.setGeometry(QtCore.QRect(10, 50, 104, 22))
        self.landschapBtn.setObjectName(_fromUtf8("landschapBtn"))
        self.opmerkingenFld = QtGui.QPlainTextEdit(QuickPrint)
        self.opmerkingenFld.setGeometry(QtCore.QRect(30, 300, 341, 71))
        self.opmerkingenFld.setObjectName(_fromUtf8("opmerkingenFld"))
        self.VensterLbl = QtGui.QLabel(QuickPrint)
        self.VensterLbl.setGeometry(QtCore.QRect(30, 20, 301, 17))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.VensterLbl.setFont(font)
        self.VensterLbl.setObjectName(_fromUtf8("VensterLbl"))
        self.openAfterSaveBox = QtGui.QCheckBox(QuickPrint)
        self.openAfterSaveBox.setGeometry(QtCore.QRect(30, 425, 141, 21))
        self.openAfterSaveBox.setChecked(True)
        self.openAfterSaveBox.setObjectName(_fromUtf8("openAfterSaveBox"))
        self.layoutWidget = QtGui.QWidget(QuickPrint)
        self.layoutWidget.setGeometry(QtCore.QRect(30, 380, 341, 29))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.pdfFileNameBox = QtGui.QLineEdit(self.layoutWidget)
        self.pdfFileNameBox.setObjectName(_fromUtf8("pdfFileNameBox"))
        self.horizontalLayout.addWidget(self.pdfFileNameBox)
        self.fileBrowseButton = QtGui.QPushButton(self.layoutWidget)
        self.fileBrowseButton.setObjectName(_fromUtf8("fileBrowseButton"))
        self.horizontalLayout.addWidget(self.fileBrowseButton)

        self.retranslateUi(QuickPrint)
        QtCore.QObject.connect(self.cancel_save_button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), QuickPrint.accept)
        QtCore.QObject.connect(self.cancel_save_button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), QuickPrint.reject)
        QtCore.QMetaObject.connectSlotsByName(QuickPrint)

    def retranslateUi(self, QuickPrint):
        QuickPrint.setWindowTitle(_translate("QuickPrint", "QuickPrint", None))
        self.titelFld.setText(_translate("QuickPrint", "Title", None))
        self.subTitelFld.setText(_translate("QuickPrint", "Subtitle", None))
        self.a4Btn.setText(_translate("QuickPrint", "A4", None))
        self.a3Btn.setText(_translate("QuickPrint", "A3", None))
        self.formaatLbl.setText(_translate("QuickPrint", "Paper size", None))
        self.bronnenFld.setPlainText(_translate("QuickPrint", "Attribution:", None))
        self.opmerkingenLbl.setText(_translate("QuickPrint", "Remarks:", None))
        self.orientatieLbl.setText(_translate("QuickPrint", "Orientation", None))
        self.portretBtn.setText(_translate("QuickPrint", "Portrait", None))
        self.landschapBtn.setText(_translate("QuickPrint", "Landscape", None))
        self.VensterLbl.setText(_translate("QuickPrint", "Create quick print as pdf:", None))
        self.openAfterSaveBox.setStatusTip(_translate("QuickPrint", "Show pdf file after saving", None))
        self.openAfterSaveBox.setWhatsThis(_translate("QuickPrint", "Show pdf file after saving", None))
        self.openAfterSaveBox.setText(_translate("QuickPrint", "Show after saving", None))
        self.label.setText(_translate("QuickPrint", "Save as:", None))
        self.fileBrowseButton.setText(_translate("QuickPrint", "Browse", None))
