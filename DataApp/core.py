#Core modules.  Top of the stack.
import os
import database
from database import DB
import json
import search

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

def login(pswd):
	db.connect(host, user, dbname, pswd)
	
def scrapeArea(latitude, longitude, radius):
	#searches area then commits images found to database
	params={'lat': latitude, 'lon': longitude, 'radius': radius}
	ids=search.search(params) #getting ids from apis
	images=search.compileData(ids)  #compiling necessarry metadata from id list
	db.addImages(images)  #adding image metadata to database
	
print(host)
print(user)
print(dbname)
print(str(keys))