
import sys
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/database')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/webscrape')
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/Storage')
from imageStorage import ImageStorage
import search
from search import WebSearch
import dbManager
import json
from urlViewer import MetaIterator
import flickrSearch
import atexit
import os
from multiprocessing import Process, Pipe, Queue
import atexit


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

	def setCenter(self, c):
		self.center=c
	
	def setZoom(self, z):
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
class SearchThread(object):
#Sending api requests and then committing that data to a database is time consuming.
#This class has 3 api request (scrape) threads and 1 commit thread
#This class will save search/commit progress on exit

	def __init__(self, searchFunction, commitFunction):
		self.searchFunction=searchFunction
		self.commitFunction=commitFunction
		self.search_queue=Queue()
		self.commit_queue=Queue()
		self.control_queue=Queue()
		self.p1=Process(target=self.mainThread, args=(self.commit_queue, self.control_queue,))
		with open('searches/searchDump.json', 'r') as file:
			data=json.load(file)
			self.dump_ids=data['flickr_ids']  #Loading in dumped ids
		file.close()
		print(str(len(self.dump_ids))+" saved ids ready to commit")
		atexit.register(self.dumpSearch)
			
	def startThreads(self, ids):
	#Begin scrape/commit
		print("Putting "+str(len(ids))+" into queue")
		for id in ids:
			self.search_queue.put(id)
		if self.p1.is_alive():
			print("Adding ids to existing threads")
		else:
			self.control_queue.put("restart")
			print("Starting threads")
			self.p1.start()		
		
	def scrapeData(self, search_queue, commit_queue):
	#Sending api requests with self.searchFunction. Example: flickrSearch.getImageDict(id)
		while not search_queue.empty():
			id=search_queue.get()
			image_dict=self.searchFunction(id)
			if image_dict is not None:
				commit_queue.put(image_dict)
				
	def mainThread(self, commit_queue, control_queue):
	#This is the main process thread.
	#Makes 3 processes to scrape data from ids in self.search_queue
	#Committs scraped data to database via commit_queue
		#Starting threads
		p2=Process(target=self.scrapeData, args=(self.search_queue, self.commit_queue,))
		p3=Process(target=self.scrapeData, args=(self.search_queue, self.commit_queue,))
		p4=Process(target=self.scrapeData, args=(self.search_queue, self.commit_queue,))
		p2.start()
		p3.start()
		p4.start()
		alive=3
		interval=self.search_queue.qsize()/10 #Progress monitor
		i=0
		closed_threads=0
		while(p2.is_alive() or p3.is_alive() or p4.is_alive() or not commit_queue.empty()):
			if not commit_queue.empty():
				image_dict=commit_queue.get()
				i+=1
				self.commitFunction(image_dict['id'], image_dict['source'], image_dict['date_taken'], (image_dict['gps'][0], image_dict['gps'][1]), image_dict['gps'][0], image_dict['gps'][1], url=image_dict['url'])
				if(i%interval==0):
					print(str(i)+" images committed")
			if not control_queue.empty():
				signal=control_queue.get()
				if(signal=="restart"): #Edge case: More ids are added to active queue but some processes have already closed.
					if not p2.is_alive():
						p2.start()
					if not p3.is_alive():
						p3.start()
					if not p4.is_alive():
						self.p4.start()
						
	def dumpSearch(self):
	#Saving search in a json file to either be committed later or transfered.
	#This is an exit function but can be used as an individual module
		dumped_ids=0
		dumped_data=0
		print("Emptying queues")
		while not self.search_queue.empty():
			self.dump_ids.append(self.search_queue.get())
			dumped_ids+=1
		while not self.commit_queue.empty():
			data=self.commit_queue.get()
			if data is not None:
				self.dump_ids.append(data['id'])
				dumped_data+=1
		print("Dumping "+str(dumped_ids)+" search ids and "+str(dumped_data)+" scrapped ids")
		data={'flickr_ids': self.dump_ids}
		with open('searches/searchDump.json', 'w+') as file:
			json.dump(data, file)
		file.close()
		print('Closing threads')
		if(self.p1.is_alive()):
			self.p1.join()
		print("Exit complete")
		
	def resumeCommit(self):
	#Resume committing dumped ids
		print("Starting search thread with loaded ids")
		self.startThreads(self.dump_ids)
		self.dump_ids=[]
		
	

#----declaring public variables------
dm=DataMap()  #Used to manipulate map
ws=WebSearch()  #general search class
store=ImageStorage() #storage class represents image server prototype
iterator=MetaIterator() #Class used to iterate through a list of image's metadata 
iterator.images=dbManager.sampleImages()  #intializing
threader=SearchThread(flickrSearch.getImageDict, dbManager.insertImage) #Search thread class

#--------------------------------------

#--Functions Used to load images' metadata from database and from a search. +Plot this data on google map--
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
	dm.setCenter((lat, long))
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
		
def makeSearch(lat, lon, radius): 
#for testing expediency, gps functionality is the only concern
#There are possibilities/utilities for much more. See flickr api
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
	
def commitSearch(region=None):
	threader.startThreads(ws.flickr_ids)
	
#  ----- Deprecated storage system replaced with ImageDB	-----
def storeImage(id, source, path=''):

	image_dict=dbManager.getImageInfo(id, source) #getting image metadata from database
	alt_id=store.makeRequest(image_dict, 'download') #making request and getting storage id from storage system
	dbManager.addAltID(id, source, alt_id) #recording storage id in database
	store.serviceRequests()					#servicing requests
	
def horizonRequest(id, source):
#Masks horizon 
	image_dict=dbManager.getImageInfo(id, source)
	if image_dict['alt_id'] is None:
		storeImage(id, source)
		image_dict=dbManager.getImageInfo(id, source)
	request_id=store.makeRequest(image_dict, 'detect horizon')
	store.serviceRequests()
	print("horizon detection result stored at "+store.buildPath(request_id))
#-------------------------------------------------------------------------------

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
	
			


			
			
				
			
						
	

