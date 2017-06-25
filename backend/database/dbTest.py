import dbManager


def commitFolder(dir, region_name):
	import data
	import os
	i=0
	images=os.listdir(dir)
	dbManager.insertRegion(region_name)
	for image in images:
		exif_dict=data.getEXIF(dir+image)
		date_taken=data.dateToDay(data.getDateTaken(exif_dict))
		date_retrieved=data.getDateRetrieved(exif_dict)
		print (date_retrieved);
		id=int(data.getID(exif_dict))
		gps=data.getGPS(exif_dict)
		lat=gps[0]
		long=gps[1]
		gps=(gps[0], gps[1])
		dbManager.insertImage(id, region_name, date_taken, date_retrieved, gps, lat, long, source='flickr')
		
commitFolder('/mnt/d/PhenologyGit/Data/Images/web_ui_test/', 'test')

		
dbManager.connection.close()
		
		
		
		
	
