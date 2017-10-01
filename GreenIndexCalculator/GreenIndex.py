from scipy import misc
from matplotlib import pylab
import os
from numpy import sum, polyfit, poly1d
import piexif
from datetime import datetime
import time
import sys
import mpldatacursor
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

    fileList = []
    pathList = []

    for (filename) in os.walk("D:\\Phenology_Images\\"):
        if len(filename[2]) != 0:
            pathList += [filename]

    for dirList in pathList:
        for filename in dirList[2]:
            if "1200.jpg" in filename:
                fileList += [dirList[0] + "\\" + filename]
    #fileList = [os.path.join("D:\\Phenology_Images\\2009\\Jun", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Jun")] \
    #        + [os.path.join("D:\\Phenology_Images\\2009\\Nov", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Nov")]

    #for fileTup in os.walk("C:\Users\Achinthya\Desktop\Projects\\vipphenology\GreenIndexCalculator\Summer_vs_Fall"):
    #    for filename in fileTup[2]:
    #        fileList += ["Summer_vs_Fall\\" + filename]

    for filename in fileList:
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            exifData = piexif.load(filename)
            date = datetime.strptime(exifData.get("Exif").get(36867), "%Y:%m:%d %H:%M:%S")
            if not (date.hour < 9 or date.hour > 17): #Time mux for nps dataset
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
                        analysisArray = analysisArray[int(xRegionData[counter][0]) : int(xRegionData[counter][1]) + 1,
                                                      int(yRegionData[counter][0]) : int(yRegionData[counter][1]) + 1, :]
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
        PlotGreenIndex([item[0] for item in pointDataSet],
                       [item[1] for item in pointDataSet],
                       xRegionData[pointSet],
                       yRegionData[pointSet])

def CalculateGreenIndex(imageArray):
    RGB = float(sum(imageArray))
    if RGB == 0:
        return -1
    return float(sum(imageArray[:,:,1])) / RGB #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList, xPoints, yPoints):
    pylab.figure()
    pylab.scatter(timeList, greenList)
    pylab.title(str(xPoints) + " " + str(yPoints))
    pylab.ylabel("Greenness Index")
    pylab.xlabel("Date of Picture")
    timeLabels = []
    for timeStamp in timeList:
        timeLabels += [int(time.mktime(timeStamp.timetuple()))]
    z = polyfit(timeLabels, greenList, 10)
    p = poly1d(z)
    pylab.plot(timeList, p(timeLabels), "r--")
    mpldatacursor.datacursor()
    pylab.show()

ParseImages()