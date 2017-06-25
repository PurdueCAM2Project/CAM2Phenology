from data import *
from sources import LocalStorage


#class used to plot and manipulate google map plots using gmplot (from github)
class DataMap:
	import os.path

	import gmplot.color_dicts
	
	if not os.path.exists('plots'):
		os.makedirs('plots')	

	center=(0, 0)
	lats=[]
	longs=[]
	image_coordinates=[]
	circles=[] #circles will be of the form (lat, long, radius)
	zoom=3

	def setCenter(c):
		self.center=c
	
	def setZoom(z):
		self.zoom=z

	def plotMap(self):
		import gmplot
		gmap=gmplot.GoogleMapPlotter(self.center[0], self.center[1], self.zoom)
		
		if self.lats:
			gmap.scatter(self.lats, self.longs, 'r', size=40, marker=False)
		if self.circles:
			for circle in self.circles:
				gmap.circle(circle[0], circle[1], circle[2])
		gmap.draw('plots/temp.html')

	def addPoint(self, point):
		self.lats.append(point[0])
		self.longs.append(point[1])

	def removePoint(self, point):
		index=image_coordinates.index(point)
		image_coordinates.pop(index)
		lats.pop(index)
		longs.pop(index)

	def clearPoints(self):
		self.lats=[]
		self.longs=[]
		self.image_coordinates=[]
		
	def clearCircles():
		self.circles=[]


#the procedural code below should be run to view, manipulate, and append data sets
from sources import LocalStorage

selected_images=[]
source=LocalStorage
selection=(0, 0, 0) #(lat, long, radius), used to select images within a circle
dm=DataMap()
increment=.03 #increment used to move selection
dir='data/'

#loading a source on the google map and setting source 
def loadSource(name):
	from data import getGeo
	from analysis import geoAnalyze
	
	source=LocalStorage(dir+name+'/')
	coordinates=getGeo(source)
	analysis_dict=geoAnalyze(coordinates)
	dm.zoom=10
	dm.center=analysis_dict['center']
	for coordinate in coordinates:
		dm.addPoint(coordinate)
	#selection[0]=analysis_dict['center'][0]
	#selection[1]=analysis_dict['center'][1]
	print (dm.center)
	print(dm.zoom)
	dm.plotMap()

#setting selection circle
def setSelect(lat, long, radius):
	selection[0]=lat
	selection[1]=long
	selection[2]=radius

#moving selection circle
def moveSelectRight():
	selection[1]=selection[1]+increment
def moveSelectLeft():
	selection[1]=selection[1]-increment
def moveSelectUp():
	selection[0]=selection[0]+increment
def moveSelectDown():
	selection[0]=selection[0]-increment

def makeSelection(name):
	source=LocalStorage(dir+name+'/')
	global selected_images
	selected_images=source.getInRange(selection[0], selection[1], selection[2])
	
	

#loadSource('web_ui_test')
			


			
			
				
			
						
	

