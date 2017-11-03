from PIL import Image
import math
import os
import pysftp
import atexit

depth=5
"""
Script used to interact with file system on sftp server hosted on '128.46.213.21'
References image by hashing its id into a file path.
The id is hashed using mod 10.  (buildFilePath(id))
This is a scalable solution to storing massive amounts of images.  
Performance will slowly decrease with scale.

Leaf folders can reasonably hold 100000 images (possibly more).  \
This is because we never have to list the directory.
However, the amount of images in a given folder should be kept as low as possible.

File structure format: 	
		root folder->
			folders: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9->
												0, 1, 2, 3, 4, 5, 6, 7, 8, 9->
																			leaves: 0, 1, 2, 3, 4, 5, 6, 7, 8, leaf folder 9-> 999.jpg, 9999.jpg, etc.jpg
"""
def buildFileTree(num_images, srv):
#THIS IS A RISKY FUNCTION! BE CARFUL IF YOU MUST RUN IT.
#building a file tree to hold <num_images> images on the sftp server
#DO NOT RUN THIS FUNCTION WITH SRV
#Replace srv with 'os' to set up locally
	print ("Building file tree to support "+str(num_images)+" images...")
	num_leaves=num_images//100000
	global depth
	depth=int(math.log(num_leaves, 10))
	i=0
	for i in range(0, num_leaves):
		path='images/'
		num=i
		j=0
		while j<depth:
			path=path+str(num%10)+'/'
			num=num//10
			j=j+1
			srv.makedirs(path)
	print ("Tree Built")

#hashing integer <num> value into a file path	
def buildPath(num):
	hash_num=num
	path=""
	i=0
	for i in range(0, depth):
		path=path+str(num%10)+'/'
		hash_num=hash_num//10
	return path	

class SFTP():
	#Using python library pysftp to manipulate sftp server

	def connect( self, pswd, hostname='128.46.213.21', file_tree='ImageDBTest/', username='cam2team'):
		self.file_tree=file_tree
		self.srv=pysftp.Connection(hostname, username, password=pswd)
		atexit.register(self.srv.close)
		
	def addJpeg(self, local_path, id):
		path=self.file_tree+buildPath(id)
		if not (self.srv.isdir(path)):
			self.srv.makedirs(path)
		self.srv.put(local_path, path+str(id)+'.jpg')
		#print(path)
		
	def getJpeg(self, id, new_path='serverImage.jpg'):
		path=self.file_tree+buildPath(id)
		self.srv.get(path+str(id)+'.jpg', new_path)
		im=Image.open(new_path)
		return im
		
	def removeJpeg(self, id):
		path=self.file_tree+buildPath(id)+str(id)+'.jpg'
		if self.srv.isfile(path):
			self.srv.remove(path)
		else:
			print("File does not exist.")

		