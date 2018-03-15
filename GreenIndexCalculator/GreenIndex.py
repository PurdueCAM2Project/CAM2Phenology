from scipy import misc
from matplotlib import pyplot
import os
from numpy import sum
import piexif
from datetime import datetime
import sys
from PIL import Image


def ParseImages():
    plotData = {}
    xRegionData = []
    yRegionData = []
    numGraphs = 1
    if not (len(sys.argv) - 1) % 4 and len(sys.argv) != 1: #Check that user has specified 4 points to box each region
        sys.argv = sys.argv[1:] #remove script name from args
        for counter in range(0, (len(sys.argv)) / 4):
            xRegionData.append(sys.argv[counter * 4 : counter * 4 + 2])
            yRegionData.append(sys.argv[counter * 4  + 2: counter * 4 + 4])
        print(xRegionData)
        print(yRegionData)
        numGraphs = len(xRegionData)
    else:
        plotData[0] = [] #precreate point list
    for filename in os.listdir("."):
        if filename.endswith(".jpg"):
            exifData = piexif.load(filename)
            analysisArray = None
            if not len(xRegionData): #No regions specified, so process entire image
                analysisArray = misc.imread(filename)
                plotData[0].append([datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d"),
                                 CalculateGreenIndex(analysisArray)])
            else:
                for counter in range(0, len(xRegionData)):
                    analysisArray = misc.imread(filename)
                    analysisArray = analysisArray[int(xRegionData[counter][0]) : int(xRegionData[counter][1]) + 1, int(yRegionData[counter][0]) : int(yRegionData[counter][1]) + 1, :]
                    #Image.fromarray(analysisArray, 'RGB').show()
                    if counter in plotData.keys():
                        plotData[counter].append([datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d"),
                         CalculateGreenIndex(analysisArray)])
                    else: #First time a region is being processed
                        plotData[counter] = [[datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d"),
                             CalculateGreenIndex(analysisArray)]]
    print(plotData)
    if not len(xRegionData): #For labeling when no regions are selected
        xRegionData = [[0, analysisArray.shape[0]]]
        yRegionData = [[0, analysisArray.shape[1]]]
    for pointSet, pointDataSet in plotData.iteritems():
        PlotGreenIndex([item[0] for item in pointDataSet], [item[1] for item in pointDataSet], xRegionData[pointSet], yRegionData[pointSet])

def CalculateGreenIndex(imageArray):
    return float(sum(imageArray[:,:,1])) / float(sum(imageArray)) #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList, xPoints, yPoints):
    pyplot.scatter(timeList, greenList)
    pyplot.title(str(xPoints) + " " + str(yPoints))
    pyplot.ylabel("Greenness Index")
    pyplot.xlabel("Date of Picture")
    pyplot.show()


ParseImages()