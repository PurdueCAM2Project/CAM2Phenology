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

flickrkey=input("Enter flickr API key: ")
with open("apikeys.json", 'w+') as file:
	json.dump({'flickr': flickrkey}, file)
file.close()

