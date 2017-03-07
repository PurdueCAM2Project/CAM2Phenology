# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'exifUI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(570, 342)
        self.runButton = QtGui.QPushButton(Dialog)
        self.runButton.setGeometry(QtCore.QRect(450, 300, 93, 28))
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.browseButton = QtGui.QPushButton(Dialog)
        self.browseButton.setEnabled(True)
        self.browseButton.setGeometry(QtCore.QRect(30, 240, 93, 28))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.browseText = QtGui.QLineEdit(Dialog)
        self.browseText.setGeometry(QtCore.QRect(150, 240, 400, 28))
        self.browseText.setObjectName(_fromUtf8("browseText"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 30, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 90, 121, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(30, 150, 121, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.searchText = QtGui.QLineEdit(Dialog)
        self.searchText.setGeometry(QtCore.QRect(150, 25, 371, 28))
        self.searchText.setObjectName(_fromUtf8("searchText"))
        self.searchText_2 = QtGui.QLineEdit(Dialog)
        self.searchText_2.setGeometry(QtCore.QRect(150, 85, 131, 28))
        self.searchText_2.setObjectName(_fromUtf8("searchText_2"))
        self.locationText = QtGui.QLineEdit(Dialog)
        self.locationText.setGeometry(QtCore.QRect(150, 145, 371, 28))
        self.locationText.setObjectName(_fromUtf8("locationText"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.runButton.setText(_translate("Dialog", "Run", None))
        self.browseButton.setText(_translate("Dialog", "Browse", None))
        self.label.setText(_translate("Dialog", "Search Text:", None))
        self.label_2.setText(_translate("Dialog", "Number of Images:", None))
        self.label_3.setText(_translate("Dialog", "Geolocation:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

