#Global Phenology: Ehren Marschall updated 3/7/17
#Helper methods for exif manipulation
import json
import htmlParser
import urllib.request
from PIL import Image
import os.path
from os.path import *

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

#puts initial exif data into photos	
def initialExif(dict, location):
	import piexif
	import datetime
	from datetime import datetime
	exif_dict=piexif.load(location)
	exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]=dict['DateTaken']
	exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]=str(datetime.today())
	exif_dict['Exif'][piexif.ExifIFD.ImageUniqueID]=dict['ImageID']
	exif_dict['Exif'][piexif.ExifIFD.UserComment]=str(dict)
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
	dir='packages/'
	overallRating=0
	packageName=''
#add new image to package
	def add(self, imgDict):
		urllib.request.urlretrieve(imgDict['Url'], 'temp.jpg')
		im=Image.open('temp.jpg')
		imgDict['Rating']=-1 
		location=self.path+imgDict['ImageID']+'.jpg'
		if not os.path.isfile(location):
			im.save(location)  #actual image passed from phen image.  This is essentially the phenImage class's only purpose at this point
			initialExif(imgDict, location)
			print('success')
			self.photos.append(imgDict)  
		else:
			print('photo already exists')
	def create(self, name, tphotos, searchUrl, images): #used to create a new package named: <name> of length <tphoto>, with dict of search urls, and array of image dictionaries 
		from datetime import datetime
		dateCreated=str(datetime.today())
		self.data={'Name': name, 'Total': tphotos, 'Url': searchUrl, 'Overall Rating': 0, 'Rated': 0,'Date Created': dateCreated, 'Photos': self.photos}  #dictionary that contains basic info. 
		self.packageName=name    												#photos is a dict of photo info updated after rating
		self.path=self.dir+name+'/'  #all photos stored in packages(or another dir)/<packagename>   Text file containing info is <packagename>.json in the same folder 
		
		self.packageName=name
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		with open(self.path+name+'.json', 'w+') as file:
			i=0
			while (i<tphotos): 
				print(self.photos)
				imgDict=images[i].copy()
				self.add(images[i])
				print('add')
				i=i+1
			json.dump(self.data, file)		
		file.close()
	
#open pre made package (import)
	def open(self, name):
		self.packageName=name
		self.path=self.dir+name+'/'
		print (name)
		if os.path.exists(self.path):
			with open(self.path+name+'.json') as file:
				self.data=json.load(file)
				self.photos=self.data['Photos']
			file.close()
			self.packageName=name
			print (self.data['Name'])
		else: 
			print('oh')
	def getImagePath(self, i): #used in searchDisplay
			t=self.data["Total"]
			index=i%t
			return self.path+self.data['Photos'][index]['ImageID']+'.jpg'			
		
	def rate(self, qual, scen, scal, cover, index):   #rating method for individual photos.  Quality, scene, scale, coverage.(IntVar variables)    All 1-3 scale.  Rating is addition of these values
		realIndex=index%self.data['Total']
		r=qual+scen+scal+cover
		tempData=self.data['Photos'][realIndex]
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
		self.data['Photos'][realIndex]=tempData.copy()
		
			
			
	def writedata(self):  #<save>='
		with open(self.path+self.packageName+'.json', "w") as file:  
    			json.dump(self.data, file)
		file.close()

	def changePath(self, newPath): #Use to change directory.  Will only effect when opening or creating package
		self.dir=newPath+'/'
	
	def getUrl(self):
		return self.data['Url']

	def getImages(n, f=2): #return a list of images of specified length
		i=0
		imList=[]
		if f==2:
			return self.photos
		while i<n:
		
			if f==1:
				im=Image.open(self.path+self.photos[i]['ImageID'])
				tup=(self.photos[i], im)
				imList.append(tup)
			else:
				imList.append(self.photos[i])
			i=i+1
		return imList

#Used to update outdated formats.  Do not call			
	def update(self): 
		list=[]
		for photo in self.data['Photos']:
			photo['ImageID']=photo['ID']
		self.writedata()					

