#Global Phenology: Ehren Marschall updated 3/11/17
#Helper methods for exif manipulation
import json
import htmlParser
import urllib.request
from PIL import Image
import os.path
from os.path import *

def initialImage(dict, location, im):
	import piexif	
	import datetime
	from datetime import datetime

	im.save(location)

	exif_dict=piexif.load(location)
	exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]=dict['DateTaken']
	exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]=str(datetime.today())
	exif_dict['Exif'][piexif.ExifIFD.ImageUniqueID]=dict['ImageID']
	exif_dict['Exif'][piexif.ExifIFD.UserComment]=str(dict)
	exif_bytes=piexif.dump(exif_dict)
	piexif.insert(exif_bytes, location)

#inserts rating into exif data
def insertRating(dict, location):
	import piexif
	import datetime
	from datetime import datetime
	
	exif_dict=piexif.load(location)
	exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]=str(datetime.today())
	rateDict=eval(exif_dict['Exif'][piexif.ExifIFD.UserComment])
	rateDict['Rating']=dict['Rating']
	rateDict['Quality']=dict['Quality']
	rateDict['Scene']=dict['Scene']
	rateDict['Coverage']=dict['Coverage']
	rateDict['Scale']=dict['Scale']
	exif_dict['Exif'][piexif.ExifIFD.UserComment]=str(rateDict)
	exif_bytes=piexif.dump(exif_dict)
	piexif.insert(exif_bytes, location)



#not currently used or functional
def downloadImage(url, id, date, searchUrl):
	urllib.request.urlretrieve(url, 'temp.jpg')
	im=Image.open('temp.jpg')
	if not os.path.exists('downloads/'):
		os.makedirs('downloads/')
	if not os.path.isfile('downloads/'+imName):
		im.save('downloads/'+imName)
	
#Class used to store Photo data and rating data in a particular search or searches.  
#All photos at this point will have a date taken as specified in search.py
#All photos will have info re-accessible online through their flickr id
#Search packages are stored in json format and are then able to be opened and rated
#The images will be stored in the same folder with all pertinent exif data stored with above helper methods		
class searchPackage:
	import datetime
	photos=[]
	data={}
	path=''
	overallRating=0
	packageName=''
	imageIndex=0
	#add new image to package
	def add(self, image, imageDict):
		imageDict['Rating']=-1 
		location=self.path+imageDict['ImageID']+'.jpg'
		if not os.path.isfile(location):	
			initialImage(imageDict, location, image)
			self.photos.append(imageDict)
			self.data['Total']=self.data['Total']+1
			  
		else:
			print('photo already exists')
	def create(self, name, searchUrl, dir): #used to create a new package named: <name> of length <tphoto>, with dict of search urls, and array of image dictionaries 
		from datetime import datetime
		dateCreated=str(datetime.today())
		self.data={'Name': name, 'Url': searchUrl, 'Total': 0, 'Overall Rating': 0, 'Rated': 0,'Date Created': dateCreated, 'Photos': self.photos}  #dictionary that contains basic info. 
		self.packageName=name
		self.path=dir+name+'/'  #all photos stored in packages(or another dir)/<packagename>   Text file containing info is <packagename>.json in the same folder 
		self.packageName=name
		if not os.path.exists(self.path):
			os.makedirs(self.path)
	
	#open pre made package (import)
	def open(self, name, dir):
		self.packageName=name
		self.path=dir+name+'/'
		print (name)
		if os.path.exists(self.path):
			with open(self.path+name+'.json') as file:
				self.data=json.load(file)
				self.photos=self.data['Photos']
			file.close()
			self.packageName=name
			print (self.data['Name'])

	def getImage(self, i): #used in searchDisplay
			if(i==0):
				self.imageIndex=0
				for photo in self.data['Photos']:
					if photo['Rating']!=-1:
						self.imageIndex=self.imageIndex+1
			else:
				self.imageIndex=self.imageIndex+i
			self.imageIndex=self.imageIndex%self.data['Total']
			im=Image.open(self.path+self.data['Photos'][self.imageIndex]['ImageID']+'.jpg')
			tup=(im, self.data['Photos'][self.imageIndex])
			return tup
	"""	def stream(buffer, num):
		i=0
		while (i<num):
			buffer.append(self.getImage(i))
			i=i+1			
	"""
	def rate(self, qual, scen, scal, cover):   #rating method for individual photos.  Quality, scene, scale, coverage.(IntVar variables)    All 1-3 scale.  Rating is addition of these values
		r=qual+scen+scal+cover
		tempData=self.data['Photos'][self.imageIndex]
		print (tempData['Rating'])
		temp=tempData['Rating']
		if temp<0:
			temp=0			
		self.data['Overall Rating']=self.data['Overall Rating']*self.data['Rated']-temp
		if tempData['Rating']==-1:
			self.data['Rated']=self.data['Rated']+1
		tempData['Rating']=r
		tempData['Coverage']=cover
		tempData['Scene']=scen
		tempData['Scale']=scal
		tempData['Quality']=qual
		insertRating(tempData, self.path+tempData['ImageID']+'.jpg')
		self.data['Overall Rating']=(self.data['Overall Rating']+r)/self.data['Rated']
		self.data['Photos'][self.imageIndex]=tempData.copy()
					
	def writedata(self):  #<save>='
		with open(self.path+self.packageName+'.json', "w+") as file:  
    			json.dump(self.data, file)
		file.close()
	
	def getUrl(self):
		return self.data['Url']

	def getImages(r1, r2): #return a list of images of specified length
		i=0
		imList=[]
		i=r1
		while i<r2 and i<len(self.photos):
			im=Image.open(self.path+self.photos[i]['ImageID'])
			tup=(im, self.photos[i])
			imList.append(tup)
			i=i+1
		return imList

#Used to update outdated formats.  Do not call			
	def update(self): 
		from search import getGeo
		list=[]
		for photo in self.data['Photos']:
			photo['gps']=getGeo(photo['ImageID'])
		self.writedata()					

