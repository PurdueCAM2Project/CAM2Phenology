import db
import imagedb
import os
import images
from imagedb import Dataset

images.buildFileTree(10000)
db.newTag('test')
ids=os.listdir('web_ui_test')
folder='web_ui_test/'
images= [folder + image for image in ids]
db.insertDatasetRow('test')

i=0
while i<10:
	imagedb.addImage(images[i], 'test', {})
	i+=1

dataset=Dataset('test')
while dataset.hasNext():
	print(dataset.getNext()[1])
	dataset.tag('test', tag_data={'test': 1})





