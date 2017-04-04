#Global Phenology, Ehren Marschall, updated 03/07/17
#file with helper functions used to analyze search results and then create better searches (based on ratings of images)
import data
from data import *


#sorts image dictionaries based on their <key> value.  For example, key='Rating'.  
#Uses standard quicksort and sorts in descending order
def sortDict(list, key):
	less=[]
	more=[]
	same=[]
	
	if len(list)>1:
		pivot=list[0][key]
		for dict in list:
			if dict[key]<pivot:
				less.append(dict)
			if dict[key]==pivot:
				same.append(dict)
			if dict[key]>pivot:
				more.append(dict)
		
		return sortDict(more, key)+same+sortDict(less, key)
	else:
		return list		
	

#Takes a RATED AND SORTED searchPackage (storage.wpy) and finds the best geo locations in the search 
#All geo locations are printed on a grid with color corresponding to value. 
def plotGeo(source):
	import gmplot
	gmap=gmplot.GoogleMapPlotter(35.6583, -83.5200, 13.8)

	print('TOTAL: '+str(source.total))
	i=0
	lats=[]
	longs=[]
	while i<source.total:
		exif=source.getEXIF(i)
		dict=eval(exif['Exif'][piexif.ExifIFD.UserComment])
		location=dict['gps']
		if location is not None:
		#	plot.plot([location[1]], [location[0]], 'ko')
			lats.append(location[0])
			longs.append(location[1])
			print(i)
		i=i+1
#	gmap.heatmap(lats, longs, radius=50, threshold=40000, dissipating=True)
	gmap.scatter(lats, longs, 'ro', size=20, marker=False)
	gmap.draw('/mnt/c/Users/emars/Desktop/ccLargeGeoPlot2.html')
	#plt.show()	

def geoTrend(pack):
	import matplotlib.pyplot as plt

	i=0
	photoset=pack.data['Photos']
	geo=[{'lat': 0, 'lon': 0}, {'lat': 0, 'lon': 0}, {'lat': 0, 'lon': 0}, {'lat': 0, 'lon': 0}]
	lat=0
	lon=0
	accuracy=0
	totalrate=0
	i=0
	color='go'
	flag=0
	interval=len(photoset)/4
	colorList=['ko', 'ro', 'yo']
	color='go'
	t=0
	for photo in photoset:
		i=i+1
		if i>interval and totalrate!=0:
			color=colorList.pop()		
			geo[t]['lat']=lat/totalrate
			geo[t]['lon']=lon/totalrate
			i=0
			t=t+1
			totalrate=0
			lat=0
			lon=0
		location=photo['gps']					
		rate=photo['Rating']
		if location is not None:
			totalrate=totalrate+1
			plt.plot([location[0]], [location[1]], color)
			lat=lat+float(location[0])
			lon=lon+float(location[1])
			accuracy=accuracy+float(location[2])
	#plt.show()
	return geo

def geoParse(source, num, geotrends, newPackage):
	from storage import searchPackage
	def calcDistance(x1, x2, y1, y2):
		import math
		dist=math.sqrt((float(x2)-float(x1))**2+(float(y2)-float(y1))**2)
		return dist
	i=0
	images=source.getImages(0, 30)
	list1=[]
	list2=[]
	list3=[]
	index=0
	while len(images) >0:
		for image in images:
			if image[1]['gps'] is not None:
				dist1=calcDistance(image[1]['gps'][0], geotrends[0]['lat'], image[1]['gps'][1], geotrends[0]['lon'])
				dist2=calcDistance(image[1]['gps'][0], geotrends[1]['lat'], image[1]['gps'][1], geotrends[1]['lon'])
				dist3=calcDistance(image[1]['gps'][0], geotrends[2]['lat'], image[1]['gps'][1], geotrends[2]['lon'])
				if (dist1<dist2) and (dist1<dist3):
					newPackage.add(image)
					j=j+1
					if i==num:
						break
				elif (dist2<dist1) and (dist2<dist3) and len(list2)+j<num:
					list2.append(image)
				elif len(list2)+len(list3)+j<num:
					list3.append(image)
		index=index+30
		images=source.getImages(index, index+30)
	t=0
	if i<num and t<len(list2):
		newPackage.add(list2[t])
		t=t+1
		i=i+1

	t=0
	if i<num and t<len(list3):
		newPackage.add(list3[t])
		t=t+1
		i=i+1
	return list1


					
#The code below takes a user-specified package, sorts it, identifies geo trends based on rating, then creates a new package using targeted geo search in search.py		
def modGeo(analysisPackage, sourcePackage, dir):

	from storage import searchPackage
	from search import targetedGeoSearch
	data=analysisPackage.data
	print (data)
	photoRatings=data['Photos']
	data['Photos']=sortDict(photoRatings, 'Rating')
	print ('SORTED')
	print (data)
	geotrends=geoTrend(analysisPackage)	
	print (geotrends)
#	imageList=targetedGeoSearch(data['Url'][0], geotrends, analysisPackage.data['Total'])
	targetGeo=searchPackage()
	targetGeo.create(analysisPackage.packageName+'I', data['Url'],  dir)
	geoParse(sourcePackage, analysisPackage.data['Total'], geotrends, targetGeo)  
	targetGeo.writedata()
	print (imageList)
