
import sys
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/database')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/webscrape')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/Storage')
from imageStorage import ImageStorage
import search
from search import WebSearch
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
ws=WebSearch()  #general search class
store=ImageStorage()


#loading a source on the google map and setting source 

def loadLocalData(name, path='Images/'):
	from source import LocalStorage
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
	
def makeSearch(lat, lon, radius): #for testing expediency, gps functionality is the only concern.
							 #There are possibilities/utilities for much more.
	types=[]
	parameters=[]
	types.append('lat')
	types.append('lon')
	types.append('radius')
	parameters.append(str(lat))
	parameters.append(str(lon))
	parameters.append(str(radius))
	ws.imageSearch(types, parameters)
	
def checkSearch():
	failed=0
	for id in ws.flickr_ids:
		if dbManager.hasImage(id)==0:
			failed=failed+1
	print(str(failed)+' images failed to commit')
	
def commitSearchImages(start, end):
	i=start
	while i<end:
		image_dict=ws.getSearchData(i)
		if image_dict!='fail':
			dbManager.insertImage(image_dict['id'], image_dict['source'], image_dict['date_taken'], (image_dict['gps'][0], image_dict['gps'][1]), image_dict['gps'][0], image_dict['gps'][1], url=image_dict['url'])
		i+=1
		if i%20==0:
			print('Images '+str(start)+'-'+str(i)+'/'+str(ws.total)+' committed.')
			print(image_dict)
		
		
def commitSearch():
	from multiprocessing import Process
	print('Commiting '+str(ws.total)+' image metadata rows to database.')
	"""interval=ws.total//4
	p1=Process(target=commitSearchImages, args=(0, interval,))
	p1.start
	p2=Process(target=commitSearchImages, args=(interval, interval*2,))
	p2.start()
	p3=Process(target=commitSearchImages, args=(interval*2, interval*3,))
	p3.start()
	p4=Process(target=commitSearchImages, args=(interval*3, interval*4,))
	p4.start()
	p2.join()
	p3.join()
	p4.join() """
	checkSearch()
	print('Commital Complete.')
	
def storeImage(id, source, path=''):
	url=dbManager.getUrl(id, source)
	alt_id=store.downloadRequest(url)
	dbManager.addAltID(id, source, alt_id)
	store.serviceRequests()
	

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
	
			


			
			
				
			
						
	

