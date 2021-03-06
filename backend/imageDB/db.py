import pymysql.cursors
import atexit
from datetime import datetime

"""
Interaction with ImageDB database.
Login/initialize via ImageDB (imageDB.py).  
Always use ImageDB to add and delete images for consistency between database and files.
All other methods can be used directly by referencing ImageDB.db
"""

timestamp=datetime.today()
print(timestamp)

#Everything relating to permissions is not implemented
class DB(object):

	connected=False
	
	def connect(self, host, user_type, db_name, user_name, password):
		self.connection=pymysql.connect( 
			host=host,
			user=user_type,
			password=password,
			db=db_name,
			cursorclass=pymysql.cursors.DictCursor
		)
		
		self.cursor=self.connection.cursor()	
		self.user_id=self.getUserID(user_name) #Getting user id based on user name input
		if self.user_id is None:				#If the user doesn't exist, then the user is created
			self.newUser(user_name)
		self.user_id=self.getUserID(user_name)	
		self.dataset_ids=self.listDatasets()	#Listing data sets as a dictionary of the form {dataset_path: dataset_id}
		#self.permissions=self.listPermissions(self.user_id) #Getting the datsets that the user is allowed to edit.
		self.connected=True

	def query(self, sql, values=None):
	#General purpose query function.
	#Useful if you know how to write sql queries
		if values is None:
			self.cursor.execute(sql)
		else:
			self.cursor.execute(sql, values)
		self.connection.commit()
		return self.cursor.fetchall()

	def listDatasets(self):
	#building the paths of all datasets for later reference.
		sql="SELECT * FROM datasets ORDER BY id"
		dataset_rows=self.query(sql)
		dataset_ids={}
		for row in dataset_rows:
			path=row['name']
			dataset_ids[path]=row['id']
		return dataset_ids
		
	def getUserID(self, user_name):
		sql="SELECT id FROM users WHERE user_name LIKE '"+user_name+"'"
		row=self.query(sql)
		if not row:
			return None
		return row[0]['id']
		
	def newUser(self, user_name):
		sql="INSERT INTO users (user_name) VALUES (%s)"
		self.query(sql, values=(user_name))
		
	"""def listPermissions(user_id):
		sql="SELECT dataset_id FROM permissions WHERE user_id==%s"
		rows=self.query(sql, values=(user_id))
		return list(rows.values())"""
		
#------------INSERTION METHODS------------	
	def insertDatasetRow(self, name):
		sql="INSERT IGNORE datasets (name, user_id) VALUES (%s, %s)"
		self.query(sql, (name, self.user_id))
		self.dataset_ids=self.listDatasets()
		
	def insertImageRow(self, dataset_name, imagehash, url=None, source=None, x_resolution=None, y_resolution=None, date_taken=None, gps=None, notes=None):
		#Do not use without adding image to file system. There is no automatic check on this that is implemented yet.
		dataset_id=self.dataset_ids[dataset_name]
		"""if dataset_id not  in self.permissions:
			print("User is not allowed to modify this dataset")
			return """
		sql="INSERT IGNORE INTO images (dataset_id, imagehash, url, source, x_resolution, y_resolution, date_taken, gps, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		if gps:
			gps=string(gps)
		self.query(sql, values=(dataset_id, str(imagehash), url, source, x_resolution, y_resolution, date_taken, gps, notes))
	
	def insertDataset(self, dataset_name, image_rows, parent_dataset='master'):
	#Insert a set of images into the database.  This is an alternative to insertDatasetRow() and insertImageRow
		num_rows=len(image_rows)
		insertDatasetRow(dataset_path, master=parent_dataset, num_images=num_rows)
		for row in image_rows:
			insertImageRow(dataset_path, row['imagehash'], url=row.get('url'), source=row.get('source'), x_resolution=row.get('x_resolution'), y_resolution=row.get('y_resolution'), date_taken=row.get('date_taken'), gps=row.get('gps'), notes=row.get('notes'))
			
	def newTag(self, tag_string, tag_type=None):
		#Create a new tag
		sql="INSERT IGNORE INTO tags (tag, tag_type) VALUES (%s, %s)"
		self.query(sql, values=(tag_string, tag_type))
		
	def insertTagLink(self, tag_id, image_id, tag_data=None, notes=None):
		#Link a tag to an image
		"""sql="SELECT dataset_id from images WHERE id=%s"
		dataset_id=self.query(sql, values=(image_id))[0]['dataset_id']
		if dataset_id not  in self.permissions:
			print("User is not allowed to modify this dataset")"""
		sql="REPLACE INTO tag_links (tag_id, image_id, user_id, tag_data, notes) VALUES (%s, %s, %s, %s, %s)"
		self.query(sql, values=(tag_id, image_id, self.user_id, tag_data, notes))
#------------END INSERTION METHODS------------

#------------DELETION METHODS--------------

	def removeImage_byID(self, image_id):
		#Do not use this without removing from file system.  No automatic check enforced.
		sql="DELETE FROM tag_links WHERE image_id=%s"
		self.query(sql, values=(image_id))
		sql="DELETE FROM images WHERE id=%s"
		return self.query(sql, values=(image_id))
		
	def removeTagLink(self, image_id=None, tag_id=None, user_id=None):
		#NOTE: If a user_id is not specified then all tag_links for the image-tag combination will be removed. 
		#Likewise, if only a user_id is specified, then all tag_links for a specific user will be removed
		values=[]
		clause=" WHERE"
		sql="DELETE FROM tag_links"
		flag=True
		if image_id is not None:
			sql=sql+clause+" image_id=%s"
			values.append(image_id)
			clause=" AND"
			flag=False
		if tag_id is not None:
			sql=sql+clause+" tag_id=%s"
			values.append(tag_id)
			clause=" AND"
			flag=False
		if user_id is not None:
			sql=sql+clause+" user_id=%s"
			values.append(user_id)
			flag=False
		value_tup=tuple(values)
		if not flag:
			self.query(sql, values=value_tup)
			
	def removeImage_byAttr(self, numeric_attributes, string_attributes):
		#Non-specific, unoptimized image deletion based on attributes
		#Attributes should be of the form {'attribute': value, ...etc} 
		#where 'attribute' corresponds to a column attribute in table 'images'
		clause=" WHERE"
		sql="DELETE FROM images" 
		flag=True
		values=[]
		for attribute in numeric_attributes.keys():
			values.append(numeric_attributes[attribute])
			sql=sql+clause+" "+attribute+"=%s"
			clause=" AND"
			flag=False		
		for attribute in string_attributes.keys():
			values.append(string_attributes[attribute])
			sql=sql+clause+" "+attribute+" LIKE %s"
			clause=" AND"
			flag=False
		if not flag:
			value_tup=tuple(values)
			self.query(sql, values=value_tup)		
			
#------------END DELETION METHODS----------

#------------SELECTION METHODS------------
	def selectDataset(self, dataset_name):
		dataset_id=self.dataset_ids[dataset_name]
		sql="SELECT * FROM images WHERE dataset_id=%s ORDER BY date_taken"
		return self.query(sql, values=(dataset_id))
	
	def selectImage_byID(self, image_id):
		sql="SELECT * FROM images WHERE id=%s"
		return self.query(sql, values=(image_id))

	def selectImage_byAttr(self, numeric_attributes, string_attributes):
		#Non-specific, unoptimized image deletion based on attributes
		#Attributes should be of the form {'attribute': value, ...etc} 
		#where 'attribute' corresponds to a column attribute in table 'images'
		clause=" WHERE"
		sql="SELECT * FROM images" 
		flag=True
		values=[]
		for attribute in numeric_attributes.keys():
			values.append(numeric_attributes[attribute])
			sql=sql+clause+" "+attribute+"=%s"
			clause=" AND"
			flag=False		
		for attribute in string_attributes.keys():
			values.append(string_attributes[attribute])
			sql=sql+clause+" "+attribute+" LIKE %s"
			clause=" AND"
			flag=False
		if not flag:
			value_tup=tuple(values)
			return self.query(sql, values=value_tup)

		
	def selectWithTag(self, tag_name):
		#Select all images with given tag (in tag_links)
		tag_id=self.getTagID(tag_name)
		sql="SELECT * FROM images INNER JOIN tag_links ON image_id=images.id where tag_id=%s"
		return self.query(sql, values=(tag_id))
			
	def selectUntagged(self, dataset_name=None, tag_name=None, user_name=None):
		select="SELECT * FROM images LEFT JOIN tag_links"
		on=" ON images.id=tag_links.image_id"
		where=" WHERE tag_links.tag_id IS NULL"
		values=[]
		if tag_name:
			tag_id=self.getTagID(tag_name)
			on=on+" AND tag_links.tag_id=%s"
			values.append(tag_id)
		if dataset_name is not None:
			where=where+" AND images.dataset_id=%s"
			values.append(self.dataset_ids[dataset_name])
		if user_name is not None:
			user_id=self.getUserID(user_name)
			on=on+" AND tag_links.user_id=%s"
			values.append(user_id)
		value_tup=tuple(values)
		sql=select+on+where
		return self.query(sql, values=value_tup)
		
	def hasImage(self, image_hash, date_taken):
		#Checks to see if an image is already in the database
		sql="SELECT id FROM images WHERE imagehash=%s and date_taken=%s"
		return self.query(sql, values=(str(image_hash), date_taken))
		
	def getLastID(self):
		sql="SELECT LAST_INSERT_ID()"
		return self.query(sql)[0]['LAST_INSERT_ID()']
		
	def getTagID(self, tag_name):
		sql="SELECT id FROM tags WHERE tag LIKE %s"
		return self.query(sql, values=(tag_name))[0]['id']
#------------END SELECTION METHODS------------
	

	

	
	


