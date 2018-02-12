#formats urls and parses data for flickr.com

import json
import urllib.request
from urllib.error import URLError, HTTPError
from datetime import datetime
import htmlParser
import apirequest

with open('apikeys.json', 'r') as file:
	key=json.load(file)['flickr']
file.close()

url='https://api.flickr.com/services/rest/?method=flickr.photos.'
format='&format=json&nojsoncallback=1' #specifying json format in url

def getResponse(url):
	i=0
	while i<5:
		i=i+1
		try:
			response=urllib.request.urlopen(url)
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		except Exception as e:
			print(e.message)
		else:
			response=response.read()
			return response
			
def searchIds(params):
	#gets the image ids of search given by params {}
	#https://www.flickr.com/services/api/explore/flickr.photos.search
	
	lat=params['lat']
	lon=params['lon']
	radius=params['radius']
	searchurl=url
	searchurl=url+'search&api_key='+key+'&per_page=500'+format
	searchurl=searchurl+'&lat='+str(lat)+'&lon='+str(lon)+'&radius='+str(radius)
	data=json.loads(getResponse(searchurl).decode())
	total=int(data['photos']['total'])
	ids=[]
	page=1
	pages=int(data['photos']['pages'])
	for photo in data['photos']['photo']:
		ids.append(photo['id'])
	while page<pages:
		page+=1
		data=json.loads(getResponse(searchurl+'&page='+str(page)).decode())
		for photo in data['photos']['photo']:
			ids.append(photo['id'])
	#print(total)
	#print(str(len(ids)))
	return ids
	

#-----metadata processing functions for individual ids (below)----
"""def buildUrls(id):
	#builds all necessarry urls for given image id
	urls={}
	urls=[url+'getInfo&api_key='+key+'&format=json&nojsoncallback=1&photo_id='+str(id)]
	return urls"""
	
def getInfo(id):
	#https://www.flickr.com/services/api/explore/flickr.photos.getInfo
	response=getResponse(url+'getInfo&api_key='+key+'&format=json&nojsoncallback=1&photo_id='+str(id))
	return response
	
def parseInfo(data):
	#parsing info retrieved from urls. formatting for database insertion. see database attributes
	data=json.loads(data.decode())
	if data is not None:
		image_dict={}
		urls=data['photo']['urls']
		url=urls['url'][0]['_content']
		#url=htmlParser.htmlParse(urls['url'][0]['_content'])
		if url is None:
			return None
		if("location" not in data['photo'].keys()):
			return None
		location=data['photo']['location']
		if('dates' not in data['photo'].keys()):
			return None
		dates=data['photo']['dates']
		if ('taken' not in dates.keys()):
			return None
		date_taken=datetime.strptime(dates['taken'], "%Y-%m-%d %H:%M:%S")
		if ('people' in data['photo'].keys()):
			people=data['photo']['people']
			if('haspeople' in people.keys()):
				image_dict['haspeople']=int(people['haspeople'])
		id=data['photo']['id']
		owner=data['photo']['owner']
		userid=owner['nsid']
		gps=(float(location['latitude']), float(location['longitude']))
		image_dict={'id': id, 'url': url, 'date_taken': date_taken, 'gps': gps, 'source': 'flickr', 'userid': userid}
		image_dict['latitude']=gps[0]
		image_dict['longitude']=gps[1]
		return image_dict
		
def findJpeg(image_dict):
	#parsing through html retrieved from the url given by flickr's 'getInfo' query to find jpeg link
	url=htmlParser.htmlParse(getResponse(image_dict['url']))
	return url
	
def processID(id):
	#Calling all functions to process given id
	info=getInfo(id)
	image_dict=parseInfo(info)
	image_dict['url']=findJpeg(image_dict)
	if image_dict['url'] is not None:
		return image_dict
	
	
	