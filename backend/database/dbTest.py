import dbManager

test=int(input("Please input test number."))

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
	
elif test==3:
	rows=dbManager.sampleImages()
	print(rows)
	print("Number of Images: "+str(len(rows)))
	rows=dbManager.sampleImages(num_images=50)
	print(rows)
	print("Number of Images: "+str(len(rows)))
	rows=dbManager.sampleImages(num_images=1000)
	#print(rows)
	print("Number of Images: "+str(len(rows)))
	
def addUrl(dir):
	import data
	import os
	images=os.listdir(dir)
	sql="UPDATE images SET source=%s WHERE id=%s"
	for image in images:
		exif_dict=data.getEXIF(dir+image)
		url=data.getUrl(exif_dict)
		id=int(data.getID(exif_dict))
		dbManager.query(sql, (url, id))		

		
		
dbManager.connection.close()
		
		
		
		
	
