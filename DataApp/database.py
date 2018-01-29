#Handles database queries

import pymysql.cursors
import atexit
import datetime

class DB():

	def connect(self, host, user, dbname, pswd):
		#connecting to database
		self.connection=pymysql.connect(
			host=host, 
			user=user,
			password=pswd,
			db=dbname,
			cursorclass=pymysql.cursors.DictCursor)					
		self.cursor=self.connection.cursor()
		atexit.register(self.connection.close)
	
	def query(self, sql, values=None):
		if values is None:
			self.cursor.execute(sql)
		else:
			self.cursor.execute(sql, values)
		self.connection.commit()
		return self.cursor.fetchall()
	
	def addRegion(self, region_name, latitude, longitude, radius=None):
		sql="INSERT IGNORE INTO regions (name, mean_point, radius) VALUES(%s, POINT%s, %s)"
		mean_point=(latitude, longitude)
		self.query(sql, values=(region_name, mean_point, radius))
		
	def addLocation(self, latitude, longitude, radius, notes=None):
		gps=(latitude, longitude)
		sql="SELECT ST_DISTANCE(POINT%s, mean_point) as dist, name FROM regions ORDER BY dist DESC limit 1"
		region=self.query(sql, values=(gps,))[0]['name']
		sql="INSERT INTO locations(region, gps, radius, notes) VALUES(%s, POINT%s, %s, %s)"
		self.query(sql, values=(region, gps, radius, notes))
		
	def addImage(self, id, source, location_id, date_taken, gps, latitude, longitude, region=None, url=None, cluster_id=None, alt_id=None):
		#print(str(gps))
		if region is None:
			sql="SELECT region FROM locations WHERE id=%s"
		region=self.query(sql, values=(location_id))[0]['region']
		sql="REPLACE INTO images (id, source, location_id, region, date_taken, gps,  latitude, longitude, url, cluster_id, alt_id) VALUES (%s, %s, %s, %s, %s, POINT%s, %s, %s, %s, %s, %s)"
		self.query(sql, values=(id, source, location_id, region, date_taken, gps latitude, longitude, url, cluster_id, alt_id))	

		
	def addImages(self, image_dicts):
		#adds array of image dictionaries to database
		for image in image_dicts:
			self.addImage(**image)
	
	def updateLocation(self, location_id):
		today=datetime.datetime.today()
		sql="UPDATE locations SET last_updated=%s WHERE id=%s"
		self.query(sql, values=(today, location_id))
			
	#---Simple/Necessary Queries---
	def getLocations(self):
		#returns array of all locationsS
		sql="SELECT * FROM locations"
		return self.query(sql)
		
	def exists(self, table_name, column, column_value):
		sql="SELECT 1 FROM %s WHERE %s=%s"
		if self.query(sql, values=(table_name, column, column_value)):
			return True
		return False
		
	
if __name__=='__main__':
	db=DB()
	db.connect('localhost', 'root', 'Phenology', 'Wettfd2312')
	db.addRegion('Great Smoky Mountains', 35.6582, -83.52)
	db.addLocation(35.65, -83.4, 2)	
	
		