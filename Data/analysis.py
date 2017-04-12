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

def calcDistance(coordinate1, coordinate2):
	import math
	dist=math.sqrt((coordinate1[0]-coordinate2[0])**2+(coordinate1[1]-coordinate2[1])**2)
	return dist

def calcMidpoint(coordinate1, coordinate2):
	midlat=(coordinate1[0]+coordinate2[0])/2
	midlong=(coordinate1[1]+coordinate2[1])/2
	return (midlat, midlong)
#Can add more data to coordinate tuple.  The first two values are lat,long.
#Example: (lat, long, imageID)
def geoAnalyze(coordinates):
	minlat=coordinates[0][0]
	minlong=coordinates[0][1]
	maxlat=coordinates[0][0]
	maxlong=coordinates[0][1]
	avglat=0
	avglong=0
	size=len(coordinates)
	for coordinate in coordinates:
		if coordinate[0]>maxlat:
			maxlat=coordinate[0]
		if coordinate[0]<minlat:
			minlate=coordinate[0]
		if coordinate[1]>maxlong:
			maxlong=coordinate[1]
		if coordinate[1]<minlong:
			minlong=coordinate[1]
		avglat=avglat+coordinate[0]
		avglong=avglong+coordinate[1]

	avglat=avglat/size
	avglong=avglong/size
	minpoint=(minlat, minlong)
	maxpoint=(maxlat, maxlong)
	radius=(calcDistance(minpoint, maxpoint))/2
	center=calcMidpoint(minpoint, maxpoint)
	return {'center': center, 'maxpoint': maxpoint, 'minpoint': minpoint, 'radius': radius,
		'meanpoint': (avglat, avglong)}

def geoCluster(coordinates, percentage):
	analysis_dict=geoAnalyze(coordinates)
	radius=analysis_dict['radius']
	cluster_dist=percentage*radius
	clusters=[]
	analysis_dict['clusters']=clusters
	for coordinate in coordinates:
		flag=0
		min_dist=cluster_dist
		clusterRef={}
		clusterRef['points']=[]
		clusterRef['meanpoint']=(0, 0)
		for cluster in clusters:
			dist=calcDistance(coordinate, cluster['meanpoint'])
			if dist<min_dist:
				flag=1
				min_dist=dist
				clusterRef=cluster
		clusterRef['points'].append(coordinate)
		size=len(clusterRef['points'])
		meanlat=(coordinate[0]/size)+(clusterRef['meanpoint'][0]*(size-1))/size
		meanlong=(coordinate[1]/size)+(clusterRef['meanpoint'][1]*(size-1))/size
		clusterRef['meanpoint']=(meanlat, meanlong)
		if flag==0:
			clusters.append(clusterRef)
	return analysis_dict			
				
	
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

def compareDate(date1, date2):
	from data import dayParse
	dayDiff=dayParse(date1)-dayParse(date2)
	yearDiff=(date1[0]-date2[0])*365
	totalDiff=yearDiff+dayDiff #Total difference, in days, of date1-date2
	return totalDiff
def dateSort(dates):
	new_dates=[]
	min_day=2030*365
	inserted=0
	length=len(dates)
	i=0
	date_dict={}
	for date in dates:
		if str(date) not in date_dict.keys():
			date_dict[str(date)]=[]
			date_dict[str(date)].append(i)
		else:
			date_dict[str(date)].append(i)
		i=i+1
	date_values=date_dict.keys()
	used_values=[]
	i=0
	length=len(date_values)
	while len(new_dates)<length:
		min_day=2030*365
		for value in date_values:
			if int(value)<min_day and value not in used_values:
				min_day=int(value)
		new_dates.append((min_day, date_dict[str(min_day)]))
		used_values.append(str(min_day))
	return new_dates

def dateAnalyze(dates):
	import data
	totals=[0]*365
	min=9999999
	max=-9999999
	minDay=[]
	maxDay=[]
	for date in dates:
		if date[0]<min:
			min=date[0]
		if date[0]>max:
			max=date[0]
		totals[date[0]%365]=len(dates[1])
	return (totals, max, min, max-min)
		
					
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
