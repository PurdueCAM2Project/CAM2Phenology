import dbManager

test=int(input("Please input test number.\nIf you do not know what this means, please read the code."))

def commitFolder(dir, region_name):
	import data
	import os
	images=os.listdir(dir)
	dbManager.insertRegion(region_name)
	for image in images:
		exif_dict=data.getEXIF(dir+image)
		date_taken=data.dateToDay(data.getDateTaken(exif_dict))
		date_retrieved=data.getDateRetrieved(exif_dict)
		#print (date_retrieved);
		id=int(data.getID(exif_dict))
		gps=data.getGPS(exif_dict)
		lat=gps[0]
		long=gps[1]
		gps=(gps[0], gps[1])
		dbManager.insertImage(id, region_name, date_taken, date_retrieved, gps, lat, long, source='flickr')
	dbManager.updateRegion(region_name)

if test==1:		
	commitFolder('Images/web_ui_test/', 'Test')

elif test==2:
	region=input("Specify Region: ")
	rows=dbManager.selectRegion(region)
	for row in rows:
		print (row)	

dbManager.connection.close()
		
		
		
		
	
