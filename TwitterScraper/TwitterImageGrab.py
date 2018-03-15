import tweepy as tw

def authentication():
    keyFile = open('Consumer_Key.txt', 'r')
    keys = keyFile.readlines()
    auth = tw.OAuthHandler(keys[0][:-1], keys[1][:-1])
    auth.set_access_token(keys[2][:-1], keys[3])
    return tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)  # set up keys for access

def processID(id):
    api = authentication()  # set up keys for access
    if not api:
        print("API not auth'd properly")
        return
    tweet = api.get_status(id)
    coordinates = tweet.place.bounding_box.coordinates[0][0]
    url = tweet.entities.get("media", [{}])[0]['media_url_https']
    return {'latitude': coordinates[1], 'longitude':coordinates[0], 'url':url, 'date_taken':tweet.created_at}

def searchIds(searchType, params=None, query=None):
    api = authentication() #set up keys for access
    if not api:
        print("API not auth'd properly")
        return
    idList = []
    geocode = None
    searchQuery = None
    if params is not None and searchType == 1:
        geocode = str(params['lat']) + ',' + str(params['lon']) + ',' + str(params['radius']) + "km"
    elif searchType == 1 and params is None:
        print("Error: Search Type is for geolocation but no coordinates provided")
        return None
    elif searchType == 2 and query is None:
        print("Error: Search Type is for query but no query provided")
        return None
    elif searchType == 2 and query is not None:
        searchQuery = query
    for tweet in tw.Cursor(api.search, q=searchQuery, geocode=geocode).items():
        #print(tweet.text)
        for media in tweet.entities.get("media", [{}]):
            if media.get("type", None)== "photo":
                #logFile.write(encode(tweet._json) + '\n')
                #print(media["media_url_https"])
                idList.append((tweet, media["media_url_https"]))
    return idList

geocode = {"lat":35.611931, "lon":-83.549657, "radius":3} #3 km radius around Smoky Mountains
search = searchIds(1, params=geocode)
print (search)
processID(search[0][0].id_str)
#print(searchIds(2, query="#smokymountains"))
