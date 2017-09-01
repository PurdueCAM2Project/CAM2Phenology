
import sys
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/database')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/webscrape')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/Storage')
from imageStorage import ImageStorage
import search
from search import WebSearch
import dbManager
from urlViewer import MetaIterator

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
	zoom=12
	marker=[0, 0, 'null']

	def setCenter(c):
		self.center=c
	
	def setZoom(z):
		self.zoom=z

	def plotMap(self): #plotting map
		import gmplot #Library that plots onto google maps
		print ('Plotting Map')
		gmap=gmplot.GoogleMapPlotter(self.center[0], self.center[1], self.zoom)
		if self.points:
			lats, longs=zip(*self.points)	
			gmap.scatter(lats, longs, 'k', size=35, marker=False)
		gmap.scatter([self.marker[0]], [self.marker[1]], 'r', size=70, marker=False)
		if self.circles:
			for circle in self.circles:
				gmap.circle(circle[0], circle[1], circle[2])
		gmap.draw('plots/temp.html') #map saved locally as 'temp.html'

	def addPoint(self, point):
		self.points.append(point)

	def removePoint(self, point):
		index=points.index(point)
		self.points.pop(index)
		
	def clearPoints(self):
		self.points=[]
		
	def clearCircles(self):
		self.circles=[]		
#-----------------------------------------------

#----declaring public variables------
dm=DataMap()  #Used to manipulate map
ws=WebSearch()  #general search class
store=ImageStorage() #storage class represents image server prototype
iterator=MetaIterator() #Class used to iterate through a list of image's metadata 
iterator.images=dbManager.sampleImages()  #intializing
#--------------------------------------


#--Functions Used to load images' metadata from database and from a search--
def loadFilter(region, latitude, longitude, radius, min_date, max_date):
#Loading images from database to be displayed on the DataMap and in the MetaIterator
#Formatting data from strings passed by UI
#Refer to dbManager selectFilter function
	from analysis import geoAnalyze
	print("Loading metadata from database")
	if region=='':
		region=None	
	if latitude!='' and longitude!='' and radius!='':
		latitude=float(latitude)
		longitude=float(longitude)
		radius=float(radius)
		circle=((latitude, longitude), radius)
	else:
		circle=None
	if min_date!='' and max_date !='':
		min_date=int(min_date)
		max_date=int(max_date)
		dates=(min_date, max_date)
	else:
		dates=None
	images=dbManager.selectFilter(region, circle, dates)
	iterator.images=images
	points=[]
	for image in images:
		point=(image['latitude'], image['longitude'])
		dm.addPoint(point)
		points.append(point)
	if points:
		analysis_dict=geoAnalyze(points)
		dm.center=analysis_dict['center']
	print("Found "+str(len(images))+" that fit the specified parameters")
	dm.plotMap()
		
def loadRegion(region_name):
#deprecated by general filter above
	images=dbManager.selectRegion(region_name)
	iterator.images=images
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
	
def clearMap():
	dm.clearPoints()
	dm.clearCircles()
	dm.plotMap()
	
def clearAll():
	ws.clear()
	clearMap()
	
def addCircle(lat, long, radius):
	radius=radius*1000
	dm.circles.append((lat, long, radius))
	dm.plotMap()
	
def addMarker(marker):
	dm.marker=marker
	dm.plotMap()
	
def loadSearchSample():
	from analysis import geoAnalyze
	clearMap()
	metadata=ws.sampleSearch() #sampling 10 images from search
	iterator.images=metadata
	points=[]
	for image_data in metadata:
		point=(image_data['gps'][0], image_data['gps'][1])
		dm.addPoint(point)
		points.append(point)
	if points:
		analysis_dict=geoAnalyze(points)
		dm.center=analysis_dict['center']
	dm.plotMap()
#-----------------------------------------------	

#--Functions to search flickr and add searched images to database--
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
#Comitting metadata to database
	i=start
	while i<end:
		image_dict=ws.getSearchData(i)
		if image_dict is not None:
			dbManager.insertImage(image_dict['id'], image_dict['source'], image_dict['date_taken'], (image_dict['gps'][0], image_dict['gps'][1]), image_dict['gps'][0], image_dict['gps'][1], url=image_dict['url'])
		i+=1
		if i%20==0:
			print('Images '+str(start)+'-'+str(i)+'/'+str(ws.total)+' committed.')
			print(image_dict)
		
		
def commitSearch(region=None):
	from multiprocessing import Process
	print('Commiting '+str(ws.total)+' image metadata rows to database.')
	interval=ws.total//4
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
	p4.join() 
	checkSearch()
	print('Commital Complete.')
	
def storeImage(id, source, path=''):
	image_dict=dbManager.getImageInfo(id, source) #getting image metadata from database
	alt_id=store.makeRequest(image_dict, 'download') #making request and getting storage id from storage system
	dbManager.addAltID(id, source, alt_id) #recording storage id in database
	store.serviceRequests()					#servicing requests
	
def horizonRequest(id, source):
	image_dict=dbManager.getImageInfo(id, source)
	if image_dict['alt_id'] is None:
		storeImage(id, source)
		image_dict=dbManager.getImageInfo(id, source)
	request_id=store.makeRequest(image_dict, 'detect horizon')
	store.serviceRequests()
	print("horizon detection result stored at "+store.buildPath(request_id))
#---------------------------------------------------------------------------------	



	
"""
THIS FUNCTION IS DEPRECATED
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
"""
	
			


			
			
				
			
						
	

