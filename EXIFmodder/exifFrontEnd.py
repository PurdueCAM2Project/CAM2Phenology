from exifUI import *
import sys
from PyQt4 import QtCore, QtGui
import search

class Consumer(QtGui.QMainWindow, Ui_Dialog):
    def __init__(self, parent = None):
        super(Consumer, self).__init__(parent)
        self.setupUi(self)
        self.browseButton.clicked.connect(self.fileBrowse)
        self.runButton.clicked.connect(self.runSearch)
        self.locationText.setDisabled(1)
        self.searchText_2.setInputMask("D9999") #number ranges from 1 - 99999
        self.setWindowTitle("Flickr Downloader")
    def fileBrowse(self):
        filepath = QtGui.QFileDialog.getExistingDirectory(self, 'Select Folder to Download Images:')
        if filepath is not "":
            self.browseText.setText(filepath)

    def runSearch(self):
        if len(self.searchText.text().replace(" ", "")) is 0:
            self.searchText.setText("Search text cannot be empty!")
            return
        elif "Search text cannot be empty!" in self.searchText.text():
            return
        if self.searchText_2.text() is "" or int(self.searchText_2.text()) is 0:
            self.searchText_2.setText("1")
        if self.browseText.text() is "":
            self.browseText.setText("File location cannot be empty")
            return
        elif "File location cannot be empty" in self.browseText.text():
            return
        searchString = self.searchText.text().replace(" ", "%20")
        searchString = searchString.replace(',', '%C')
        searchString = "&text=" + searchString + "&per_page=500"
        print(searchString)
        search.search(searchString, int(self.searchText_2.text()), self.browseText.text() + '\\')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainWindow = Consumer()
    mainWindow.show()
    sys.exit(app.exec_())