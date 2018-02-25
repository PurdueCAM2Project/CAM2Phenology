import tweepy as tw
from jsonpickle import encode

def authentication():
    keyFile = open('Consumer_Key.txt', 'r')
    keys = keyFile.readlines()
    auth = tw.OAuthHandler(keys[0][:-1], keys[1][:-1])
    auth.set_access_token(keys[2][:-1], keys[3])
    return auth

def scrape():
    api = tw.API(authentication(), wait_on_rate_limit=True, wait_on_rate_limit_notify=True) #set up keys for access
    if not api:
        print("API not auth'd properly")
        return
    logFile = open('TweetLog.txt', 'w')

    #TODO change this as needed for search
    searchQuery = '#smoky OR #smokymountains'# OR #gatlinburg OR #gatlinburgTN'

    i = 0
    for tweet in tw.Cursor(api.search, q=searchQuery).items():
        for media in tweet.entities.get("media", [{}]):
            if media.get("type", None)== "photo":
                logFile.write(encode(tweet._json) + '\n')
                print(media["media_url_https"])

scrape()
