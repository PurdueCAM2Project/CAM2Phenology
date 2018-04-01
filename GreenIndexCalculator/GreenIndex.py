from scipy import misc
from matplotlib import pylab, pyplot
import os
from numpy import sum, polyfit, poly1d
import piexif
from datetime import datetime
import time
import sys
import mpldatacursor
from PIL import Image
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def ParseImages():
    plotData = {}
    xRegionData = []
    yRegionData = []
    tempData = []
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
    #for (filename) in os.walk("D:\\Phenology_Images\\"):
    #    if len(filename[2]) != 0:
    #        pathList += [filename]

    #for dirList in pathList:
    #    if "2010" in dirList[0]: # or "2005" in dirList[0] or "2006" in dirList[0] or "2007" in dirList[0] or "2008" in dirList[0]:
            #if ("Apr" in dirList[0] or "May" in dirList[0]):
            #if "Dec" in dirList[0] or "Nov" in dirList[0] or "Oct" in dirList[0]:
    #        for filename in dirList[2]:
    #            if "1200.jpg" in filename:
    #                fileList += [dirList[0] + "\\" + filename]
                    #fileList += [dirList[0] + "\\" + filename]
    #fileList = [os.path.join("D:\\Phenology_Images\\2009\\Jun", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Jun")] \
    #        + [os.path.join("D:\\Phenology_Images\\2009\\Nov", filename) for filename in os.listdir("D:\\Phenology_Images\\2009\\Nov")]

    #for fileTup in os.walk("C:\Users\Achinthya\Desktop\Projects\\vipphenology\GreenIndexCalculator\Summer_vs_Fall"):
    #    for filename in fileTup[2]:
    #        fileList += ["Summer_vs_Fall\\" + filename]
    for fileTup in os.walk("D:\Phenology_Images\Campbell\carlos_cambell_rad=1.json\\"):
        for filename in fileTup[2]:
            fileList.append("D:\Phenology_Images\Campbell\carlos_cambell_rad=1.json\\" + filename)

    for filename in fileList:
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            try:
                exifData = piexif.load(filename)
                print(exifData)
                print(exifData.get("Exif"))
                print(exifData.get("Exif").get(36867))
                date = datetime.strptime((exifData.get("Exif").get(36867)).decode("utf-8"), "%Y:%m:%d %H:%M:%S")
            except:
                continue
            #if "C730UZ" in str(exifData.get("0th").get(272)): #C730UZ #E-420
            #if "E-420" in str(exifData.get("0th").get(272)): #C730UZ #E-420
        if date is not None and not (date.hour < 9 or date.hour > 17): #Time mux for nps dataset
            if date.month:# in range(4,6):
                print (filename)
                analysisArray = None
                if not len(xRegionData): #No regions specified, so process entire image
                    analysisArray = misc.imread(filename)
                    greenIndex, redIndex = CalculateGreenIndex(analysisArray)
                    if greenIndex != -1:
                        plotData[0].append([date, greenIndex, redIndex])
                else:
                    for counter in range(0, len(xRegionData)):
                        analysisArray = misc.imread(filename)
                        analysisArray = analysisArray[int(xRegionData[counter][0]) : int(xRegionData[counter][1]) + 1,
                                                      int(yRegionData[counter][0]) : int(yRegionData[counter][1]) + 1, :]
                        #Image.fromarray(analysisArray, 'RGB').show()
                        greenIndex, redIndex = CalculateGreenIndex(analysisArray)
                        if greenIndex != -1:
                            if counter in plotData.keys():
                                plotData[counter].append([date, greenIndex, redIndex])
                            else: #First time a region is being processed
                                plotData[counter] = [[date, greenIndex, redIndex]]
                #tempData.append(GetTemperature(date))
    #print(plotData)
    if not len(xRegionData): #For labeling when no regions are selected
        xRegionData = [[0, analysisArray.shape[0]]]
        yRegionData = [[0, analysisArray.shape[1]]]
    for pointSet, pointDataSet in plotData.items():
        PlotGreenIndex([item[0] for item in pointDataSet],
                       [item[1] for item in pointDataSet],
                       [item[2] for item in pointDataSetSet],
                       xRegionData[pointSet],
                       yRegionData[pointSet], tempData)

def GetTemperature(date):
    url = ('https://www.wunderground.com/history/airport/KTYS/' + str(date.year) + '/'
           + str(date.month) + '/' + str(date.day) + '/DailyHistory.html')
    #print(url)
    pattern = "[0-9]*\.[0-9]*"
    soup = BeautifulSoup(urlopen(url).read(), "lxml")
    weatherNext = False
    for element in soup.find_all('td'):
        if weatherNext:
            tempSearch = re.search(pattern, str(element))
            return float(tempSearch.group(0)) / 200 #/200 to scale data down so it can be seen on same scale as Greenness Index
        if "11:" in str(element) and "AM" in str(element) and "EST" not in str(element) and "EDT" not in str(element):
            weatherNext = True

def CalculateGreenIndex(imageArray):
    RGB = float(sum(imageArray))
    if RGB == 0:
        return -1
    return (float(sum(imageArray[:,:,1])) / RGB, float(sum(imageArray[:, :, 0])) / RGB) #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList, redList, xPoints, yPoints, tempData):

    pylab.figure()
    pylab.scatter(timeList, greenList)
    pylab.scatter(timeList, redList)
    pylab.title(str(xPoints) + " " + str(yPoints))
    pylab.ylabel("Greenness Index")
    pylab.xlabel("Date of Picture")
    timeLabels = []
    for timeStamp in timeList:
        timeLabels += [int(time.mktime(timeStamp.timetuple()))]

    maxGreen, maxRed = 0, 0
    minGreen, minRed = 1000, 1000
    minDateG, maxDateG, minDateR, maxDateR = 0, 0, 0, 0
    for i, greenIndex, redIndex in enumerate(greenList):
        if greenIndex < minGreen:
            minGreen = greenIndex
            minDateG = timeList[i]
        elif greenIndex > maxGreen:
            maxGreen = greenIndex
            maxDateG = timeList[i]
        if redIndex < minRed:
            minRed = redIndex
            minDateR = timeList[i]
        elif redIndex > maxRed:
            maxRed = redIndex
            maxDateR = timeList[i]
    print (minDateG)
    print (maxDateG)
    print (minDateR)
    print (maxDateR)
    print(tempData)
    #z = polyfit(timeLabels, greenList, 1)
    #t = polyfit(timeLabels, tempData, 2)
    #p = poly1d(z)
    #p_t = poly1d(t)
    #pylab.plot(timeList, p(timeLabels), "r--")
    #pylab.plot(timeList, p_t(tempData), "m--")
    #pylab.scatter(timeList, tempData, c = "g")
    mpldatacursor.datacursor()
    print (p)
    pylab.show()

ParseImages()