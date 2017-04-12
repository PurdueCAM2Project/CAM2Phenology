import piexif
from PIL import Image
import os
import os.path


def initialImage(dict, location, im):
	import datetime
	from datetime import datetime

	im.save(location)

	exif_dict=piexif.load(location)
	exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]=dict['DateTaken']
	exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]=str(datetime.today())
	exif_dict['Exif'][piexif.ExifIFD.ImageUniqueID]=dict['ImageID']
	exif_dict['Exif'][piexif.ExifIFD.UserComment]=str(dict)
	exif_bytes=piexif.dump(exif_dict)
	piexif.insert(exif_bytes, location)


def insertRating(dict, location):
	import datetime
	from datetime import datetime

	exif_dict=piexif.load(location)
	exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]=str(datetime.today())
	rateDict=eval(exif_dict['Exif'][piexif.ExifIFD.UserComment])
	rateDict['Rating']=dict['Rating']
	rateDict['Quality']=dict['Quality']
	rateDict['Scene']=dict['Scene']
	rateDict['Coverage']=dict['Coverage']
	rateDict['Scale']=dict['Scale']
	exif_dict['Exif'][piexif.ExifIFD.UserComment]=str(rateDict)
	exif_bytes=piexif.dump(exif_dict)
	piexif.insert(exif_bytes, location)

def getGPS(exif_dict):
	dict=eval(exif_dict['Exif'][piexif.ExifIFD.UserComment])
	location=dict['gps']
	if location is not None:
		return location
	else:
		print('No GPS Data')

def getImage(location):
	im=Image.open(location)
	return im

def getEXIF(location):
	exif_dict=piexif.load(location)
	return exif_dict

def parseDir(path):
	images=[]
	subDir=os.listdir(path)
	for item in subDir:
		if os.path.isfile(path+item):
			images.append(path+item)
		else:
			images.extend(parseDir(path+item+'/'))
	return images

def getGeo(source):
	i=0
	coordinates=[]
	while i<source.total:
		exif=source.getEXIF(i)
		dict=eval(exif['Exif'][piexif.ExifIFD.UserComment])
		location=dict['gps']
		if location is not None:
			coordinates.append((location[0], location[1]))
		i=i+1
	return coordinates
	
def makeGMPlot(coordinateGroups):
	import gmplot
	gmap=gmplot.GoogleMapPlotter(35.6583, -83.5200, 13.8)
	lats=[]
	longs=[]
	colors = ['r', 'b', 'c', 'm', 'w', 'k', 'y', 'g']
	i=0
	for coordinates in coordinateGroups:
		i=i+1
		print (i)
		lats=[]
		longs=[]
		for coordinate in coordinates:
			lats.append(coordinate[0])
			longs.append(coordinate[1])
		#gmap.heatmap(lats, longs, radius=50, threshold=40000, dissipating=True)
		i=i%len(colors)
		gmap.scatter(lats, longs, colors[i], size=25, marker=False)
	gmap.draw('/mnt/c/Users/emars/Desktop/ccLargeGeoClusterPlot.TEST.html')


#Modules to deal with dates
month_list=[('Null', 365, 0), ('January', 0, 31), ('February', 31, 28), ('March', 59, 31),
	('April', 90, 30), ('May', 120, 31), ('June', 151, 30), ('July', 181, 31),
	('August', 212, 31), ('September', 243, 30), ('October', 273, 31),
	('November', 304, 30), ('December', 334, 31)]

def parseDate(date_exif):
	date_string=str(date_exif)
	newDate=[]
	date_string=dateString.replace("b", "")
	date_string=dateString.replace("'", "")
	date=date_string.split('-')
	newDate.append(int(date[0]))
	newDate.append(int(date[1]))
	newDate.append(int(date[2]))
	return newDate
	
def getDates(source):
	dates=[]
	i=0
	while i<source.total:
		dict=source.getEXIF(i)
		date_exif=dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
		day=dateToDay(date_exif)
		dates.append(day)
		i=i+1
	return dates

def dateToDay(date):
	date=str(date)
	date=date.replace("b", "")
	date=date.replace("'", "")
	date_array=date.split('-')
	year=int(date_array[0])
	month=int(date_array[1])
	day=int(date_array[2])
	total_day=(year-1950)*365+month_list[month][2]+day
	return total_day

def dayToDate(day):
	days=day%365
	year=1950+(day//365)
	month=0
	month_total=0
	while days>month_total:
		month=month+1
		month_total=month_total+month_list[i][2]		
	month_day=days-month_list[i][1]
	return str(year)+'-'+str(month)+'-'+str(month_day)

#Class for time slider. Organizes into days. 
#Contains methods to access lists of images for specific days.
class TimeSlider():

	def __init__(self, source, days, infoTup):
		self.source=source
		self.days=days
		self.maxDay=infoTup[1]
		self.minDay=infoTup[2]
		self.range=infoTup[3]
		self.day_index=0
		self.current_day=days[0][0]

	def getImage(self, i):
		index=i
		index=index%len(self.days[self.day_index][1])
		return self.source.getImage(self.days[self.day_index][1][index])
	def getEXIF(self, i):
		index=i
		index=index%len(self.days[self.day_index][1])
		return	self.source.getEXIF(self.days[self.day_index][1][index])

	def nextDay(self):
		self.day_index=self.day_index+1
		self.day_index=self.day_index%len(self.days)
		self.current_day=self.days[self.day_index][0]
	def previousDay(self):
		self.day_index=self.day_index-1
		self.day_index=self.day_index%len(self.days)
		self.current_day=self.days[self.day_index][0]
	def nextYear(self):
		next_year=self.current_day+365
		i=self.day_index
		day=self.current_day
		while day<next_year and i<len(self.days):
			i=i+1
			day=self.days[i][0]
		if day==next_year:
			self.current_day=next_year
			self.day_index=i

	def previousYear(self):
		last_year=self.current_day-365
		i=self.day_index
		day=self.current_day
		while day>last_year and i>0:
			i=i-1
			day=self.days[i][0]
		if day==next_year:
			self.current_day=last_year
			self.day_index=i
	
	def goToDay(self, yr, mn, dy):
		date_string=yr+'-'+mn+'-'+dy
		d=dateToDay(date_string)
		i=0
		for day in self.days:	
			if day[0]>d:
				print('date not found')
				break;
			if day[0]==d:
				self.current_day=day[0]
				self.day_index=i
				break;
			i=i+1
class DataList(object):

	def pushImages(self, num):
		i=self.index
		while i<num and i<self.source.total:
			self.imageList.append((self.source.getImage(i), self.source.getEXIF(i)))
			i=i+1

	def pushImageMeta(self, num):
		i=self.index
		while i<num and i<self.source.total:
			self.imageList.append(self.source.getEXIF(i))
			i=i+1

	def __init__(self, source):
		self.source=source
		self.type=type
		self.imageList=[]
		self.index=0
	def addImages(self, numAdded):
		self.index=self.numImages
		self.numImages=self.numImages+numAdded
	def getNext(self,i):
		self.index=self.index+i
		self.index=self.index%len(self.imageList)
		return (self.imageList[self.index])
	
	def isEmpty(self):
		return len(self.imageList)==0;
	def popImage(self):
		
		if len(self.imageList)>0:
			return self.imageList.pop()
			self.index=self.index+1
		else:
			print ('No cached images')
