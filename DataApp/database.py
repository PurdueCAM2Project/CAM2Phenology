#Handles database queries
#02/12/18

import pymysql.cursors
import atexit
import datetime	
import json

filter={'min_date': 'date_taken>%s',
		'max_date': 'date_taken<%s',
		'year': 'YEAR(date_taken)=%s',
		'month': 'MONTH(date_taken)=%s',
		'day_of_year': 'DAYOFYEAR(date_taken)=%s',
		'date_taken': 'date_taken=%s',
		'region': 'images.region LIKE %s',
		'geo_range': 'ST_WITHIN(images.gps, ST_BUFFER(POINT%s, %s))' 
		}

def makeFilter(params, union=False):
	#constructing a sql 'WHERE' clause using the database schema and the params passed in
	#this is for selecting from images table
	#input: params=array of tuples of the form [(<param_key>, <value>),...]
	#output: sql, [values]
	#geo_range=[<(x, y)>, <radius>] 
	if (len(params))==0:
		return "", []
	sql="WHERE" #string used to execute query
	values=[] #values order matches ordering of respective '%s' in sql string
	condition=" "
	for param in params:
		sql=sql+condition+filter[param[0]]
		if param[0]=='geo_range':
			values.extend(param[1])
		else:
			values.append(param[1])
		condition=' AND '
		if union:
			condition=' OR '
	return sql, values
	
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
		self.tag_dict=self.getTags()
		atexit.register(self.connection.close)
		
	def query(self, sql, values=None):
		if values is None:
			self.cursor.execute(sql)
		else:
			self.cursor.execute(sql, values)
		self.connection.commit()
		return self.cursor.fetchall()
		
	def addRegion(self, region_name, latitude, longitude, radius=None):
		"""polygon="POLYGON("
		character='('
		for point in polygon_points:
			polygon=polygon+character+str(point[0])+' '+str(point[1])
			character=', '
		polygon=polygon+"))
		print (polygon)"""
		sql="INSERT IGNORE INTO regions (name, mean_point, radius) VALUES(%s, POINT%s, %s)"
		print(sql)
		mean_point=(latitude, longitude)
		self.query(sql, values=(region_name, mean_point, radius))
		
	def addLocation(self, latitude, longitude, radius, notes=None):
		gps=(latitude, longitude)
		sql="SELECT ST_DISTANCE(POINT%s, mean_point) as dist, name FROM regions ORDER BY dist asc limit 1"
		region=self.query(sql, values=(gps,))[0]['name']
		sql="INSERT INTO locations(region, gps, radius, notes) VALUES(%s, POINT%s, %s, %s)"
		self.query(sql, values=(region, gps, radius, notes))
	
	def addImage(self, id, source, date_taken, gps, latitude, longitude, userid=None, region=None, url=None, cluster_id=None, alt_id=None):
		#print(str(gps))
		if region is None:
			sql="SELECT name FROM regions ORDER BY ST_DISTANCE(POINT%s, regions.mean_point) limit 1"
			region=self.query(sql, values=(gps,))[0]['name']
		sql="REPLACE INTO images (source_id, source, region, date_taken, gps,  latitude, longitude, userid, url, cluster_id, alt_id) VALUES (%s, %s, %s, %s, POINT%s, %s, %s, %s, %s, %s ,%s)"
		self.query(sql, values=(id, source, region, date_taken, gps, latitude, longitude, userid, url, cluster_id, alt_id))	
		return 1

	def addImages(self, image_dicts):
		#adds array of image dictionaries to database
		for image in image_dicts:
			self.addImage(**image)
	
	def updateLocation(self, location_id):
		today=datetime.datetime.today()
		sql="UPDATE locations SET last_updated=%s WHERE id=%s"
		self.query(sql, values=(today, location_id))

	def createTag(self, tagname):
		self.query("INSERT INTO tags (tagname) values (%s)", values=(tagname))
		self.tag_dict=self.getTags()

	def tagImage(self, image_id, tagname, tag_data):
		if tag_name not in self.tag_dict.keys():
			print("Error, tag does not exist.")
			return 0
		tag_id=self.tag_dict[tagname]
		if tag_data is not None:
			tag_data=json.dumps(tag_data) #converting to json string
		values=(image_id, tag_id, tag_data)
		sql="REPLACE INTO tags (image_id, tag_id, tag_data) VALUES (%s, %s, %s)"
		self.query(sql, values=values)
		return 1
	
	#---Simple/Necessary Queries---
	
	def getImages(self, selection='*', filter_params=[], order_by='date_taken', limit='LIMIT 100000', union=False, tagname=None):
		#returns images based on filter_params. See makeFilter()
		#default arguments return (max)100000 images in database ordered by date_taken
		where_clause, values=makeFilter(filter_params, union=union)
		if tagname is not None:
			if tagname not in self.tag_dict.keys():
				print("Specified tag does not exist. Ignoring tag.")
			else:
				tag_id=self.tag_dict[tagname]
				values.insert(0, tag_id)
				join="INNER JOIN tag_links ON tag_links.tag_id=%s AND tag_links.image_id=images.id"
		else:
			join=""
		
		sql="SELECT "+selection+" FROM images "+join+" "+where_clause+" ORDER BY "+order_by+" "+limit
		values=tuple(values)
		return self.query(sql, values=values)
	
	def getTags(self):
		#returns a tag dictionary of all tags.  {<tag_name>: tag_id, ...}
		tags=self.query("SELECT * FROM tags")
		tag_dict={}
		for t in tags:
			tag_dict[t['tagname']]=t['id']
		return tag_dict	
		
	def getLocations(self):
		#returns array of all locations (as dictionaries)
		return self.query("SELECT *, ST_X(gps) as latitude, ST_Y(gps) as longitude FROM locations ORDER BY last_updated")
		
	def getRegions(self):
		return self.query("SELECT *, ST_X(mean_point) as latitude, ST_Y(mean_point) as longitude FROM regions")
		
	def getRegion(self, region_name):
		#returns images belonging to region <region_name>
		return self.query("SELECT * FROM images WHERE region LIKE %s", values=(region_name,))
	
	def exists(self, table_name, column, column_value):
		sql="SELECT 1 FROM %s WHERE %s=%s"
		if self.query(sql, values=(table_name, column, column_value)):
			return True
		return False
		
	def pruneIDs(self, id_list):
		#checking to see which ids are already in database
		if(len(id_list))<1:
			return None
		values=[]
		#id_list is list of values of form (id, source)
		sql="SELECT search.id, search.source FROM (SELECT %s AS id, %s AS source "
		values.extend([id_list[0][0], id_list[0][1]])
		for i in range(1, len(id_list)):
			sql=sql+"UNION ALL SELECT %s, %s "
			values.extend([id_list[i][0], id_list[i][1]])
		sql=sql+") search LEFT JOIN images ON search.id=images.source_id AND search.source LIKE images.source WHERE images.id is null"
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
	
if __name__=="__main__":
	db=DB()
	db.connect('localhost', 'root', "Phenology", "Wettfd2312")
	#db.addRegion('test', '4.0', '5.0')
	db.addRegion('test', 4.2, -23.5, [(0, 0), (10, 0), (0, 10), (0, 0)])
	
		
