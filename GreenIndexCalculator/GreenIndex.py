from scipy import misc
from matplotlib import pylab, pyplot
import os
from numpy import sum, polyfit, poly1d
import piexif
from datetime import datetime
import time
import sys
import mpldatacursor
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def ParseImages():
    plotData = {}
    xRegionData = []
    yRegionData = []
    tempData = []
    if not (len(sys.argv) - 1) % 4 and len(sys.argv) != 1: #Check that user has specified 4 points to box each region
        sys.argv = sys.argv[1:] #remove script name from args
        for counter in range(0, (len(sys.argv)) // 4):
            xRegionData.append(sys.argv[counter * 4 : counter * 4 + 2])
            yRegionData.append(sys.argv[counter * 4  + 2: counter * 4 + 4])
        print(xRegionData)
        print(yRegionData)
    else:
        plotData[0] = [] #precreate point list

    fileList = []
    for fileTup in os.walk("C:\\Users\\Achinthya\\Downloads\\Carlos_Campbell_Overlook_0.1kmRadius"):
        for filename in fileTup[2]:
            fileList.append("C:\\Users\\Achinthya\\Downloads\\Carlos_Campbell_Overlook_0.1kmRadius\\" + filename)
    for filename in fileList:
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            try:
                exifData = piexif.load(filename)
                date = datetime.strptime((exifData.get("Exif").get(36867)).decode("utf-8"), "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(e)
                continue
            #Camera model filter
            #if "C730UZ" in str(exifData.get("0th").get(272)): #C730UZ #E-420
            #if "E-420" in str(exifData.get("0th").get(272)): #C730UZ #E-420
        #Date and time filter
        #if date is not None and not (date.hour < 9 or date.hour > 17): #Time mux for nps dataset
        #    if date.month:# in range(4,6):
            print (filename)
            analysisArray = None
            try:
                if not len(xRegionData): #No regions specified, so process entire image
                    analysisArray = misc.imread(filename)
                    greenIndex, redIndex, ratio = CalculateGreenIndex(analysisArray)
                    if greenIndex != -1:
                        plotData[0].append([date, greenIndex, redIndex, ratio])
                else:
                    for counter in range(0, len(xRegionData)):
                        analysisArray = misc.imread(filename)
                        analysisArray = analysisArray[int(xRegionData[counter][0]) : int(xRegionData[counter][1]) + 1,
                                                      int(yRegionData[counter][0]) : int(yRegionData[counter][1]) + 1, :]
                        #Image.fromarray(analysisArray, 'RGB').show() #display image (for use with image slicing/bounding boxes)
                        greenIndex, redIndex, ratio = CalculateGreenIndex(analysisArray)
                        if greenIndex != -1:
                            if counter in plotData.keys():
                                plotData[counter].append([date, greenIndex, redIndex, ratio])
                            else: #First time a region is being processed
                                plotData[counter] = [[date, greenIndex, redIndex, ratio]]
                tempData.append(GetTemperature(date))
            except Exception as e:
                print(e)
                pass
    if not len(xRegionData): #For labeling when no regions are selected
        xRegionData = [[0, analysisArray.shape[0]]]
        yRegionData = [[0, analysisArray.shape[1]]]
    for pointSet, pointDataSet in plotData.items():
        PlotGreenIndex([item[0] for item in pointDataSet],
                       [item[1] for item in pointDataSet],
                       [item[2] for item in pointDataSet],
                       [item[3] for item in pointDataSet],
                       xRegionData[pointSet],
                       yRegionData[pointSet], tempData)

def GetTemperature(date):
    url = ('https://www.wunderground.com/history/airport/KTYS/' + str(date.year) + '/'
           + str(date.month) + '/' + str(date.day) + '/DailyHistory.html') #TODO genericize to be location generalized
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
    return float(sum(imageArray[:,:,1])) / RGB, float(sum(imageArray[:, :, 0])) / RGB, float(sum(imageArray[:,:,1])) / float(sum(imageArray[:, :, 0])) #Greenness index: G / (R + G + B)

def PlotGreenIndex(timeList, greenList, redList, ratioList, xPoints, yPoints, tempData):
    print(ratioList)
    pylab.figure()
    pylab.scatter(timeList, greenList, c='g', label='Greeness Index')
    pylab.scatter(timeList, redList, c='r', label='Redness Index')
    pylab.title("Carlos Campbell Image Data")
    pylab.ylabel("Index Value")
    pylab.xlabel("Date of Picture")
    pylab.legend()
    timeLabels = []
    for timeStamp in timeList:
        timeLabels += [int(time.mktime(timeStamp.timetuple()))]

    maxGreen, maxRed = 0, 0
    minGreen, minRed = 1000, 1000
    minDateG, maxDateG, minDateR, maxDateR = 0, 0, 0, 0
    for i, greenIndex in enumerate(greenList):
        if greenIndex < minGreen:
            minGreen = greenIndex
            minDateG = timeList[i]
        elif greenIndex > maxGreen:
            maxGreen = greenIndex
            maxDateG = timeList[i]
    for i, redIndex in enumerate(redList):
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
    mpldatacursor.datacursor()
    pylab.show()

    pylab.figure()
    pylab.scatter(timeList, ratioList, c='g', label='G to R ratio')
    pylab.title("Carlos Campbell Image Data")
    pylab.ylabel("Index Value")
    pylab.xlabel("Date of Picture")
    pylab.legend()
    mpldatacursor.datacursor()
    pylab.show()
ParseImages()