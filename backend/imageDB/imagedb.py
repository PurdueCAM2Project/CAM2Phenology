import db
import images
from PIL import Image
import imagehash
import json

def newDataset(name, master=None, num_images=0):
	db.insertDatasetRow(name, master=master, num_images=num_images)
	
def addImage(image_path, dataset_name, image_dict):
	image_dict['dataset_name']=dataset_name
	im=Image.open(image_path)
	image_hash=imagehash.average_hash(im)
	image_dict['imagehash']=image_hash
	db.insertImageRow(**image_dict)
	images.addJpeg(im, db.getLastID())
	
def tagImage(image_id, tag_name, tag_data={}):
	tag_id=db.getTagID(tag_name)
	json_string=None
	if tag_data:
		json_string=json.dumps(tag_data)
	db.insertTrainingTag(tag_id, image_id, tag_data=json_string) 
	
class  Dataset():
	#singly linked list

	def __init__(self, dataset_name):
		self.rows=db.selectDataset(dataset_name)
		self.current_image=()
		
	def getNext(self):
		if self.rows:
			row=self.rows.pop()
			pil_image=images.getJpeg(row['id'])
			self.current_image=(pil_image, row)
			return self.current_image
		return 0
	
	def tag(self, tag_name, tag_data={}):
		image_id=self.current_image[1]['id']
		tagImage(image_id, tag_name)
		
	def hasNext(self):
		return self.rows
	
	
	

	