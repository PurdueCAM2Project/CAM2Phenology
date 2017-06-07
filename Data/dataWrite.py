import os
import os.path

if not os.path.exists('dataAnalysis'):
	os.makedirs('dataAnalysis')

if not os.path.isfile('preferences.txt'):
	with open('preferences.txt', 'w+') as file:
		dir='data/'
		d=input("Please specify your image storage directory\n Press Enter for default (data/)")
		if d!='':
			dir=d
			file.write(dir)
		else:
			file.write('data/')
with open('preferences.txt') as file:
	preferences=file.read().splitlines()
dir=preferences[0]

#this is the most time consuming sorting and should be done first.
def analyzeDates(source):
	import json
	from data import getDates, getGPS, getEXIF
	from analysis import dateSort, dateAnalyze
	dates=getDates(source)
	print (source.images)
	new_dates=dateSort(dates)
	info=dateAnalyze(new_dates)
	dated_images=[]
	for date in new_dates:
		images=[]
		for image in date[1]:
			#'image' is a reference to an index in the array of image file strings stored in source
			exif_dict=getEXIF(source.directory
+source.images[image])
			gps=getGPS(exif_dict)
			d=source.images[image].split('/')
			id=d[len(d)-1]
			images.append((id, gps))
		dated_images.append((date[0], images))
	dump_dict={'days': dated_images, 'info': info}
	print(source.directory)
	array=source.directory.split('/')
	name=array[len(array)-2]
	with open('dataAnalysis/'+name+'.json', 'w+') as file:
		json.dump(dump_dict, file)
	file.close()



		

from sources import LocalStorage
ls=LocalStorage(dir+'web_ui_test/')
analyzeDates(ls)
