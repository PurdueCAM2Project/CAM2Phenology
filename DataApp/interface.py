#command line application to access all functions
#data is loaded and then accessed
#The program will crash if a function is attempted that the user does not have permission for
#02/12/18

import core
import getpass
import sys

meta=core.MetadataList() #class to keep track of loaded data. See core.py

def displayData(dict_list):
	#displays rows of dicts (needs improvement)
	if not dict_list:
		print("none")
		return 
	header=list(dict_list[0].keys())
	for dict in dict_list:
		output=""
		for key in header:
			output=output+key+": "+str(dict[key])+" | "
	print(output)
	
def queryDatabase():
	#query database and show result
	sql=""
	print("Querying database.  Type 'c' to exit.")
	sql=input("mysql > ")
	while sql!='c':
		print(displayData(core.db.query(sql=sql)))
		sql=input("mysql > ")
		
def addRegion():
	#add region to database
	region_name=input('Enter Region Name: ')
	latitude=input('Enter Latitude: ')
	longitude=input("Enter Longitude: ")
	core.db.addRegion(region_name, latitude, longitude)
	
def addLocation():
	#add location to database.  location.region_name will be the closest region
	latitude=input('Enter Latitude: ')
	longitude=input('Enter Longitude: ' )
	radius=input('Enter Radius: ')
	notes=input("Enter location notes: ")
	if notes=="":
		notes=None
	core.db.addLocation(float(latitude), float(longitude), float(radius), notes=notes)
	

	
def downloadData():
	#downloads data loaded into <meta>
	if not meta.image_list:
		print("No data is loaded")
		return
	limit=input("Enter the amount of images you would like to download (press enter to download all images): ")
	if limit=="" or int(limit)>len(meta.image_list):
		limit=len(meta.image_list)
	limit=int(limit)
	print("Downloading "+str(limit)+" images to "+core.default_image_path)
	meta.downloadImages(limit)
	
def updateData():
	#re scrape locations
	update_thresh=input("Enter the minimum days since last location update.\nAll locations that have not been updated for a time longer than the time specified will be updated.\nEX: Entering 0 will update all locations, entering 1 will update all locations that have not been updated for over a day.\n")
	print("Updating Locations")
	core.scrapeLocations(int(update_thresh))
		
def loadRegion():
	#loads region into <meta>
	print("Regions:")
	displayData(core.db.getRegions())
	region_name=input("Input Region Name")
	meta.image_list=core.db.getRegion(region_name)
	print(str(len(meta.image_list))+" images' metadata loaded")
	
def loadQuery():
	#loads query result into <meta>.  should be list of images.
	print("Enter Query.  Images returned from query will be loaded.")
	sql=input("mysql > ")
	meta.image_list=core.db.query(sql)
	print(str(len(meta.image_list))+" images loaded")
	
parameters={'latitude': None, 'longitude': None, 'radius': None}
functions={'q': queryDatabase, 'al': addLocation, 'ar': addRegion, 'ud': updateData, 'lr': loadRegion, 'lq': loadQuery, 'dd': downloadData, 'e': sys.exit}	

def showFunctions():
	print("Possible Functions:")
	displayData([functions])
	
if __name__=='__main__':
	core.login(getpass.getpass("Input password: "))
	while True:
		func=input("Enter Input Function (type 'h' to show possible functions):\nDataApp> ")
		if func=='h':
			showFunctions()
		else:
			functions[func]()