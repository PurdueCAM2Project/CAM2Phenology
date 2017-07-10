import pymysql.cursors
import getpass
import os.path
import json

print("Using MySQL server @ 128.46.213.21")

if not os.path.exists('preferences.json'):
	import db_setup

with open('preferences.json') as file:
	pref=json.load(file)
file.close

print("Using database "+pref['database']+", with user name: "+pref['user name'])	
pswd=getpass.getpass("Input password:")
connection=pymysql.connect(host='128.46.213.21',
			user=pref['user name'],
			password=pswd,
			db=pref['database'],
			cursorclass=pymysql.cursors.DictCursor)
							
cursor=connection.cursor()							

def query(sql, values=None):
	if values is None:
		cursor.execute(sql)
	else:
		cursor.execute(sql, values)
	connection.commit()

#insertion and deletion methods
def insertRegion(name, num_images=0, mean_point=None):
	sql= "INSERT IGNORE INTO regions (name, num_images, mean_point) VALUES (%s, %s, %s)"
	cursor.execute(sql, (name, num_images, mean_point))
	connection.commit()
		
def insertImage(id, region, date_taken, date_retrieved, gps, latitude, longitude, source=None, cluster_id=None):
	#print(str(gps))
	sql="REPLACE INTO images (id, region, date_taken, date_retrieved, gps,  latitude, longitude, source, cluster_id) VALUES (%s, %s, %s, %s, point"+str(gps)+", %s, %s, %s, %s)"
	cursor.execute(sql, (id, region, date_taken, date_retrieved, latitude, longitude, source, cluster_id))
	#sql="UPDATE regions SET num_images= num_images+1 WHERE name LIKE '"+str(region)+"'"
	#cursor.execute(sql)
	connection.commit()

def updateRegion(region_name):
	region_name="'"+region_name
	region_name=region_name+"'"
	sql="UPDATE regions set num_images= (SELECT COUNT(*) FROM images WHERE region LIKE "+region_name+")" 
	cursor.execute(sql)
	connection.commit()	

#--selection methods--

#selects all images from a region
def selectRegion(region_name):
	"""returns an array of dictionaries corresponding to the database rows.
	The array is ordered by date_taken"""

	region_name="'"+region_name
	region_name=region_name+"'"
	sql='SELECT * FROM images WHERE region LIKE '+region_name+' ORDER BY date_taken'
	print(sql)
	cursor.execute(sql)
	return cursor.fetchall()
	
#selects specified number of images at random from all images
def sampleImages(num_images=100):
	"""Every image has a chance dictated by 'fragment'*1.01 to be selected.
	This somewhat non-intuitive approach was used for efficiency"""
	
	sql="SELECT SUM(num_images) AS total_images FROM regions"
	cursor.execute(sql)
	total_images=cursor.fetchall()[0]['total_images']
	fragment=float(num_images/total_images)
	fragment=fragment*1.01
	sql="SELECT * FROM images WHERE RAND()<=%s LIMIT %s"
	cursor.execute(sql, (fragment, num_images))
	return cursor.fetchall()
	


	
	
	
	

	

	

