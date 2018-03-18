#Setup script
import json
"""
preferences.txt:
<db host address>
<db user name>
<dbname>

apikeys.json:
{source: key}
"""
print("Initial setup...")
address=input("Enter database host address: ")
username=input("Enter database user name: ")
dbname=input("Enter database name")
with open("preferences.txt", 'w+') as file:
	file.write(address+" "+username+" "+dbname)
file.close()

keys={}
keys['flickr']=input("Enter flickr API key: ")
keys['twitter_consumer_key']=input("Enter Twitter consumer key: ")
keys['twitter_consumer_secret']=input("Enter Twitter consumer Secret: ")
keys['twitter_access_token']=input("Enter Twitter access token: ")
keys['twitter_access_secret']=input("Enter Twitter access secret: ")
with open("apikeys.json", 'w+') as file:
	json.dump(keys, file)
file.close()

