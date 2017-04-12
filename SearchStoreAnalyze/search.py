#this class handles all image searching.  Retrieval is handled by searchPackage class (in storage)
#All searches done on flickr using flickr API.  Plan to rename flickrSearch and have a master search class to handle searches done from different API's
#Suggest looking at flickr.photos.search on flickr's api explorer
#Somewhat slow depending on internet
#Global Phenology: Ehren Marschall, 3/7/17
import json
import urllib.request
import htmlParser
import storage
from storage import *
import tkinter
from tkinter import *

#below are helper methods to navigate flickr api.  Used in other files as well as this one

#retrieve json from a link
def getJSON(url):
	from urllib.error import URLError, HTTPError
	i=0
	while i<5:
		i=i+1
		try:
			response=urllib.request.urlopen(url)
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		else:		
			response=response.read()
			data=json.loads(response.decode())
			if data['stat']=='ok':
				return data
			break


def retrieveImage(url):
	from urllib.error import URLError, HTTPError
	i=0
	from PIL import Image
	while i<5:
		i=i+1
		try:
			urllib.request.urlretrieve(url, 'temp.jpg')
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		else:
			im=Image.open('temp.jpg')
			return im
#retrieve EXIF
def getEXIF(id):
	url='https://api.flickr.com/services/rest/?method=flickr.photos.getExif&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9&photo_id='+id+'&format=json&nojsoncallback=1'
	data=getJSON(url)
	exif_dict=data['photo']['exif']
	return exif_dict

#return general info
def getInfo(id):
	url='https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9&format=json&nojsoncallback=1&photo_id='+id
	data=getJSON(url)
	return data

#return latitude and longitude (only with photos that have geo tagging)
def getGeo(id):
	url='https://api.flickr.com/services/rest/?method=flickr.photos.geo.getLocation&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9&format=json&nojsoncallback=1&photo_id='+id
	data=getJSON(url)
	if data is not None:
		locate=data['photo']['location']
		tup=(float(locate['latitude']), float(locate['longitude']), float(locate['accuracy']))
		return tup
#Takes flickr ImageID then finds the jpeg link, and the date taken.  
def getImageDict(id):
	data=getInfo(id)
	if data is not None:
		urls=data['photo']['urls']
		geo=getGeo(id)
		pic=htmlParser.htmlParse(urls['url'][0]['_content'])      #grabbing image jpeg link.  Only grabbing photos with dates.  
		if pic is not None:
			date=pic[1]
			dateString = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
			imageDict={'ImageID': id, 'Url': pic[0], 'DateTaken': dateString, 'gps': geo}
			return imageDict
	
	return 'fail' #<--If parser fails to find a date
def getImageTup(id):
	imageDict=getImageDict(id)
	if imageDict !='fail':
		im=retrieveImage(imageDict['Url'])
		return (im, imageDict)

#uses geoTrends in analysis to parse through images and return a dict of the ones that fit the desired geo parameters (does not modify search parameters)
def targetedGeoSearch(url, geotrends, num):
#uses 3 geo locations which are averages of good, medium, and bad ratings in that order
#Search looks for images closest to good, then medium, then bad ratings to find <num> images 
	def calcDistance(x1, x2, y1, y2):
		import math
		dist=math.sqrt((float(x2)-float(x1))**2+(float(y2)-float(y1))**2)
		return dist
	list1=[] #priority 1
	list2=[] #priority 2
	list3=[] #priority 3
	url=url+'&per_page=500'
	data=getJSON(url)
	i=0
	j=0
	page=0	
	photos=data['photos']['photo']
	while i<int(data['photos']['total']) and j<num:
		page=page+1
		data=getJSON(url+'&page='+str(page))	
		photos=data['photos']['photo']
		for photo in photos:
			i=i+1	
			imageDict=getImageDict(photo['id'])
			if imageDict!='fail' and imageDict['gps'] is not None:
				dist1=calcDistance(imageDict['gps'][0], geotrends[0]['lat'], imageDict['gps'][1], geotrends[0]['lon'])
				dist2=calcDistance(imageDict['gps'][0], geotrends[1]['lat'], imageDict['gps'][1], geotrends[1]['lon'])
				dist3=calcDistance(imageDict['gps'][0], geotrends[2]['lat'], imageDict['gps'][1], geotrends[2]['lon'])
				print ('dist1: '+str(dist1)+', dist2: '+str(dist2)+' dist3: '+str(dist3))
				if (dist1<dist2) and (dist1<dist3):
					list1.append(imageDict)
					j=j+1
					if j==num:
						break
				elif (dist2<dist1) and (dist2<dist3):
					list2.append(imageDict)
				else:	
					list3.append(imageDict)
	i=0
	while j<num and i<len(list2):
		list1.append(list2[i])
		j=j+1
		i=i+1
	i=0
	while j<num and i<len(list3):
		list1.append(list3[i])
		j=j+1
		i=i+1
	return list1

#Class used to search flickr and store links to images from the resulting search
#based on user input in searchDisplay.py, the class can launch packageCreator which makes a searchPackage (from storage.py) with desired size and length
#In the future, must create dedicated flickr api search class (with other apis) and have this be a master search class which interacts with the api classes.
#Class primarily used with searchDisplay.py 	  
class Search:

	package=searchPackage()  #one search package used and updated
	pullnum=0	       
	pullPic=''
	printnum=0
	search_type=''
	searchUrls=[]  #Array of searches used in respective search
	links=[]
	pullnum=0
	ids=[]  #one set of ids kept and updated.  This is the 'image cache' in display.
	imageIndex=0 
	def search(self, t, p):  #t is an array of search types, and p is an array of parameters.  Types come pre formattted from searchDisplay to fit flickrs API
		idset=[]
		url='https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9'  #This link uses API key from Ehren Marschall
		i=0
		while (i<len(t)): #formatting parameter
			parameter=p[i]
			parameter=parameter.replace(' ', '+')
			parameter=parameter.replace(',','%C')
			url=url+t[i]+parameter			
			i=i+1
			print (parameter)
		
		url=url+'&per_page=500&format=json&nojsoncallback=1'  #specfying json format.  Useful for python dict{} structure 
		print('Url: '+url)
		data=getJSON(url)
		print(data)
		photos=data['photos']
		total=int(data['photos']['total'])
		print('Number of Search Hits: '+str(total))
		j=0
		while (j<len(photos['photo'])):
			id=photos['photo'][j]['id']
			self.ids.append(id)   #appending flickr photo ids
			j=j+1
		self.searchUrls.append(url)
	
	def imageCircle(self, i):
		imageIndex=imageIndex+i
		imageIndex=imageIndex%len(self.ids)
		imageTup=getImageTup(self.ids[imageIndex])
		if imageTup is not None:
			return imageTup
		else:
			return self.imageCircle(i)			
	
	def clear(self):  #clearing image (id) cache
		print("cleared")
		self.pullnum=0
		del self.searchUrls[:]
		del self.links[:]
		del self.ids[:]


	def pull(self):    #pulling image data to be displayed using Flickr.photos.getInfo.  Pulls one image's data
		if self.pullnum<len(self.ids):
			url2='https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9&photo_id='+self.ids[self.pullnum]+'&format=json&nojsoncallback=1'
			data2=getJSON(url2)
			urls=data2['photo']['urls']
			tempPic=htmlParser.htmlParse(urls['url'][0]['_content'])
			if tempPic is not None:
				self.pullPic=tempPic[0]
				print (data2)
				tempstring=str(data2)
				return tempstring
			else: 
				self.pullnum=self.pullnum+1
				self.pull()
		return "There are no more cached photos"	

	def makePackage(self, numphotos, name, dir, images):  #creating list of image ids and links, of length numphotos to be passed into searchPackage to create a package.  Returns package to searchDisplay   
		i=0
		j=0
		newids=[]
		urlCounter=0
		images.create(name, self.searchUrls, dir)
		while urlCounter<len(self.searchUrls) and i<numphotos:
			url=self.searchUrls[urlCounter]
			urlCounter=urlCounter+1
			data=getJSON(url)
			page=1
			t=0
			while page<=((int(data['photos']['total'])/500)+1) and i<numphotos:
				page=page+1
				if data is not None:
					photos=data['photos']['photo']
					for photo in photos:					
						imageTup=getImageTup(photo['id'])
						if imageTup is not None:
							images.add(imageTup[0], imageTup[1])
							print('added image '+str(i)+'/'+str(numphotos))
							i=i+1
							if i==numphotos:
								break
				data=getJSON(url+'&page='+str(page))
		images.writedata()
		


	def packageCreator(self, dir, images, top2):  #This is a UI made for the user to specify if they want to import a package, or make a new one with their cache of ids.  User specifies name and number of photos
		array=[]
		pname=StringVar(top2)
		pname.set('default')
		top2.title("Package Manager")
		L1=Label(top2, text="If creating new search package, specify desired name and number of images to load (num). Note that you need search images cached.\nYou currently have "+str(len(self.ids))+ " cached images. If you wish to load pre-saved package, please select one").grid(row=0, rowspan=2, columnspan=4, sticky=W+E)
		if not os.path.exists(dir):
			os.makedirs(dir)
		array=os.listdir(dir)
		array.append(' ')
		L2=Label(top2, text='New Package').grid(row=2, column=0, sticky=W+E)
		L3=Label(top2, text="Num").grid(row=2, column=1, sticky=W+E)
		L4=Label(top2, text="Load Package").grid(row=2, column=2)				
		E1=Entry(top2, bd=5)
		entry1=E1
		E1.grid(row=3, column=0)
		E2=Entry(top2, bd=5, width =6)
		entry2=E2
		E2.grid(row=3, column=1)
		importname=''
		E3=Entry(top2, bd=5)
		E3.grid(row=4, column=0)
		def setImport(n):
			def importPackage():
				if n != 'default':
					images.open(n, dir)  #opening already made package
					top2.destroy()
				else: 
					print("Must choose package to import")
			B2.configure(command=importPackage)
			B2.command=importPackage	
		def makeNew():
			print('wait, creating...')
			name=entry1.get()
			num=int(entry2.get())
			self.makePackage(num, name, dir, images)  #making a new package			
			print('done')
			top2.destroy()
		packages=OptionMenu(top2, pname, *array, command =setImport).grid(row=3, column=3)
		B2=Button(top2, text='Import Package', width=10)
		B2.grid(row=3, column=4)
		B1=Button(top2, text="Make Package", width=10, command=makeNew)
		B1.grid(row=3, column=2)
		
