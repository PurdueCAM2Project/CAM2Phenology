
import sys
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/database')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
import data
import dbManager



#class used to plot and manipulate google map plots using gmplot (gmplot was found on github)
class DataMap(object):
	import os.path
	import gmplot.color_dicts
	
	if not os.path.exists('plots'):
		os.makedirs('plots')	
	if not os.path.exists('Images'):
		os.makedirs('Images')
	
	center=(0, 0)
	points=[]
	circles=[] #circles will be of the form (lat, long, radius)
	zoom=10

	def setCenter(c):
		self.center=c
	
	def setZoom(z):
		self.zoom=z

	def plotMap(self):
		import gmplot
		gmap=gmplot.GoogleMapPlotter(self.center[0], self.center[1], self.zoom)
		lats, longs=zip(*self.points)
		if self.points:
			gmap.scatter(lats, longs, 'r', size=40, marker=False)
		if self.circles:
			for circle in self.circles:
				gmap.circle(circle[0], circle[1], circle[2])
		gmap.draw('plots/temp.html')

	def addPoint(self, point):
		self.points.append(point)

	def removePoint(self, point):
		index=points.index(point)
		self.points.pop(index)
		
	def clearPoints(self):
		self.points=[]
		
	def clearCircles():
		self.circles=[]


#the procedural code below should be run to view, manipulate, and append data sets
selected_images=[]
selection=(0, 0, 0) #(lat, long, radius), used to select images within a circle
selections=[] #list to store selections
increment=.03 #increment used to move selection
dm=DataMap()
dm.circles=selections


#loading a source on the google map and setting source 

def loadLocalData(name, path='Images/'):
	from source ismport LocalStorage
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
	
	
def loadRegion(region_name):
	images=dbManager.selectRegion(region_name)
	points=[]
	from analysis import geoAnalyze
	for image in images:
		point=(image['latitude'], image['longitude'])
		dm.addPoint(point)
		points.append(point)
		
	analysis_dict=geoAnalyze(points)
	dm.center=analysis_dict['center']
	print(dm.center)
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
	
			


			
			
				
			
						
	

