import os.path
from os.path import *
import data
from multiprocessing import Process


"""class Source:

	def getImage(index):
	def search(paramaters):
	def clear():
	def save(location):
"""

class WebSearch():

	"""TODO: initialize with types of web searches as an array of strings. 
	Right now this is not necessarry as flickr is the only source.
 
	def __init__(self, apis):
		self.web_sources=[]
		for api in apis:
			self.web_sources.append(eval(api))"""


	def __init__(self):
		import flickrSearch
		self.directory='data/temp/'
		self.ids=[]
		self.api=flickrSearch
		self.total=0
		p1=Process
		p2=Process
		p3=Process
		p4=Process
		print(os.listdir(self.directory))
		self.checked=0
	def loadImages(self, starting_index, ending_index, dir, pID):
		i=starting_index
		global checked
		j=0
		t=len(self.ids)//4
		while(i<ending_index):
			i=i+1
			if not os.path.isfile(dir+self.ids[i]+'.jpg'):
				image_dict=self.api.getImageTup(self.ids[i], dir)
				self.checked=self.checked+1
				if image_dict is not None:
					#print(tup[1])
					data.initialImage(image_dict, dir)

		print('checked, PID: '+str(pID))
	
	def search(self, types, parameters):
		self.ids=self.api.search(types, parameters)
	"""	interval=len(self.ids)//4
		interval=interval-1
		p1=Process(target=self.loadImages, args=(0, 10, self.directory))
		p1.start()
		self.p2=Process(target=self.loadImages, args=(interval, interval+10, self.directory,))
		self.p2.start()
		self.p3=Process(target=self.loadImages, args=(interval*2, interval*2+10, self.directory,))
		self.p3.start()
		self.p4=Process(target=self.loadImages, args=(interval*3, interval*3+10, self.directory,))
		self.p4.start()"""

	def saveAll(self, location):
		import shutil
		import time
		import os
		interval=len(self.ids)//100
		total=len(self.ids)
		p1=Process()
		p2=Process()
		p3=Process()
		p4=Process()
		
		
		"""p1.terminate()
		self.p2.terminate()
		self.p3.terminate()
		self.p4.terminate()"""
		index=0
		while(index<total):

			if not p1.is_alive():
				p1=Process(target=self.loadImages, args=(index, index+interval, location, 1,))
				p1.start()
				index=index+interval
				print("downloaded "+str(index)+"/"+str(total))

			elif not p2.is_alive():
				p2=Process(target=self.loadImages, args=(index, index+interval, location, 2,))
				p2.start()
				index=index+interval
				print("downloaded "+str(index)+"/"+str(total))

			elif not p3.is_alive():
				p3=Process(target=self.loadImages, args=(index, index+interval, location, 3,))
				p3.start()
				index=index+interval
				print("downloaded "+str(index)+"/"+str(total))

			elif not p4.is_alive():
				p4=Process(target=self.loadImages, args=(index, index+interval, location, 4,))
				p4.start()
				index=index+interval
				print("downloaded "+str(index)+"/"+str(total))

		print('SUCCESSFULLY DOWNLOADED ALL IMAGES')


	def getImage(self, index):
		print('test2')
		index=index%self.total	
		return data.getImage(self.directory+self.images[index])
	def getEXIF(self, index):
		index=index%self.total
		return data.getEXIF(self.directory+self.images[index])

#class used to access data stored locally in ntfs file format
class LocalStorage(object):
	
	#class is initialized with a directory
	def __init__(self, directory):
		self.directory=directory
		self.images=os.listdir(directory)
		self.total=len(self.images)

	#returns the image with PIL accessed by respective index
	def getImage(self, index):
		index=index%self.total
		if index<self.total:
			return data.getImage(self.directory+self.images[index])

	def getImageByID(self, id):
		if id in self.images:
			return data.getImage(self.directory+id)

	#returns EXIF by index
	def getEXIF(self, index):
		index=index%self.total
		if index<self.total:
			#print(str(self.images[index]))
			return data.getEXIF(self.directory+self.images[index])

	def getEXIFByID(self, id):
		if id in self.images:
			return data.getEXIF(self.directory+id)

	#returning the ids of all photos in a geographical circle
	def getInRange(self, lat, long, radius):
		from analysis import calcDistance
		circled_images=[]
		for image in self.images:
			location=data.getGPS(data.getEXIF(self.directory+image))
			dist=calcDistance(location, (lat, long))
			if dist<radius:
				circled_images.append(image)
		return circled_images

	def copyImage(self, id, dest):
		from shutil import copyfile
		copyfile(self.directory+id, dest)

	def hasImage(self, id):
		return directory+id in self.images

	def removeImage_byID(self, id):
		os.remove(self.directory+id)
		self.images.remove(id)

	def removeImage_byIndex(self, index):
		os.remove(self.directory+self.images[index])
		self.images.pop(index)

	def removeAll(self):
		del self.images[:]
		os.rmdir(self.directory)

	#using horizon detection module
	#saves image as gray_image.jpg
	def horizonDetect(self, index):
		import horizonDetection
		from horizonDetection import findHorizon
		findHorizon(self.directory+self.images[index])

def makeLocalStorage(directory):
	source=LocalStorage(directory)
	return source
#defaultStorage=makeLocalStorage('/mnt/d/data/Phenology/packages/CCLargeGeo/')
