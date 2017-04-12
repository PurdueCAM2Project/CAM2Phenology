import os.path
from os.path import *
import data


"""class Source:

	def getImage(index):
	def search(paramaters):
	def clear():
	def save(location):
"""
class LocalStorage(object):

	def __init__(self, directory):
		self.directory=directory
		self.images=os.listdir(directory)
		self.total=len(self.images)

	def getImage(self, index):
		index=index%self.total
		if index<self.total:
			return data.getImage(self.directory+self.images[index])

	def getEXIF(self, index):
		index=index%self.total
		if index<self.total:
			return data.getEXIF(self.directory+self.images[index])


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


def makeLocalStorage(directory):
	source=LocalStorage(directory)
	return source
defaultStorage=makeLocalStorage('/mnt/d/data/Phenology/packages/CCLargeGeo/')
