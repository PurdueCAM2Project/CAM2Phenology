#this class handles all image searching.  Retrieval is handled by searchPackage class (in phenImage)
#All searches done on flickr using flickr API.  Plan to rename flickrSearch and have a master search class to handle searches done from different API's
#Suggest looking at flickr.photos.search on flickr's api explorer
#Somewhat slow depending on internet
#Global Phenology: Ehren Marschall, 2/7/17
import json
import urllib.request
import htmlParser
import phenImage
from phenImage import *
import tkinter
from tkinter import *

#below are helper methods to navigate flickr api.  Used in other files as well as this one

#retrieve json from a link
def getJSON(url):
	response=urllib.request.urlopen(url)
	response=response.read()
	data=json.loads(response.decode())
	return data

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
	return data

#Takes flickr ImageID then finds the jpeg link, and the date taken.  
def getImageLink(id):
	data=getInfo(id)
	urls=data['photo']['urls']
	pic=htmlParser.htmlParse(urls['url'][0]['_content'])      #grabbing image jpeg link.  Only grabbing photos with dates.  
	if pic is not None:
		date=pic[1]
		dateString = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
		imageDict={'ImageID': id, 'Url': pic[0], 'DateTaken': dateString}
		return imageDict
	else:
		return 'fail' #<--If parser fails to find a date

#uses geoTrends in analysis to parse through images and return a dict of the ones that fit the desired geo parameters (does not modify search parameters)
def targetedGeoSearch(url, geotrends, num):
#uses 3 geo locations which are averages of good, medium, and bad ratings in that order
#Search looks for images closest to good, then medium, then bad ratings to find <num> images 
	def calcDistance(x1, y1, x2, y2):
		import math
		dist=math.sqrt((float(x2)-float(x1))**2+(float(y2)-float(y1))**2)
		return dist
	list1=[] #priority 1
	list2=[] #priority 2
	list3=[] #priority 3
	url=url+'&per_page=500'
	data=getJSON(url)
	photos=data['photos']['photo']
	i=0
	j=0
	while i<len(photos) and j<num:
		print (i)
		geo=getGeo(photos[i]['id'])
		if geo is not None:
			imageDict=getImageLink(photos[i]['id'])
			if imageDict!='fail':
				location=geo['photo']['location']
				dist1=calcDistance(location['latitude'], geotrends[0]['lat'], location['longitude'], geotrends[0]['lon'])
				dist2=calcDistance(location['latitude'], geotrends[1]['lat'], location['longitude'], geotrends[1]['lon'])
				dist3=calcDistance(location['latitude'], geotrends[2]['lat'], location['longitude'], geotrends[2]['lon'])
				if (dist1<dist2) and (dist1<dist3):
					list1.append(imageDict)
					j=j+1
				elif (dist2<dist1) and (dist2<dist3):
					list2.append(imageDict)
				else:	
					list3.append(imageDict)
		i=i+1
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
#based on user input in searchDisplay.py, the class can launch packageCreator which makes a searchPackage (from phenImage.py) with desired size and length
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

	def clear(self):  #clearing image (id) cache
		print("cleared")
		self.pullnum=0
		self.searchUrls=''
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

	def makePackage(self, numphotos, name):  #creating list of image ids and links, of length numphotos to be passed into searchPackage to create a package.   
		i=0
		j=0
		imgInfo=[]
		newids=[]
		subIndex=len(self.ids)//numphotos
		index=0
		while (i<numphotos and j<len(self.ids)):
			index=(subIndex*j+index//len(self.ids))%len(self.ids)     #This will pull evenly from entire cache of ids to ensure that all searches get used regardless of numphotos value
			imageDict=getImageLink(self.ids[index])
			if imageDict!='fail':
				imgInfo.append(imageDict.copy())
				newids.append(self.ids[index])
				i=i+1
			j=j+1
		self.package.create(name, len(imgInfo), self.searchUrls, imgInfo)
		

	def packageCreator(self):  #This is a UI made for the user to specify if they want to import a package, or make a new one with their cache of ids.  User specifies name and number of photos
		array=[]
		top2=Toplevel()
		pname=StringVar(top2)
		pname.set('default')
		top2.title("Package Manager")
		L1=Label(top2, text="If creating new search package, specify desired name and number of images to load (num). Note that you need search images cached.\nYou currently have "+str(len(self.ids))+ " cached images. If you wish to load pre-saved package, please select one").grid(row=0, rowspan=2, columnspan=4, sticky=W+E)
		if not os.path.exists('packages/'):
			os.makedirs('packages/')
		array=os.listdir(self.package.dir)
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
		def changeDir():
			self.package.changePath(E3.get())
	
		def setImport(n):
			def importPackage():
				if n != '<package>':
				
					self.package.open(n)  #opening already made package
					top2.destroy()
				else: 
					print("Must choose package to import")
			B2.configure(command=importPackage)
			B2.command=importPackage	
		def makeNew():
			name=entry1.get()
			num=int(entry2.get())
			alert=Label(top2, text="WAIT-creating...").grid(row=3, sticky=W+E)
			self.makePackage(num, name)  #making a new package
			top2.destroy()
		packages=OptionMenu(top2, pname, *array, command =setImport).grid(row=3, column=3)
		B2=Button(top2, text='Import Package', width=10)
		B2.grid(row=3, column=4)
		B1=Button(top2, text="Make Package", width=10, command=makeNew)
		B1.grid(row=3, column=2)
		B3=Button(top2, text='SpecifyDir', width=10, command=changeDir)	
		B3.grid(row=4, column=1)
