from data import *
import sources
from sources import *
import os
import os.path

def display():
	import display
#important variables
dataDict={}
coordinates=[]
if not os.path.isfile('preferences.txt'):
	with open('preferences.txt', 'w+') as file:
		file.write('data/')
with open('preferences.txt') as file:
	preferences=file.read().splitlines()
dir=preferences[0]
if not os.path.exists(dir):
	os.makedirs(dir)
localData=os.listdir(dir)
localData.append(' ')
def changeStorage(newDir):
	with open('preferences.txt','w+') as file:
		preferences[0]=newDir+'/'
		file.writelines(preferences)
		dir=newDir+'/'
def newLocalStorage(directory, buffer):
	import copy
	print(dir+directory)
	source=sources.makeLocalStorage(dir+directory+'/')
	newList=DataList(copy.copy(source), int(buffer))
	dataDict[directory]=copy.copy(newList)

def modifyPlot(plotCoordinates, plot):
	import matplotlib.pyplot
	i=0
	while i<len(plotCoordinates)-1:
		coordinate=plotCoordinates[i]
		plot.plot(coordinate[1], coordinate[0], 'ko')
		i=i+1
	coordinate=plotCoordinates[i]
	plot.plot(coordinate[1], coordinate[0], 'go')
def initialPlot(sourceString, plot):
	allCoordinates=getGeo(dataDict[sourceString])
	increment=(dataDict[sourceString].numImages//10)
	if increment==0:
		increment=1
	i=0
	while i<dataDict[sourceString].numImages:
		plot.plot(allCoordinates[i][1], allCoordinates[i][0])
		i=i+increment
def plotAllPoints(sourceString, plot):
	allCoordinates=getGeo(dataDict[sourceString])
	modifyPlot(allCoordinates, plot)
def addPoint(sourceString, plot):
	exif_dict=dataDict[sourceString].getNext(0)[1]
	coordinate=getGPS(exif_dict)
	coordinates.append(coordinate)
	modifyPlot(coordinates, plot)	
def removePoint(sourceString, plot):
	exif_dict=dataDict[sourceString].getNext(0)[1]
	coordinate=getGPS(exif_dict)
	coordinates.remove(coordinate)
	modifyPlot(coordinates, plot)
def makeGMPlot(source):
	import gmplot
	from data import getGeo
	lats=[]
	longs=[]
	for coordinate in coordinates:
		lats.append(coordinate[0])
		longs.append(coordinate[1])
	gmap=gmplot.GoogleMapPlotter(35.6583, -83.5200, 13.8)
	coordinates=getGeo(source)
#       gmap.heatmap(lats, longs, radius=50, threshold=40000, dissipating=True)
	gmap.scatter(lats, longs, 'r', size=20, marker=False)
	gmap.draw('/mnt/c/Users/emars/Desktop/ccLargeGeoPlot2.html')
"""	
source=makeLocalStorage(dir+'CCLargeGeo/')
makeGMPlot(source) """	
#import display
