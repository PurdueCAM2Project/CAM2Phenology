#Core modules.  Top of the stack.
#inherits from database, search, and utility
#02/12/18

import os
import database
from database import DB
import modeldata
import json
import search
import datetime
import utility as util
from PIL import Image
import analysis

filter=database.filter #filter parameters for general queries on images table

if not os.path.isfile('preferences.txt'):
	import setup

if not os.path.isdir('TimeSliders'):
	os.makedirs('TimeSliders')
	
def getSetup():
	with open("preferences.txt", 'r') as file:
		params=file.read().split(" ")
		host=params[0]
		user=params[1]
		dbname=params[2]
	file.close()
	with open("apikeys.json", 'r') as file:
		keys=json.load(file)
	file.close()
	return host, user, dbname, keys
	
db=DB()
host, user, dbname, keys=getSetup()
default_image_path='images/' #where images will be downloaded to

def login(pswd):
	db.connect(host, user, dbname, pswd)
	
class MetadataList():

	#class to keep track of metadata and call functions on sets of rows from database
	image_list=[]

	def loadDataFromQuery(self, query_string):
		del self.image_list[:]
		self.image_list.extend(db.query(query_string))

	def loadData(self, *params):
		self.image_list=db.loadFilter(*params)

	def downloadImages(self, limit=None, path=default_image_path, name_by_date=False):
		import random
		regions=db.getRegions()
		print(str(path))
		for region in regions:
			if not os.path.exists(path+region['name'].replace(" ", "_")):
				os.makedirs(path+region['name'].replace(' ', '_'))
		random.shuffle(self.image_list) #might need optimizations if handling large lists (this can be done in constant time in sql)
		if limit is None or int(limit)==len(self.image_list):
			limit=len(self.image_list)
		limit=int(limit)
		for i in range(0, limit):
			image_meta=self.image_list[i]
			if name_by_date:
				file_name=image_meta['source']+"_"+image_meta['date_taken'].strftime("%Y-%m-%d_%H:%M:%S").replace(":", "-")
			else:
				file_name=image_meta['source']+str(image_meta['id'])+'.jpg'
			file_path=path+image_meta['region'].replace(" ", "_")+"/"+file_name
			util.downloadWithExif(image_meta, file_path)
	
	def getImage(self, index):
		metadata=self.image_list[index]
		util.download(metadata['url'], 'temporary.jpg')
		im=Image.open('temporary.jpg')
		return im, metadata

	def getAttribute(self, attr_key):
		#get one specific attribute from list of image dictionaries
		attrList=[self.image_list[i][attr_key] for i in range(0, len(self.image_list))]
		return attrList
		
	def plotPoints(self):
		#plot data on google map
		coordinates=[]
		for meta in self.image_list:
			coordinates.append((meta['latitude'], meta['longitude']))
		modeldata.plotGoogleMap(coordinate_groups=[coordinates])
		
	def getTimeSlider(self, delimeter):
		buckets=[]
		numbuckets=[]
		if delimeter=='weekday':
			numbuckets=7
			for i in range(0, numbuckets):
				buckets.append([])
			for image_meta in self.image_list:
				buckets[image_meta['date_taken'].weekday()].append(image_meta)
		elif delimeter=="hour":
			numbuckets=24
			for i in range(0, numbuckets):
				buckets.append([])
			for image_meta in self.image_list:
				buckets[image_meta['date_taken'].time().hour].append(image_meta)
		elif delimeter=="month":
			numbuckets=12
			for i in range(0, numbuckets):
				buckets.append([])
			for image_meta in self.image_list:
				buckets[image_meta['date_taken'].date().month-1].append(image_meta)
		elif delimeter=="year":
			numbuckets=14
			for i in range(0, numbuckets):
				buckets.append([])
			for image_meta in self.image_list:
				bucketnum=image_meta['date_taken'].date().year
				if bucketnum>=2005:
					buckets[bucketnum-2005].append(image_meta)

		return buckets
		
	def graphTimeSlider(self, delimeter):
		buckets=self.getTimeSlider(delimeter)
		modeldata.graph(buckets, delimeter)
		
	def plotTimeSlider(self, delimeter):
		buckets=self.getTimeSlider(delimeter)
		buckets1=[]
		for b in buckets:
			b1=[(b[i]['latitude'], b[i]['longitude']) for i in range(0, len(b))]
			buckets1.append(b1)
		modeldata.plotGoogleMapByTime(buckets1)
		

metadata=MetadataList()
		
def scrapeArea(latitude, longitude, radius, tag=None):
	#searches area then commits images found to database
	params={'lat': latitude, 'lon': longitude, 'radius': radius}
	ids=search.search(params) #getting ids from apis
	ids=db.pruneIDs(ids)
	search_function=search.compileData #function to compile metadata form search apis
	commit_function=db.addImages		#function to commit metadata to database
	#multithreading. see utility.pipeData()
	util.pipeData(ids, [search_function, commit_function], [3, 1], 20)
	
def scrapeLocations(update_thresh=1): #update_thresh= the threshhold that determines when to update a location
	locations=db.getLocations()
	#Scraping for new images
	for location in locations:
		if(location['last_updated'] is not None and (datetime.datetime.today()-location['last_updated']).days<update_thresh):
			break
		print('Scraping '+str((location['latitude'], location['longitude'])))
		scrapeArea(location['latitude'], location['longitude'], location['radius'], tag=location['region'])
		db.updateLocation(location['id'])

def showLocations():
	import webbrowser
	locations=db.getLocations()
	modeldata.plotGoogleMap(circle_groups=[[(locations[i]['latitude'], locations[i]['longitude'], locations[i]['radius']*1000) for i in range(0, len(locations))]])	
	webbrowser.open('temp.html')
	
def plotUserDayClusters():
	import webbrowser
	print('Not Implemented Correctly Yet.\nUsing "plotUserPaths"')
	"""query_result=db.getUserDayOrderByTime()
	
	start_clusters, end_clusters=analysis.clusterUserDays(query_result)
	points=start_clusters[0][
	circle_groups=[]
	
	circle_groups.append([(start_clusters[i][0][0], start_clusters[i][0][1], start_clusters[i][1]*1000) for i in range(0, len(start_clusters))])
	circle_groups.append([(end_clusters[i][0][0], end_clusters[i][0][1], end_clusters[i][1]*110.567*1000) for i in range(0, len(end_clusters))])
	print(str(circle_groups))
	modeldata.plotGoogleMap(circle_groups=circle_groups)
	#webbrowser.open('temp.html')"""

def plotUserPaths(filter_params=[]):
	paths=db.getUserPaths(filter_params=filter_params)
	start_markers=[]
	end_markers=[]
	for path in paths:
		start_markers.append(path[0])
		end_markers.append(path[-1])
	modeldata.plotGoogleMap(polygon_groups=paths, marker_groups=[start_markers, end_markers])
	
#def plotHourSlider(*filter_params):
	

print("Connected to: "+host)
print("User: "+user)
print("Database: "+dbname)
print("API Keys: "+str(keys))


	
	
	
