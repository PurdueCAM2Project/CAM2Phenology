
import tkinter
from tkinter import *
from PIL import Image, ImageTk


class UrlIterator:

	images=[]
	
	url=''
	index=-1
	
	def download(self, url):
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
		self.index=self.index+1
		self.index=self.index%len(self.images)
		print(self.images[self.index])
		url=self.images[self.index]['url']
		self.download(url)
		im=Image.open('view.jpg')
		self.url=url
		return (im)
			
	def previous(self):
		self.index=self.index-1
		self.index=self.index%len(self.images)
		print(self.images[self.index])
		url=self.images[self.index]['url']
		self.download(url)
		im=Image.open('view.jpg')
		self.url=url
		return (im)
		
	def store(self):
		import storageUtil
		from storageUtil import storeImage
		id=self.images[self.index]['id']
		source=self.images[self.index]['source']
		storageUtil.storeImage(id, source)
		
	def horizonFunc(self):
		import storageUtil
		from storageUtil import horizonRequest
		id=self.images[self.index]['id']
		source=self.images[self.index]['source']
		storageUtil.horizonRequest(id, source)
	
iterator=UrlIterator()

def display():			
	root=tkinter.Tk()			

	def configureDisplay(im):
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
	canvas.grid(row=0, column=1, rowspan=15, columnspan=15)
	canvas.configure(background='blue')

	next=Button(root, text='Next', width=5, command=displayNext)
	previous=Button(root, text='Previous', width=5, command=displayPrevious)
	store=Button(root, text='Store Image', width=8, command=iterator.store)
	detectHorizon=Button(root, text='Horizon Detection', width=10, command=iterator.horizonFunc)
	
	next.grid(row=16, column=15)
	previous.grid(row=16, column=5)
	store.grid(row=16, column=10)
	detectHorizon.grid(row=17, column=10)
	
	root.mainloop()








	