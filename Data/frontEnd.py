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
testSource=LocalStorage(dir+'CCLargeGeo/')
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

#Methods to deal with pyplot in display
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
	allCoordinates=getGeo(dataDict[sourceString].source)
	increment=(dataDict[sourceString].source.total//10)
	if increment==0:
		increment=1
	i=0
	while i<dataDict[sourceString].source.total:
		plot.plot(allCoordinates[i][1], allCoordinates[i][0])
		i=i+increment
def plotAllPoints(sourceString, plot):
	allCoordinates=getGeo(dataDict[sourceString].source)
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
#END pyplot methods

#below methods to create and manipulate google map plots
def makeGMPlot(gmCoordinates):
	import gmplot
	from data import getGeo
	lats=[]
	longs=[]
	tempList=dataList
	for coordinate in gmCoordinates:
		
		lats.append(coordinate[0])
		longs.append(coordinate[1])
	gmap=gmplot.GoogleMapPlotter(35.6583, -83.5200, 13.8)
#       gmap.heatmap(lats, longs, radius=50, threshold=40000, dissipating=True)
	gmap.scatter(lats, longs, 'r', size=20, marker=False)
	gmap.draw('/mnt/c/Users/emars/Desktop/ccLargeGeoPlot2.html')


def clusterPlot(source):	
	import analysis
	from analysis import geoCluster
	coordinates=getGeo(source)
	dict=geoCluster(coordinates, .1)
	groups=[]
	for cluster in dict['clusters']:
		groups.append(cluster['points'])
	data.makeGMPlot(groups)

def makeTimeSlider(source):
	from data import getDates, TimeSlider
	from analysis import dateSort, dateAnalyze
	dates=getDates(testSource)
	new_dates=dateSort(dates)
	print(new_dates)
	info=dateAnalyze(new_dates)
	return TimeSlider(source, new_dates, info)


class ImageManager(object):

	from data import TimeSlider
	import PIL.Image
	from sources import LocalStorage
	def __init__(self):
		self.activeImage=Image.open('tempDisplay.jpg')
		self.activeSource=LocalStorage
		self.index=0
		self.sourceList={'Source Selection': (self.activeSource, 0)}
	
	def changeActive(self, newSourceName):
		self.sourceList[self.activeSource.directory][1]=self.index
		self.activeSource=self.sourceList[newSourceName][0]
		self.index=self.sourceList[newSourceName][1]
		self.getCurrent()

	def addLocal(self, name):
		source=sources.makeLocalStorage(dir+name+'/')
		self.index=0
		self.activeSource=source
		self.sourceList[name+'/']=(source, 0)
		 

	def getNext(self):
		self.index=self.index+1
		self.activeImage=self.activeSource.getImage(self.index)
		print(self.activeSource.getEXIF(self.index))

	def getCurrent(self):
		self.activeImage=self.activeSource.getImage(self.index)
		print(self.activeSource.getEXIF(self.index))

	def getPrevious(self):
		self.index=self.index-1
		self.activeImage=self.activeSource.getImage(self.index)
		print(self.activeSource.getEXIF(self.index))

	def addTimeSlider(self):
		ts=makeTimeSlider(self.activeSource)
		self.activeSource=TimeSlider
		self.activeSource=ts
		self.index=0
		self.sourceList['Time Slider']=(self.activeSource, 0)
	
	def nextDy(self):
		self.activeSource.nextDay()
		self.index=0
		self.activeImage=self.activeSource.getImage(0)
		print(self.activeSource.getEXIF(0))

	def previousDy(self):
		self.activeSource.previousDay()
		self.index=0
		self.activeImage=self.activeSource.getImage(0)
		print(self.activeSource.getEXIF(0))

	def nextYr(self):
		self.activeSource.nextYear()
		self.index=0
		self.activeImage=self.activeSource.getImage(0)
		print(self.activeSource.getEXIF(0))

	def previousYr(self):
		self.activeSource.previousYear()
		self.index=0
		self.activeImage=self.activeSource.getImage(0)
		print(self.activeSource.getEXIF(0))

	def goToDy(self, yr, mn, dy):
		self.activeSource.goToDay(yr, mn, dy)
		self.index=0
		self.activeImage=self.activeSource.getImage(0)
		print(self.activeSource.getEXIF(0))




