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

tables=['regions', 'clusters', 'images']	

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
	
def assignRegions():
#Goes through all images and assigns them a region if they fall within the circle given by a regions mean_point and radius
	sql="UPDATE images INNER JOIN regions ON ST_WITHIN(images.gps, ST_BUFFER(regions.mean_point, regions.radius/111))"
	sql=sql+" SET images.region=regions.name"
	cursor.execute(sql)
	connection.commit()

def updateRegion(region_name):
	region_name="'"+region_name
	region_name=region_name+"'"
	sql="UPDATE regions SET num_images= (SELECT COUNT(*) FROM images WHERE region LIKE "+region_name+")" 
	cursor.execute(sql)
	connection.commit()	
		
def insertImage(id, source, date_taken, gps, latitude, longitude, region="Smoky Mountains", url=None, cluster_id=None, alt_id=None):
	#print(str(gps))
	sql="REPLACE INTO images (id, source, region, date_taken, date_retrieved, gps,  latitude, longitude, url, cluster_id, alt_id) VALUES (%s, %s, %s, %s, %s, point"+str(gps)+", %s, %s, %s, %s, %s)"
	cursor.execute(sql, (id, source, region, date_taken, timestamp, latitude, longitude, url, cluster_id, alt_id))
	sql="UPDATE regions SET num_images= num_images+1 WHERE name LIKE '"+str(region)+"'"
	cursor.execute(sql)
	connection.commit()

def clusterImages(region_name, fragment=0.3):
	#sort images into clusters by location.
	#A smaller fragment implies more clusters and lower cluster size
	#A larger fragment implies less clusters and a higher cluster size
	
	def calcDistance(coordinate1, coordinate2):
		import math
		dist=math.sqrt((coordinate1[0]-coordinate2[0])**2+(coordinate1[1]-coordinate2[1])**2)
		return dist
	sql="UPDATE images SET cluster_id=NULL WHERE region LIKE %s"
	cursor.execute(sql, (region_name))
	connection.commit()
	sql="DELETE FROM clusters WHERE region_name LIKE %s"
	cursor.execute(sql, (region_name))
	connection.commit()
	sql="SELECT AVG(ST_X(gps)), AVG(ST_Y(gps)) FROM images WHERE region like %s"
	cursor.execute(sql, (region_name))
	averages=cursor.fetchall()[0]
	average_point=(averages['AVG(ST_X(gps))'], averages['AVG(ST_Y(gps))'])
	sql="SELECT AVG(ST_DISTANCE(POINT"+str(average_point)+", gps)) as average_point FROM images WHERE region like %s"
	#print(sql)
	cursor.execute(sql, (region_name))
	average_dist=cursor.fetchall()[0]["average_point"]*fragment #setting the max distance from a point to a cluster.
	#print(str(average_dist))
	clusters=[]
	sql="SELECT ST_X(gps) as lat, ST_Y(gps) as lon FROM images WHERE region LIKE %s"
	cursor.execute(sql, (region_name))
	coordinates=cursor.fetchall()
	#print(str(coordinates))
	for coordinate in coordinates:
		#print(str(coordinate))
		flag=True
		min_dist=average_dist
		cluster_ref={}
		cluster_ref['meanpoint']=(0, 0)
		cluster_ref['radius']=average_dist
		cluster_ref['size']=0
		for cluster in clusters:
			dist=calcDistance(cluster['meanpoint'], (coordinate['lat'], coordinate['lon']))
			if dist<min_dist:
				flag=False
				min_dist=dist
				cluster_ref=cluster
		if(min_dist>cluster_ref['radius']):
			cluster_ref['radius']=min_dist
		cluster_ref['size']=cluster_ref['size']+1
		size=cluster_ref['size']
		meanlat=(coordinate['lat']/size)+(cluster_ref['meanpoint'][0]*(size-1))/size
		meanlong=(coordinate['lon']/size)+(cluster_ref['meanpoint'][1]*(size-1))/size	
		cluster_ref['meanpoint']=(meanlat, meanlong)
		if(flag):
			clusters.append(cluster_ref)
	for cluster in clusters:
		sql="INSERT INTO clusters (gps, radius, region_name, num_images) VALUES (POINT"+str(cluster['meanpoint'])+", %s, %s, %s)"
		cursor.execute(sql, (cluster['radius'], region_name, cluster['size']))
	connection.commit()
	sql="UPDATE images INNER JOIN clusters on ST_WITHIN(images.gps, ST_BUFFER(clusters.gps, clusters.radius)) SET images.cluster_id=clusters.id"
	cursor.execute(sql)
	connection.commit()
	
def insertImageNote(id, source, note):
	if len(note)>500:
		print('Note exceeds max database length')
		return 
	sql="UPDATE images SET notes=%s WHERE id=%s AND source LIKE %s"
	cursor.execute(sql, (note, id, source))
	connection.commit()
	
def updateImageRating(id, source, rating):
	#A way to assess useablility
	#The rating must be -1, 0 or 1.
	#This rating must be made by a human. 
	#1->useable
	#-1->not useable
	#0->unrated
	#Note: Attribute stored in database as 'useable'
	if(rating==1 or rating==-1 or rating==0):
		sql="UPDATE images SET useable=%s WHERE id=%s AND source LIKE '"+source+"'"
		cursor.execute(sql, (rating, id))
		connection.commit()
	else:
		print("Rating must be -1, 0, or 1.\nRating not applied.")
	
def addAltID(id, source, alt_id):
	#This is a way to keep a reference to the image when it is moved to a storage system
	sql="UPDATE images SET alt_id=%s WHERE id=%s AND source LIKE '"+source+"'"
	cursor.execute(sql, (alt_id, id))
	connection.commit()

def updateUserid(image_id, userid, source):
	sql="UPDATE images SET userid=%s WHERE id=%s AND source LIKE '"+source+"'"
	cursor.execute(sql, (userid, image_id))
	connection.commit()
	
def updateHaspeople(image_id, haspeople, source):
	sql="UPDATE images SET haspeople=%s WHERE id=%s AND source LIKE '"+source+"'"
	cursor.execute(sql, (haspeople, image_id))
	connection.commit()
	
#----------------------------------

#--selection functions--

def getImageInfo(id, source):
	sql="SELECT * FROM images WHERE id=%s and source LIKE '"+source+"'"
	cursor.execute(sql, (id))
	rows=cursor.fetchall()
	return rows[0]

def getTable(table_name, limit=None):
	#Select all (or <limit>) rows from given table name
	sql="SELECT * FROM "+str(table_name)
	if limit is not None:
		sql=sql+" LIMIT "+str(limit)
	cursor.execute(sql)
	return cursor.fetchall()
	
def getRegionInfo(region):
	sql="SELECT * regions WHERE name LIKE '"+str(region)+"'"
	cursor.execute(sql)
	return cursor.fetchall()[0]
	
def getYear(year, region=None):
	sql="SELECT * FROM images WHERE YEAR(date_taken)=%s"
	if region is not None:
		sql=sql+" AND region LIKE '"+region+"'"
	cursor.execute(sql, (year))
	return cursor.fetchall()

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
	

def selectRegion(region_name, limit=''):
	#selects all images from a region
	"""returns an array of dictionaries corresponding to the database rows.
	The array is ordered by date_taken"""
	region_name="'"+region_name
	region_name=region_name+"'"
	sql='SELECT * FROM images WHERE region LIKE '+region_name+' ORDER BY date_taken'+limit
	print(sql)
	cursor.execute(sql)
	return cursor.fetchall()

def selectClusters(region_name):
	#Selects the clusters from the given region
	sql="SELECT ST_X(gps) as lat, ST_Y(gps) as lon, radius*111 as radius FROM clusters where region_name LIKE %s"
	cursor.execute(sql, (region_name))
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
		coordinate_radius=circle[1]/111
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
	
def selectAttribute(attribute, limit=None, parameters=""):
	#Selects the values of the specified attribute from the 'images' table
	#<parameters> can be a sql 'WHERE' clause
	sql="SELECT "+attribute+" FROM images"
	sql=sql+parameters
	if limit is not None:
		sql=sql+" limit "+str(limit)
	cursor.execute(sql)
	
	return cursor.fetchall()
	
def getDateFrequencies(parameters=""):
	frequencies={}
	sql="SELECT YEAR(date_taken) AS year, MONTH(date_taken) AS month, COUNT(*) AS freq FROM images "+parameters+" GROUP BY year, month ORDER BY freq"
	cursor.execute(sql)
	frequencies['year/month']=cursor.fetchall()
	sql="SELECT MONTH(date_taken) AS month, DAY(date_taken) as day, COUNT(*) AS freq FROM images "+parameters+" GROUP BY month, day ORDER BY freq desc"
	cursor.execute(sql)
	frequencies['month/day']=cursor.fetchall()
	sql="SELECT MONTH(date_taken) as month, HOUR(date_taken) AS hour, COUNT(*) AS freq FROM images "+parameters+" GROUP BY month, hour ORDER BY freq desc"
	cursor.execute(sql)
	frequencies['month/hour']=cursor.fetchall()
	sql="SELECT MONTH(date_taken) as month, DAYOFWEEK(date_taken) as weekday, COUNT(*) AS freq FROM images "+parameters+" GROUP BY month, weekday ORDER BY freq desc"
	cursor.execute(sql)
	frequencies['month/weekday']=cursor.fetchall()
	sql="SELECT DAYOFWEEK(date_taken) AS weekday, HOUR(date_taken) AS hour, COUNT(*) AS freq FROM images "+parameters+" GROUP BY weekday, hour ORDER BY freq desc"
	cursor.execute(sql)
	frequencies['weekday/hour']=cursor.fetchall()
	return frequencies
	
	
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
	


	
	
	
	

	

	

