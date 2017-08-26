import sys
import math
import os
import os.path
import json
sys.path.insert(0, '/mnt/d/PhenologyGit/backend/utility')
from PIL import Image
import imagehash
import data
import atexit




	
class ImageStorage():

	id=0
	depth=0
	
	def __init__(self, num_images=1000000):
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
				data={'download requests': [], 'serviced requests': []}
				json.dump(data, file)
			file.close()

		atexit.register(self.exitHandler)

	def buildFileTree(self, num_images):
		print ("Building file tree to support "+str(num_images)+" images...")
		num_leaves=num_images//1000
		self.depth=int(math.log(num_leaves, 10))
		i=0
		for i in range(0, num_leaves):
			path='images/'
			num=i
			j=0
			while j<self.depth:
				path=path+str(num%10)+'/'
				num=num//10
				j=j+1
				os.makedirs(path, exist_ok=True)
		print ("Tree Built")
		
	def downloadRequest(self, url, image_dict={}):
	#make a download request.
	#This method records the request and returns the id that can be used to access stored image (important)
		self.id=self.id+1
		with open('requests.json') as file:
			data=json.load(file)
			download_requests=data['download requests']
			download_requests.append({'url': url, 'image info': image_dict, 'storage id': self.id})
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
			for request in data['download requests']:
				self.downloadStore(request['url'], request['image info'], request['storage id'])
			data['serviced requests'].extend(data['download requests'])
			del data['download requests'][:]
		file.close()
		with open('requests.json', 'w+') as file:
			json.dump(data, file)
		file.close()
		
				
	def downloadStore(self, url, image_dict, id):
	#download and store images
	#TODO: create exif process to attach exif data in <image_dict>
		import urllib.request
		import shutil
		from urllib.error import URLError, HTTPError
		i=0
		path=self.buildPath(id)
		print(path)
		while i<5:
			#print(id)
			#print(url)
			i=i+1
			try:
				urllib.request.urlretrieve(url, path+'.jpg')
			except URLError as e:
				print('Url Error')
			except HTTPError as e:
				print('HTTP Error')
			else:
				return
		#if it fails:
		print ('FAILED DOWNLOAD: '+image_dict)
		return 'failed'
		
	def buildPath(self, num):
		hash_num=num
		path='images/'
		i=0
		for i in range(0, self.depth):
			path=path+str(num%10)+'/'
			hash_num=hash_num//10
		return path+str(num)

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

	

		

		



	