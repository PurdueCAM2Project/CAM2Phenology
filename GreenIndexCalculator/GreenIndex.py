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
    fileList = [os.path.join("D:\\Phenology_Images\\2009\\Jun", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Jun")] \
            + [os.path.join("D:\\Phenology_Images\\2009\\Nov", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Nov")]
    for filename in fileList:
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            exifData = piexif.load(filename)
            date = datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d %H:%M:%S")
            if not (date.hour < 7 or date.hour > 19): #Time mux for nps dataset
                print(filename)
                analysisArray = None
                if not len(xRegionData): #No regions specified, so process entire image
                    analysisArray = misc.imread(filename)
                    greenIndex = CalculateGreenIndex(analysisArray)
                    if greenIndex != -1:
                        plotData[0].append([date, greenIndex])
                else:
                    for counter in range(0, len(xRegionData)):
                        analysisArray = misc.imread(filename)
                        analysisArray = analysisArray[int(xRegionData[counter][0]) : int(xRegionData[counter][1]) + 1, int(yRegionData[counter][0]) : int(yRegionData[counter][1]) + 1, :]
                        #Image.fromarray(analysisArray, 'RGB').show()
                        greenIndex = CalculateGreenIndex(analysisArray)
                        if greenIndex != -1:
                            if counter in plotData.keys():
                                plotData[counter].append([date, greenIndex])
                            else: #First time a region is being processed
                                plotData[counter] = [[date, greenIndex]]
    #print(plotData)
    if not len(xRegionData): #For labeling when no regions are selected
        xRegionData = [[0, analysisArray.shape[0]]]
        yRegionData = [[0, analysisArray.shape[1]]]
    for pointSet, pointDataSet in plotData.iteritems():
        PlotGreenIndex([item[0] for item in pointDataSet], [item[1] for item in pointDataSet], xRegionData[pointSet], yRegionData[pointSet])

def CalculateGreenIndex(imageArray):
    RGB = float(sum(imageArray))
    if RGB == 0:
        return -1
    return float(sum(imageArray[:,:,1])) / RGB #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList, xPoints, yPoints):
    pyplot.scatter(timeList, greenList)
    pyplot.title(str(xPoints) + " " + str(yPoints))
    pyplot.ylabel("Greenness Index")
    pyplot.xlabel("Date of Picture")
    pyplot.show()


ParseImages()