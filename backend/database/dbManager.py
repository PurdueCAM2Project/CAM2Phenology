import pymysql.cursors
import getpass
import os.path
import json
import atexit
from datetime import datetime

timestamp=datetime.today()

#Will initialize and connect on import

mysql_host='128.46.213.21'
print("Using MySQL server @ "+mysql_host)

if not os.path.exists('preferences.json'):
	import db_setup

with open('preferences.json') as file:
	pref=json.load(file)
file.close

print("Using database "+pref['database']+", with user name: "+pref['user name'])	

pswd=getpass.getpass("Input password:")
connection=pymysql.connect(host=mysql_host, #hpvision has address '128.46.213.21. testing on localhost'
			user=pref['user name'],
			password=pswd,
			db=pref['database'],
			cursorclass=pymysql.cursors.DictCursor)
							
cursor=connection.cursor()							

#general purpose query function
def query(sql, values=None):
	if values is None:
		cursor.execute(sql)
	else:
		cursor.execute(sql, values)
	connection.commit()
	
#---Phenology Database Functions---	

#--insertion functions--

def insertRegion(name, num_images=0, mean_point=None):
	sql= "INSERT IGNORE INTO regions (name, num_images, mean_point) VALUES (%s, %s, %s)"
	cursor.execute(sql, (name, num_images, mean_point))
	connection.commit()
		
def insertImage(id, source, date_taken, gps, latitude, longitude, region="Smoky Mountains", url=None, cluster_id=None, alt_id=None):
	#print(str(gps))
	sql="REPLACE INTO images (id, source, region, date_taken, date_retrieved, gps,  latitude, longitude, url, cluster_id, alt_id) VALUES (%s, %s, %s, %s, %s, point"+str(gps)+", %s, %s, %s, %s, %s)"
	cursor.execute(sql, (id, source, region, date_taken, timestamp, latitude, longitude, url, cluster_id, alt_id))
	sql="UPDATE regions SET num_images= num_images+1 WHERE name LIKE '"+str(region)+"'"
	cursor.execute(sql)
	connection.commit()
	
def insertImageNote(id, source, note):
	if len(note)>500:
		print('Note exceeds max database length')
		return 
	sql="UPDATE images SET notes=%s WHERE id=%s AND source LIKE %s"
	cursor.execute(sql, (note, id, source))
	connection.commit()

def updateRegion(region_name):
	region_name="'"+region_name
	region_name=region_name+"'"
	sql="UPDATE regions SET num_images= (SELECT COUNT(*) FROM images WHERE region LIKE "+region_name+")" 
	cursor.execute(sql)
	connection.commit()	
	
#This method is to be used when the an is commited to a storage location having key/path=alt_id
def addAltID(id, source, alt_id):
	sql="UPDATE images SET alt_id=%s WHERE id=%s AND source LIKE '"+source+"'"
	cursor.execute(sql, (alt_id, id))
	connection.commit()
	
#----------------------------------

#--selection functions--

def getImageInfo(id, source):
	sql="SELECT * FROM images WHERE id=%s and source LIKE '"+source+"'"
	cursor.execute(sql, (id))
	rows=cursor.fetchall()
	return rows[0]

#checks to see if image is in database	
def hasImage(id):
	#Returns 0 if the image is not found
	sql='SELECT COUNT(*) FROM images WHERE ID=%s'
	cursor.execute(sql, (id))
	dict=cursor.fetchall()[0]
	return dict['COUNT(*)']

#get the original url of an image	
def getUrl(id, source):
	sql="SELECT url FROM images WHERE id=%s AND source LIKE '"+source+"'"
	print(sql)
	cursor.execute(sql, (id))
	dict=cursor.fetchall()
	return dict[0]['url']
	
#selects all images from a region
def selectRegion(region_name, limit=''):
	"""returns an array of dictionaries corresponding to the database rows.
	The array is ordered by date_taken"""
	region_name="'"+region_name
	region_name=region_name+"'"
	sql='SELECT * FROM images WHERE region LIKE '+region_name+' ORDER BY date_taken'+limit
	print(sql)
	cursor.execute(sql)
	return cursor.fetchall()
	
def selectFilter(region=None, circle=None, date_range=None):
	#circle should be formatted as a tuple ((latitude, longitude), kilometer_radius)
	#date_range should be formatted a tuple (min_date, max_date)
	values=[]
	sql="SELECT * FROM images"
	flag=False
	if region is not None:
		flag=True
		sql=sql+" WHERE region LIKE %s"
		values.append(region)
	if circle is not None:
		if (flag):
			sql=sql+" AND"
		else:
			sql=sql+" WHERE"
		flag=True
		coordinate_radius=circle[1]/69
		sql=sql+" ST_WITHIN(gps, ST_BUFFER(POINT"+str(circle[0])+", %s))=1"
		values.append(coordinate_radius)
	if date_range is not None:
		if flag:
			sql=sql+" AND"
		else:
			sql=sql+" WHERE"
		sql=sql+" date_taken>=%s AND date_taken<=%s"
		values.append(date_range[0])
		values.append(date_range[1])
	sql=sql+" ORDER BY date_taken"
	value_tup=tuple(values)
	print(sql)
	cursor.execute(sql, value_tup)
	return cursor.fetchall()
		
	
#selects specified number of images at random from all images
def sampleImages(num_images=100):
	"""Every image has a chance dictated by 'fragment'*1.01 to be selected.
	This somewhat non-intuitive approach was used for efficiency"""
	
	#sql="SELECT SUM(num_images) AS total_images FROM regions"  (This sql statement will be re implemented when region_name is in all images
	sql="SELECT COUNT(*) AS total_images FROM images"
	cursor.execute(sql)
	total_images=cursor.fetchall()[0]['total_images']
	if(total_images==0):
		return []
	fragment=float(num_images/total_images)
	fragment=fragment*1.01
	sql="SELECT * FROM images WHERE RAND()<=%s LIMIT %s"
	cursor.execute(sql, (fragment, num_images))
	return cursor.fetchall()
	
#----------------------------------------------------

#---End Phenology Database Functions---	


#---Image Storage Functions---

#--Insertion Functions--

def insertStoredImage(id, image_hash, url=None):
	#recording an image that is downloaded and stored (somewhere)
	sql="INSERT INTO storedImages (id, image_hash, url) VALUES (%s, '"+str(image_hash)+"', %s)"
	cursor.execute(sql, (id, url))
	connection.commit()
	
#--Boolean Functions--

#Using a PIL average_hash to detect image duplicates and to access images
def isImageStored(image_hash):
	sql="SELECT COUNT(*) FROM storedImages WHERE image_hash LIKE '"+str(image_hash)+"'"
	cursor.execute(sql)
	dict=cursor.fetchall()
	return dict[0]['COUNT(*)']

#Returns id of image with given image_hash
def idFromHash(image_hash):
	sql="SELECT id FROM storedImages WHERE image_hash LIKE '"+str(image_hash)+"'"
	cursor.execute(sql)
	dict=cursor.fetchall()
	return dict[0]['id']

def closeConnection():
	connection.close()
	
atexit.register(closeConnection)
	


	
	
	
	

	

	

