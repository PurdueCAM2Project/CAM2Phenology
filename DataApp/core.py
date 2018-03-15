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

filter=database.filter #filter parameters for general queries on images table

if not os.path.isfile('preferences.txt'):
	import setup
	
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
	
	def downloadImages(self, limit=None, path=default_image_path):
		import random
		regions=db.getRegions()
		for region in regions:
			if not os.path.exists(path+region['name']):
				os.makedirs(path+region['name'].replace(' ', '_'))
		random.shuffle(self.image_list) #might need optimizations if handling large lists (this can be done in constant time in sql)
		if limit is None or int(limit)==len(self.image_list):
			limit=len(self.image_list)
		limit=int(limit)
		for i in range(0, limit):
			image_meta=self.image_list[i]
			file_path=path+image_meta['region']+"/"+image_meta['source']+str(image_meta['id'])+'.jpg'
			util.download(image_meta['url'], file_path)
	
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
		
def scrapeArea(latitude, longitude, radius):
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
		scrapeArea(location['latitude'], location['longitude'], location['radius'])
		db.updateLocation(location['id'])
		
print("Connected to: "+host)
print("User: "+user)
print("Database: "+dbname)
print("API Keys: "+str(keys))


	
	
	
