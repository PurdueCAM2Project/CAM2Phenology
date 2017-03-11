#Global Phenology, Ehren Marschall, updated 03/07/17
#file with helper functions used to analyze search results and then create better searches (based on ratings of images)

import matplotlib.pyplot as plt

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
	

#Takes a RATED AND SORTED searchPackage (phenImage.py) and finds the best geo locations in the search 
#All geo locations are printed on a grid with color corresponding to value. 
#TODO: put gps tags into exif so we don't have to query flickr for geo location
def geoTrend(pack):
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

	
#The code below takes a user-specified package, sorts it, identifies geo trends based on rating, then creates a new package using targeted geo search in search.py		
def modGeo(analysisPackage, dir):

	from phenImage import searchPackage
	from search import targetedGeoSearch
	data=analysisPackage.data
	print (data)
	photoRatings=data['Photos']
	data['Photos']=sortDict(photoRatings, 'Rating')
	print ('SORTED')
	print (data)
	geotrends=geoTrend(analysisPackage)
	print (geotrends)
	imageList=targetedGeoSearch(data['Url'][0], geotrends, 5)
	targetGeo=searchPackage()
	targetGeo.create(analysisPackage.packageName+'I', len(imageList), data['Url'], imageList, dir)
	targetGeo.writedata()
	print (imageList)
