import db
import images
from images import SFTP
from PIL import Image
import imagehash
import json
from db import DB

"""
High level interaction with image tagging database (ImageDB).
DB() from db.py is the class used to interact with the database (currently hosted on '128.46.213.21')
SFTP() from images.py is the class used to interact with the file structure of images via sftp on '128.46.213.21'.
Base functionality has been implemented.  
Many functions have not been brought to this level (see db.py)
In progress.

-Ehren Marschall 10/26/2017
"""


login_info="host: 128.46.213.21, user_type: cam2team,  db_name: ImageDB, user_name: test user1"  #meaningless string. ignore.
		
class ImageDB():
	
	"""
	Connect to database and sftp server.
	Password is required.
	Please use your own user name (will be created if it does not exist).
	For all testing use 'ImageDBTest'.  This database will be reinitialized occassionally
	For reliable code, use 'ImageDB' where data will remain more permanently.
	Variables 'self.db' and 'self.server' can be referenced directly.
	"""

	def __init__(self, user_name, password, host='128.46.213.21', user_type='cam2team',  db_name='ImageDBTest'):
		self.db=DB()
		self.server=SFTP()
		#Connecting to database.  Essential function
		self.server.connect(password, file_tree=db_name+'/')
		self.db.connect(host, user_type, db_name, user_name, password)
		
	def newDataset(self, name, num_images=0):
		#Create a new dataset
		#Every image must reference a dataset
		self.db.insertDatasetRow(name)
		
	def addImage(self, image_path, dataset_name='test', image_dict={}):
		#Add image metadata to database and image to file system
		image_dict['dataset_name']=dataset_name
		im=Image.open(image_path)
		image_hash=imagehash.average_hash(im)
		date_taken=None
		if('date_taken' in image_dict.keys()):
			date_taken=image_dict['date_taken']
		#print(str(image_hash))
		if(self.db.hasImage(image_hash, date_taken)):
			print("Image already exists in database")
			return 
		x_resolution, y_resolution=im.size
		image_dict['x_resolution']=x_resolution
		image_dict['y_resolution']=y_resolution
		image_dict['imagehash']=image_hash
		self.db.insertImageRow(**image_dict)
		last_id=self.db.getLastID()
		self.server.addJpeg(image_path, last_id)
		return last_id
		
	def removeImage(self, id):
		self.db.removeImage_byID(id)
		self.server.removeJpeg(id)
		   
	def tagImage(self, image_id, tag_name, tag_data={}):
		#Insert a tag link into database
		tag_id=self.db.getTagID(tag_name)
		if tag_id is None:
			self.db.newTag(tag_name)
		tag_id=self.db.getTagID(tag_name)
		json_string=None
		if tag_data:
			json_string=json.dumps(tag_data)
		self.db.insertTagLink(tag_id, image_id, tag_data=json_string) 
	
	def getDataset(self, dataset_name):
		return Dataset(self.db, self.server, dataset_name=dataset_name)
		
	def getImage(self, id):
		#returns PIL image
		return self.server.getJpeg(id)
		
		
		
class  Dataset():
	"""Psuedo data structure.  Loads data specified by the dataset name.
	This class is an abstraction to simplify functionality.
	Can be used to quickly retrieve and tag images.
	The easiest way to initialize is to use the 'getDataset' function in ImageDB class above"""
	
	def __init__(self, db, server, dataset_name=None):
		self.db=db
		self.server=server
		if dataset_name is not None: #alternatively call 'loadUntagged' after initializing 
			self.rows=self.db.selectDataset(dataset_name)
		self.current_image=()
		
	def loadUntagged(self, parameters={}):
		#Loading untagged images fitting <parameters>.  See db.py for parameter options
		#if parameters is not passed, then all untagged images will be loaded
		self.rows=self.db.selectUntagged(**parameters)
		
	def getNext(self):
		#Psuedo singly linked list style.  This will remove an image from the list and return its data.
		if self.rows:
			row=self.rows.pop()
			pil_image=self.server.getJpeg(row['id'])
			self.current_image=(pil_image, row)
			return self.current_image
		return 0
		
	def tag(self, tag_name, tag_data={}):
		#Tag self.current_image
		#This code is copied verbatim from ImageDB
		tag_id=self.db.getTagID(tag_name)
		image_id=self.current_image[1]['id']
		if tag_id is None:
			self.db.newTag(tag_name)
		tag_id=self.db.getTagID(tag_name)
		json_string=None
		if tag_data:
			json_string=json.dumps(tag_data)
		self.db.insertTagLink(tag_id, image_id, tag_data=json_string) 
	
	def hasNext(self):
		return self.rows

	
	

	