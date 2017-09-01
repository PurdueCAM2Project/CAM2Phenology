
import tkinter
from tkinter import *
from PIL import Image, ImageTk
import storageUtil

class MetaIterator:
#Class used for iterating through, and performing functions on images based on their url and metadata
#This class has been used for two seperate UIs hence the messy imports
	images=[]	
	url=''
	index=-1
	marker=[0, 0, 'null']
	
	def download(self, url):
	#Used to temprarily save an image
		import urllib.request
		from urllib.error import URLError, HTTPError
		i=0
		while i<5:
			#print(id)
			#print(url)
			i=i+1
			try:
				urllib.request.urlretrieve(url, 'view.jpg')
			except URLError as e:
				print('Url Error')
			except HTTPError as e:
				print('HTTP Error')
			else:
				return
				
	def next(self):
		import storageUtil
		from storageUtil import addMarker
		self.index=self.index+1
		self.index=self.index%len(self.images)
		print(self.images[self.index])
		url=self.images[self.index]['url']
		self.download(url)
		im=Image.open('view.jpg')
		self.url=url
		self.marker[0]=self.images[self.index]['latitude']
		self.marker[1]=self.images[self.index]['longitude']
		self.marker[2]=str(self.images[self.index]['date_taken'])
		storageUtil.addMarker(self.marker)
		return (im)
			
	def previous(self):
		import storageUtil
		from storageUtil import addMarker
		self.index=self.index-1
		self.index=self.index%len(self.images)
		print(self.images[self.index])
		url=self.images[self.index]['url']
		self.download(url)
		im=Image.open('view.jpg')
		self.url=url
		self.marker[0]=self.images[self.index]['latitude']
		self.marker[1]=self.images[self.index]['longitude']
		self.marker[2]=str(self.images[self.index]['date_taken'])
		storageUtil.addMarker(self.marker)
		return (im)
		
	def store(self):
		import storageUtil
		from storageUtil import storeImage
		#storing jpeg file in storage prototype
		id=self.images[self.index]['id']
		source=self.images[self.index]['source']
		storageUtil.storeImage(id, source)
		
	def horizonFunc(self): #calling the horizon detection function
		import storageUtil
		from storageUtil import horizonRequest
		id=self.images[self.index]['id']
		source=self.images[self.index]['source']
		storageUtil.horizonRequest(id, source) #sending horizon detection request to ImageStorage
	
	def noteImage(self, note): #inserting a note into database
		import dbManager
		id=self.images[self.index]['id']
		source=self.images[self.index]['source']
		dbManager.insertImageNote(id, source, note)
	
	
	

def display(iterator, root=None, sub_window=False, row_offset=0, column_offset=0 ):						
#Class used to display images from url viewer
#this can be launched independently as well as in another window (default is independent)

	if root is None:
		root=tkinter.Tk()
		
	def configureDisplay(im):
		#displaying image based on current image in the iterator
		image=im.resize((960, 540), Image.ANTIALIAS)
		tkim=ImageTk.PhotoImage(image)
		canvas.image=tkim
		canvas.create_image(0, 0, image=canvas.image, anchor='nw')
		
	def displayNext():
		im=iterator.next()
		configureDisplay(im)
		
	def displayPrevious():
		im=iterator.previous()
		configureDisplay(im)
	
		
	
	canvas=Canvas(root, width=960, height=540)

	canvas.configure(background='blue')
	
	note_entry=Text(root, width=50, height=20)
	
	next=Button(root, text='Next', width=5, command=displayNext)
	previous=Button(root, text='Previous', width=5, command=displayPrevious)
	store=Button(root, text='Store Image', width=8, command=iterator.store)
	detectHorizon=Button(root, text='Horizon Detection', width=10, command=iterator.horizonFunc)
	add_note=Button(root, text='Add Note', width=10, command= lambda : iterator.noteImage(note_entry.get('1.0', '500.0')))
	
	canvas.grid(row=0+row_offset, column=1+column_offset, rowspan=15, columnspan=15)
	next.grid(row=16+row_offset, column=15+column_offset)
	previous.grid(row=16+row_offset, column=5+column_offset)
	store.grid(row=16+row_offset, column=10+column_offset)
	detectHorizon.grid(row=17+row_offset, column=10+column_offset)
	note_entry.grid(row=18+row_offset, column=10+column_offset)
	add_note.grid(row=18, column=11+column_offset)
	
	if not sub_window:
		root.mainloop()








	