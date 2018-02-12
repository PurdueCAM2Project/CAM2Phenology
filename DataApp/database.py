#Handles database queries
#02/12/18

import pymysql.cursors
import atexit
import datetime		
	
class DB():
#Access and update database

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
		self.filter="" #"WHERE" clause of sql query
		
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
		
	def addImage(self, id, source, date_taken, gps, latitude, longitude, userid=None, region=None, url=None, cluster_id=None, alt_id=None):
		#print(str(gps))
		if region is None:
			sql="SELECT name FROM regions ORDER BY ST_DISTANCE(POINT%s, regions.mean_point) limit 1"
			region=self.query(sql, values=(gps,))[0]['name']
		sql="REPLACE INTO images (id, source, region, date_taken, gps,  latitude, longitude, userid, url, cluster_id, alt_id) VALUES (%s, %s, %s, %s, POINT%s, %s, %s, %s, %s, %s ,%s)"
		self.query(sql, values=(id, source, region, date_taken, gps, latitude, longitude, userid, url, cluster_id, alt_id))	
		
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
		#returns array of all locations (as dictionaries)
		return self.query("SELECT *, ST_X(gps) as latitude, ST_Y(gps) as longitude FROM locations ORDER BY last_updated")
		
	def getRegions(self):
		return self.query("SELECT *, ST_X(mean_point) as latitude, ST_Y(mean_point) as longitude FROM regions")
		
	def getRegion(self, region_name):
		return self.query("SELECT * FROM images WHERE region LIKE %s", values=(region_name,))
	
	def exists(self, table_name, column, column_value):
		sql="SELECT 1 FROM %s WHERE %s=%s"
		if self.query(sql, values=(table_name, column, column_value)):
			return True
		return False
		
	def pruneIDs(self, id_list):
		if(len(id_list))<1:
			return None
		values=[]
		#id_list is list of values of form (id, source)
		sql="SELECT search.id, search.source FROM (SELECT %s AS id, %s AS source "
		values.extend([id_list[0][0], id_list[0][1]])
		for i in range(1, len(id_list)):
			sql=sql+"UNION ALL SELECT %s, %s "
			values.extend([id_list[i][0], id_list[i][1]])
		sql=sql+") search LEFT JOIN images ON search.id=images.id AND search.source LIKE images.source WHERE images.id is null"
		rows=self.query(sql, values=tuple(values))
		pruned_ids=[]
		for row in rows:
			pruned_ids.append((row['id'], row['source']))
		return pruned_ids

"""class SQL: #Class to format sql queries (unsure if this is needed yet)

	in_circle="ST_WITHIN(gps, ST_BUFFER(POINT%s, %s))=1"
	
	def formatWhere(param_dict):
		sql="WHERE"
		andstring=""
		values=[]
		for key in param_dict.keys():
			
			sql=sql+" "+andstring+key
			if(isinstance(param_dict[key], str)):
				sql=sql+" LIKE %s"
				values.append(key)
			elif key!="gps" and key!="radius":
				sql=sql+"=%s"
				values.append(key)
			else:
				sql=sql+" "+in_circle
				values.extend([param_dict['gps'], param_dict['radius']])
			andstring="and "
		return sql, values
		
			
			
	def select(table, attributes=['*'], where={}):
		#Simple select statement. Not useable for joining or complex queries in general
		sql="SELECT "+attributes[0]
		for i in range(1, len(attributes)):
			sql=sql+", "+attributes[i]
		where_clause, values=formatWhere(where)
		sql=" FROM "+table+" "+where_clause
		return sql, values"""
	
	
		