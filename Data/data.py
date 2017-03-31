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

class DataList(object):

	def pushImages(self, num):
		i=self.index
		while i<num and i<self.source.total:
			self.imageList.append(self.source.getImage(i))
			i=i+1

	def pushImageMeta(self, num):
		i=self.index
		while i<num and i<self.source.total:
			self.imageList.append(self.source.getEXIF(i))
			i=i+1

	def __init__(self, source, bufferNum):
		self.source=source
		self.type=type
		self.imageList=[]
		self.index=0
	def getNext(self,i):
		self.index=self.index+i
		self.index=self.index%len(self.imageList)
		return self.imageList[self.index]
	
	def isEmpty(self):
		return len(self.imageList)==0;
		

	def popImage(self):
		
		if len(self.imageList)>0:
			return self.imageList.pop()
			self.index=self.index+1
		else:
			print ('No cached images')

def makeDataList(source, bufferNum, type):
	dataList=DataList(source, bufferNum)
	if type=='image':
		dataList.pushImages(bufferNum)
	else:
		dataList.pushImageMeta(bufferNum)
	return dataList
