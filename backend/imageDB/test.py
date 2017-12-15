import images
import imagedb
import os
import os.path
from PIL import Image
import imagehash
from imagedb import Dataset
import getpass
import time
import json
from imagedb import ImageDB
from ftplib import FTP
import sys

"""
Test file for image tagging database and file system (ImageDB). (In progress)
Tests can be used as example code.
Testing files:  db (database methods), images(file system methods), and imageDB(high level combination).
Runs 'functionalityTest()' when run as main.  

-Ehren Marschall 10/17/2017
"""


db_name="ImageDB"
#Testing should be done on this database (mostly). Alternatively, connect to 'ImageDB'
if(len(sys.argv)>1):
	db_name=sys.argv[1]
print("Using database "+str(db_name))
#NOTE: insert your own username
password=getpass.getpass("Using login info: "+imagedb.login_info+"\nPASSWORD: ")
idb=ImageDB('test user1', password, db_name=db_name) #Connecting to imageDB database and sftp server.

def download(url, path=''):
#unimportant download function
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
			
def functionalityTest():
	#Testing base functionality to ensure that scripts run on a new machine. 
	#Downloads 10 (temporary) images and checks their hash values
	
	data=idb.db.selectDataset('test1')
	for i in range(0, 10):
		im=idb.getImage(data[i]['id'])
		hash=imagehash.average_hash(im)
		if(str(hash)!=data[i]['imagehash']):
			print("ERROR: IMAGES DO NOT MATCH\nDatabase imagehash: "+str(data[i]['imagehash'])+"    Downloaded image imagehash: "+str(hash))
	print("Test Complete")
	
if __name__=="__main__":
	functionalityTest()

	
	
def uploadFolder(folder_name, dataset_name='test1'):
	#uploading images in specified folder to imageDB. Note: dataset_name must exist
	files=os.listdir(folder_name)
	for file in files:
		idb.addImage(folder_name+'/'+file, dataset_name=dataset_name)
	print('added '+str(len(files))+' files to imageDB(test)')
		
	
def uploadTagDelete(folder_name):
	#Testing upload, tag, select untagged, delete tag, and delete image functions
	
	#Adding images to imageDB and tagging them with tag 'delete test 1'
	local_files=os.listdir(folder_name)
	test_files=[]
	for i in range(0, 10):
		test_files.append(folder_name+local_files[i])
		print(str(test_files))
	idb.db.newTag('delete test 1') #creating tag 'delete test 1'
	idb.db.newTag('delete test 2')
	for file in test_files:
		id=idb.addImage(file, dataset_name='test2') #adding image
		idb.tagImage(id, 'delete test 1')			#tagging image
		
	#Selecting untagged images and tagging with 'delete test 2'
	untagged=idb.db.selectUntagged()
	for row in untagged:
		idb.tagImage(row['id'], 'delete test 2')
		
	#Selecting untagged images 
	untagged=idb.db.selectUntagged()
	print(str(untagged))
	
	#Selecting untagged images with respect to tag 'delete test 2'
	untagged=idb.db.selectUntagged(tag_name='delete test 2')
	print(str(untagged))
	t_id=idb.db.getTagID('delete test 2')
	#removing all images with tag 'delete test 2'
	idb.db.removeTagLink(tag_id=t_id)
	#reselecting. should be all images in dataset 'test2'
	untagged=idb.db.selectUntagged(dataset_name='test2', tag_name='delete test 2')
	print(str(untagged))
	#removing the selected images
	for row in untagged:
		idb.removeImage(row['id'])	
	no_images=idb.db.selectDataset('test2')
	print(str(no_images))


class FTPTransfer:
#Class used to transfer files from old FTP server to new SFTP server and Database.
#Useful test cases.  Only useful for grsm images at this point
	
	if not os.path.isfile('ftpContents.json'):
		content=False
		
	def makeFile():
		with open('ftpContents.json', 'w+') as file:
			data=[]
			json.dump(data, file)
		file.close()
		global content_flag
		content=True
		with open('ftpContents.json', 'r') as file:
			data=json.load(file)
			print(str(len(data))+" images' contents recorded")
		file.close()
		
	server_path='ftp://128.46.75.58'
	def download(url, path=''):
		import urllib.request
		from urllib.error import URLError, HTTPError
		i=0
		while i<5:
			#print(id)
			#print(url)
			i=i+1
			try:
				urllib.request.urlretrieve(url, path+'FTPtemp.jpg')
			except URLError as e:
				print('Url Error')
			except HTTPError as e:
				print('HTTP Error')
			else:
				return

	def dateFromGRSM(file_name):
		#retrieving date from grsm file name
		
		from datetime import datetime
		l=list(file_name)
		year=l[4]+l[5]+l[6]+l[7]
		month=l[8]+l[9]
		day=l[10]+l[11]
		hour=l[12]+l[13]
		minute=l[14]+l[15]
		stamp=year+'-'+month+'-'+day+' '+hour+':'+minute
		return datetime.strptime(stamp, "%Y-%m-%d %H:%M")
		
	def recordGRSM():
		#Logging grsm files
		ftp=FTP('128.46.75.58')
		ftp.login()
		years=ftp.nlst('/WD1/GRSM')
		meta=[]
		files_added=0
		for year in years:
			months=ftp.nlst('/'+year)
			print(year)
			for month in months:
				ftp.cwd('/'+month)
				print(month)
				files=ftp.nlst()
				for f in files:
					#date_taken=FTPTransfer.dateFromGRSM(f)
					meta.append(month+'/'+f)
					files_added+=1
		for i in range(0, 10):
			print(meta[i])
		print(str(files_added)+" files recorded")
		with open('ftpContents.json', 'w+') as file:
			json.dump(meta, file)
		file.close()
		ftp.close()
	
	def transferData(limit=None, files=None, data=None):
		#transferring grsm data to sftp server and imageDB database
		ftp=FTP('128.46.75.58')
		ftp.login()
		url="ftp://128.46.75.58"
		#idb.newDataset('GRSM')
		if data==None:
			with open('ftpContents.json', 'r') as file:
				data=json.load(file)
			file.close()
		if limit is None:
			limit=len(data)
		print('Adding '+str(limit)+' images to image database')
		for i in range(33800, limit):
			if (i%100==0):
				print(str(i)+" images added")
			path=data[i]
			#print(path.split('/')[6])
			date_taken=FTPTransfer.dateFromGRSM(path.split('/')[6])
			FTPTransfer.download(url+path)
			idb.addImage("FTPtemp.jpg", dataset_name="GRSM", image_dict={"date_taken": date_taken, 'source': 'NPS'}) #Good example of adding an image from a local file name
		ftp.close()
	
	
	

"""DEPRECATED: All code below this point can be ignored

print("\nImages added. Checking image integrity")
dataset=Dataset('test1')
while dataset.hasNext():
	data=dataset.getNext()
	hash=imagehash.average_hash(data[0])
	dbhash=data[1]['imagehash']
	if(str(hash)!=dbhash):
		message="\nIMAGES DO NOT MATCH!"
	else:
		message=" -Confirmed"
	print("Stored hash: "+str(hash)+" Database hash: "+str(dbhash)+message)
	
imagedb.db.newTag('test1', 'test')
print("\nNew tag created 'test1'")
print("\nTagging images with tag 'test1' and tag data {'test': 1}")
dataset=Dataset('test1')
while dataset.hasNext():
	print(dataset.getNext()[1])
	dataset.tag('test1', tag_data={'test': 1})

print("\nAdding 10 images into dataset test2")
while i<20:
	imagedb.addImage(images[i], 'test2', {})
	i+=1

imagedb.db.newTag('test2', 'test')
print("New tag created 'test2'")	
print("\nLoading and printing images in 'test2' without a tag (should be all 10), and tagging them with 'test2'")
dataset.loadUntagged({'dataset_name': 'test2'})
while dataset.hasNext():
	print(dataset.getNext()[1])
	dataset.tag('test2', tag_data={'test': 2})
	
print("test1 images have tag 'test1' and test2 images have tag test2")	
print("\nLoading and printing images without tag 'test2' and tagging them 'test2' (should be all images in dataset 'test1'")
dataset.loadUntagged({'tag_name': 'test2'})
while dataset.hasNext():
	print(dataset.getNext()[1])
	dataset.tag('test2', tag_data={'test': 2})
	
print("\nLoading and printing all images that haven't been tagged by 'test user2' (should be all 20)")
dataset.loadUntagged({'user_name': 'test user2'})
imagedb.db.user_id=imagedb.db.getUserID('test user2')
while dataset.hasNext():
	print(dataset.getNext()[1])
	dataset.tag('test1', tag_data={'test': 1})
	
print("\nLoading and printing all images that haven't been tagged by 'test user2' (should be none)")
dataset.loadUntagged({'user_name': 'test user2'})
while dataset.hasNext():
	print(dataset.getNext()[1])"""

	
	
"""BENCHMARKS.  
import random	
print("Creating 10 temporary test datasets")
imagedb.newDataset('test1')
imagedb.newDataset('test2')
imagedb.newDataset('test3')
imagedb.newDataset('test4')
imagedb.newDataset('test5')
imagedb.newDataset('test6')
imagedb.newDataset('test7')
imagedb.newDataset('test8')
imagedb.newDataset('test9')
imagedb.newDataset('test10')
dataset_list=['test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9', 'test10']
tag_list=[]

rand_list=[]
for i in range(0, 50000):
	rand_list.append(random.randint(0, 9))
print("Inserting 50000 randomized image rows")
start=time.time()
for element in rand_list:
	temp_dataset=dataset_list[element]
	imagedb.db.insertImageRow(temp_dataset, imagehash=None)
end=time.time()
total_time=end-start
print("Operation time: "+str(total_time)+" seconds")
print("Selecting all images in set 1")
start=time.time()
imagedb.db.selectDataset('test1')
end=time.time()
total_time=end-start
print("Operation time: "+str(total_time)+" seconds")
print("Selecting all images in set 5")
start=time.time()
imagedb.db.selectDataset('test5')
end=time.time()
total_time=end-start
print("Operation time: "+str(total_time)+" seconds")

letters='abcdefghijklmnopqrstuvwxyz'
print("Inserting 1000 random tags")
for i in range (0, 1000):
	random_letter=random.choice(letters)
	imagedb.db.newTag(random_letter+str(i), 'test')
	tag_list.append(random_letter+str(i))
tag_data={'test': 1}
print("Randomly inserting 100000 tag links over first 50000 images")
start=time.time()
for i in range(0, 100000):
	imagedb.tagImage(random.randint(1,49999), tag_list[random.randint(0, 999)], tag_data=tag_data)
end=time.time()
total_time=end-start
print("Operation time: "+str(total_time)+" seconds")
print("Selecting all images tagged with "+tag_list[0])
start=time.time()
imagedb.db.selectWithTag(tag_list[0])
end=time.time()
total_time=end-start
print("Operation time: "+str(total_time)+" seconds")"""








	
	






