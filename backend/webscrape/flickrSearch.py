import json
import urllib.request
from datetime import datetime

#This was made to be its own independent search of flickr.
#It has not been modified, but it is still currently used with general search classs

with open('APIkeys.json', 'r') as file:
	keys=json.load(file)
file.close()
key=keys['flickr']
mUrl='https://api.flickr.com/services/rest/?method=flickr.photos.'

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
		except Exception as e:
			print(e.message)
		else:
			response=response.read()
			data=json.loads(response.decode())
			if data['stat']=='ok':
				return data
			break


def search(types, parameters):
	ids=[]
	url=mUrl+'search&api_key='+key+'&per_page=500&format=json&nojsoncallback=1'
	i=0
	while (i<len(types)): #formatting parameter
		parameter=parameters[i]
		parameter=parameter.replace(' ', '+')
		parameter=parameter.replace(',','%C')
		url=url+'&'+types[i]+'='+parameter
		i=i+1
	data=getJSON(url)
	print(url)
	#print(data)
	#print('Search Hits:'+data['photos']['total'])
	total=data['photos']['total']
	done=0
	page=1
	while(done==0):
		photos=data['photos']['photo']
		for photo in photos:
			ids.append(photo['id'])
		if len(ids)>=int(data['photos']['total']):
			done=1
		else:
			page=page+1
			print("Grabbing Page" +str(page))
			data=getJSON(url+'&page='+str(page))
	#print('Search Complete')
	return (ids, total)

def getInfo(id): #getting url to send to html parser for parsing (not jpeg url.)
	url=mUrl+'getInfo&api_key='+key+'&format=json&nojsoncallback=1&photo_id='+str(id)
	data=getJSON(url)
	if( data is not None and data['stat']=='ok'):
		return data
	else:
		return None

def getGeo(id):
	url=mUrl+'geo.getLocation&api_key='+key+'&format=json&nojsoncallback=1&photo_id='+str(id)
	data=getJSON(url)
	if data is not None:
		locate=data['photo']['location']
		tup=(float(locate['latitude']), float(locate['longitude']), float(locate['accuracy']))
		return tup

def retrieveImage(url, id, dir):
	from urllib.error import URLError, HTTPError
	from PIL import Image
	i=0
	while i<5:
		#print(id)
		#print(url)
		i=i+1
		try:
			urllib.request.urlretrieve(url, dir+str(id)+'.jpg')
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		else:
			"""im=Image.open(dir+str(id)+'.jpg')
			return im"""
			return 'success'
def getUserid(image_id):
#getting the user who uploaded the image
	data=getInfo(image_id)
	#print(str(image_id))
	if data is not None:
		owner=data['photo']['owner']
		userid=owner['nsid']
		#print(userid)
		return userid
	print('none')
		


def getPeople(image_id):
#returns 1 if flickr api says the image has people and 0 otherwise
	data=getInfo(image_id)
	if data is not None:
		if('people' in data['photo'].keys()):
			people=data['photo']['people']
			if 'haspeople' in people.keys():
				haspeople=int(people['haspeople'])
				#print(str(haspeople))
				return haspeople
	print('none')
		

#Takes flickr ImageID then finds the jpeg link and relevant metadata
def getImageDict(id):
	import htmlParser
	data=getInfo(id)
	image_dict={}
	if data is not None:
		urls=data['photo']['urls']
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
		owner=data['photo']['owner']
		image_dict['userid']=owner['nsid']
		
		pic=htmlParser.htmlParse(urls['url'][0]['_content'])  #grabbing image jpeg link from html
		if pic is None:
			return None
			"""date=pic[1]
			dayint=0
			dayint=dayint+int(date[0])*10000 + int(date[1])*100 + int(date[2])"""
		gps=(float(location['latitude']), float(location['longitude']))
		image_dict={'id': id, 'url': pic, 'date_taken': date_taken, 'gps': gps, 'source': 'flickr'}
		image_dict['latitude']=gps[0]
		image_dict['longitude']=gps[1]
		#I am inserting redundant latitude/longitude values for the UrlIterator class. (08/31/17)
		return image_dict
	#print('fail')
	return None #<--If parser fails to find a date

def getImageTup(id, dir):
	imageDict=getImageDict(id)
	if imageDict !='fail':
		result=retrieveImage(imageDict['Url'], id, dir)
		if result is not None:
			return (imageDict)


		

					
	
	
