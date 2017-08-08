import sys
import math
import os
import os.path
import json
import datetime
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
from PIL import Image
import imagehash
import dbManager
import data
#import data

	

class ImageStorage():

	id=0
	depth=0
	
	def __init__(self, num_images=1000000):
		import atexit
		self.request_functions={'download': self.downloadStore, 'detect horizon': self.horizonDetect}
		if os.path.isfile('ids.txt'):
			with open('ids.txt', 'r') as file:
				lines=file.readlines()
				self.id=int(lines[0])
				self.depth=int(lines[1])
			file.close()
		else:
			self.buildFileTree(num_images)
		if not os.path.isfile('requests.json'):
			print('making file')
			with open('requests.json', 'w+') as file:
				data={'requests': [], 'serviced requests': []}
				json.dump(data, file)
			file.close()
		atexit.register(self.exitHandler)
		
	#building a directory structure to hold 1000 images in a single folder, with 10 sub-directories per directory
	#This is to be used with mod 10 hashing to build paths
	def buildFileTree(self, num_images):
		print ("Building file tree to support "+str(num_images)+" images...")
		num_leaves=num_images//1000
		self.depth=int(math.log(num_leaves, 10))
		i=0
		for i in range(0, num_leaves):
			path='Images/'
			num=i
			j=0
			while j<self.depth:
				path=path+str(num%10)+'/'
				num=num//10
				j=j+1
				os.makedirs(path, exist_ok=True)
		print ("Tree Built")
		
		
	#make a request.	
	def makeRequest(self, image_dict, request):
	#image_dict contains all necessarry parameters for request as well as any image metadata
	#Request is the string dictionary key of request_functions
	#This method will return the image id used to access the result of the request.
		self.id=self.id+1
		print(self.id)
		with open('requests.json') as file:
			data=json.load(file)
			requests=data['requests']
			dict_string=str(image_dict)
			requests.append({'request': request, 'image info': dict_string, 'storage id': self.id})
		file.close()
		with open('requests.json', 'w+') as file:
			json.dump(data, file)
		file.close()
		return self.id
		
	def serviceRequests(self):
	#carrying out requests stored in 'requests.json'.
	#Only download requests implemented at this point
		with open('requests.json') as file:
			data=json.load(file)
			
			for request in data['requests']:
				self.request_functions[request['request']](eval(request['image info']), request['storage id'])
			data['serviced requests'].extend(data['requests'])
			del data['requests'][:]
		file.close()
		with open('requests.json', 'w+') as file:
			json.dump(data, file)
		file.close()
		
				
	def downloadStore(self, image_dict, id):
	#download and store an image sourced from <d_url>.  Stored based on the value of <id>
	#TODO: create exif process to attach exif data in <image_dict>	
		import urllib.request
		from urllib.error import URLError, HTTPError
		d_url=image_dict['url']
		i=0
		path=self.buildPath(id)
		print(path)
		while i<5:
			#print(id)
			#print(url)
			i=i+1
			try:
				urllib.request.urlretrieve(d_url, path)
			except URLError as e:
				print('Url Error')
			except HTTPError as e:
				print('HTTP Error')
			else: #if image doesn't exist -> add image to storage database
				im=Image.open(path)
				image_hash=imagehash.average_hash(im)
				print(image_hash)
				im.close()
				if dbManager.isImageStored(image_hash): #detecting duplicate image
					duplicate_id=dbManager.idFromHash(image_hash)
					print("Image duplicate detected. Storage cancelled.\nReturning duplicate's id: "+str(duplicate_id))
					os.remove(path)
					return
				else:
					dbManager.insertStoredImage(id, image_hash, url=d_url)
					#data.initialImage(image_dict, path+'.jpg') <this isnt formatted well enough to implement yet
					return
		#if it fails:
		print ('FAILED DOWNLOAD: '+image_dict)
		return 0
		
	def getImage(self, id):
	#returning PIL image
		path=self.buildPath(id)
		return Image.open(path)
		
	def horizonDetect(self, image_dict, id):
		import horizonDetection
		from horizonDetection import findHorizon
		path=self.buildPath(image_dict['alt_id'])
		new_path=self.buildPath(id)
		findHorizon(path, new_path)
		
		
	#hashing the (integer) value of <num> to return a path 
	def buildPath(self, num):
		hash_num=num
		path='Images/'
		i=0
		for i in range(0, self.depth):
			path=path+str(num%10)+'/'
			hash_num=hash_num//10
		return path+str(num)+'.jpg'
		
	#When sys.exit() the value of the next id to be given out is stored
	def exitHandler(self):
		with open('ids.txt', 'w+') as file:
			file.write(str(self.id)+"\n")
			file.write(str(self.depth)+"\n")
		file.close()
		
		
		
		
			
	"""def addImage(self, path=''):
		im=Image.open(path+'temp.jpg')
		path=self.buildPath(self.id)
		save_id=self.id+100000000000
		path=path+str(save_id)+'.jpg'
		im.save(path)
		self.id=self.id+1
		return save_id  """

	

		

		



	