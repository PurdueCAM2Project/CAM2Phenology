import tweepy as tw
import json

with open('apikeys.json', 'r') as file:
	keys=json.load(file)
file.close()

authenticated=True

def authenticate():
	auth=tw.OAuthHandler(keys['twitter_consumer_key'], keys['twitter_consumer_secret'])
	auth.set_access_token(keys['twitter_access_token'], keys['twitter_access_secret'])
	return tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

"""def authentication():
	keyFile = open('Consumer_Key.txt', 'r')
	keys = keyFile.readlines()
	auth = tw.OAuthHandler(keys[0][:-1], keys[1][:-1])
	auth.set_access_token(keys[2][:-1], keys[3])
	return tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)  # set up keys for access"""

def processID(id):
	api=authenticate()
	if not api:
		print("API not auth'd properly")
		return
	tweet = api.get_status(id)
	if tweet is not None:
		coordinates = tweet.place.bounding_box.coordinates[0][0]
		url = tweet.entities.get("media", [{}])[0]['media_url_https']
		return {'id': id, 'source': 'twitter', 'latitude': coordinates[1], 'longitude': coordinates[0], 'gps': (coordinates[1], coordinates[0]), 'url': url, 'date_taken': tweet.created_at}
	return -1

def searchIds(params):
	idList = []
	geocode = None
	searchQuery = None
	api=authenticate()
	if not api:
		print('twitter authentication failed')
	if 'lat' in params.keys() and 'lon' in params.keys() and 'radius' in params.keys():	
		geocode = str(params['lat']) + ',' + str(params['lon']) + ',' + str(params['radius']) + "km"
	if 'tag' in params.keys():
		searchQuery='#'+params['tag'].replace(" ", "")
		print(searchQuery)
	if geocode:
		for tweet in tw.Cursor(api.search, q=None, geocode=geocode).items():
			#print(tweet.text)
			for media in tweet.entities.get("media", [{}]):
				if media.get("type", None)== "photo":
					#logFile.write(encode(tweet._json) + '\n')
					#print(media["media_url_https"])
					idList.append(int(tweet.id_str))
					#idList.append((tweet, media["media_url_https"]))
	if searchQuery:
		for tweet in tw.Cursor(api.search, q=searchQuery, geocode=None).items():
			#print(tweet.text)
			for media in tweet.entities.get("media", [{}]):
				if media.get("type", None)== "photo":
					#logFile.write(encode(tweet._json) + '\n')
					#print(media["media_url_https"])
					idList.append(int(tweet.id_str))
					#idList.append((tweet, media["media_url_https"]))
	print("Twitter Images: "+str(len(idList)))
	print(str(idList))
	return idList

"""geocode = {"lat":35.611931, "lon":-83.549657, "radius":3} #3 km radius around Smoky Mountains
search = searchIds(geocode)
print (search)
processID(search[0][0].id_str)
print(searchIds(None, query="#smokymountains"))"""
