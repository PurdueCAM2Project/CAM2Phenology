import flickrSearch
import json
import os.path

#The implementation of a general web search needs much more work
if not os.path.exists('searches'):
	os.makedirs('searches')
	with open('searches/searchDump.json', 'w+') as file:
		dict={'flickr_ids': []}
		json.dump(dict, file)
	file.close()
	
			
def download(url, path=''):
	import urllib.request
	from urllib.error import URLError, HTTPError
	i=0
	while i<5:
		#print(id)
		#print(url)
		i=i+1
		try:
			urllib.request.urlretrieve(url, path+'temp.jpg')
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		else:
			return


class WebSearch:

	flickr_ids=[] #cached flickr image ids
	total=0		  #total cached search images
	
	def imageSearch(self, types, parameters):
		"""ideally, this should take a generalized search dictionary.
	The api scripts should then individually parse the search paramters to format their own url.
	I am unsure of the best way to integrate this until we are working with more apis.
	For now it is only set up for flickr.
	"""	
		search=flickrSearch.search(types, parameters)
		self.total=self.total+int(search[1])
		self.flickr_ids.extend(search[0])
		print('Total Search Hits: '+str(self.total))
		
	def sampleSearch(self, num_images=12):
		metadata=[]
		import random
		random.shuffle(self.flickr_ids)
		i=0
		j=0
		while (i<num_images):
			image_data=self.getSearchData(j)
			if image_data is not None:
				image_data=(self.getSearchData(j))
				metadata.append(image_data)
				print(image_data)
				i+=1
			j+=1
				
		print("Sample Complete")				
		return metadata
		
	def getSearchData(self, index):
		#Returns the data for 1 image
		image_dict=flickrSearch.getImageDict(self.flickr_ids[index])
		return image_dict	
		
	def clear(self):
		del self.flickr_ids[:]
		self.total=0	
	
	#records all of the data from the search in a format ready to be committed to database. 
	#Data is a dictionary
	def recordData(self, data, search_id):
		file_name='search_'+str(search_id)
		with open('searches/file_name.json', 'w+') as file:
			json.dump(data, file)
		file.close()
			
	#records the search with a search id and all search parameters
	def recordSearch(self, search_dict):
		with open('searches/searches.json', 'r+') as file:
			data=json.load(file)
			data['searches'].append(search_dict)
		file.close()
		
		
			