from scipy import misc
from matplotlib import pyplot
import os
from numpy import sum
import piexif
from datetime import datetime

def ParseImages():
    plotData = []
    for filename in os.listdir("."):
        if filename.endswith(".jpg"):
            exifData = piexif.load(filename)
            plotData.append([datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d"),
                             CalculateGreenIndex(misc.imread(filename))])
    PlotGreenIndex([item[0] for item in plotData], [item[1] for item in plotData])

def CalculateGreenIndex(imageArray):
    return float(sum(imageArray[:,:,1])) / float(sum(imageArray)) #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList):
    pyplot.scatter(timeList, greenList)
    pyplot.show()


ParseImages()