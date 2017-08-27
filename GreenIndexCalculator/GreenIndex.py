from scipy import misc
from matplotlib import pyplot
import os
from numpy import sum
import piexif
from datetime import datetime
import sys
from PIL import Image


def ParseImages():
    plotData = []
    xRegionData = []
    yRegionData = []
    if len(sys.argv) == 5: #TODO expand to multiple region support
        xRegionData.append(sys.argv[1 : 3])
        yRegionData.append(sys.argv[3 :])
    for filename in os.listdir("."):
        if filename.endswith(".jpg"):
            exifData = piexif.load(filename)
            analysisArray = None
            if not len(xRegionData): #No regions specified, so process entire image
                analysisArray = misc.imread(filename)
            else: #TODO expand to multiple region support
                analysisArray = misc.imread(filename)
                analysisArray = analysisArray[int(xRegionData[0][0]) : int(xRegionData[0][1]) + 1, int(yRegionData[0][0]) : int(yRegionData[0][1]) + 1, :]
                Image.fromarray(analysisArray, 'RGB').show()
            plotData.append([datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d"),
                             CalculateGreenIndex(analysisArray)])
    PlotGreenIndex([item[0] for item in plotData], [item[1] for item in plotData])

def CalculateGreenIndex(imageArray):
    return float(sum(imageArray[:,:,1])) / float(sum(imageArray)) #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList):
    pyplot.scatter(timeList, greenList)
    pyplot.show()


ParseImages()