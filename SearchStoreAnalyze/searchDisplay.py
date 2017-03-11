#This is the UI to search, compile (make package), and rate images.  Using a search.py search() class to search and to interact with image packages (phenImage.py searchPackage())
#Currently only compatible with flickr API search
#Global Phenology: Ehren Marschall, updated 3/7/17
import tkinter  #Tkinter framework.  
from tkinter import *
#thoroughly uses phenImage.py and search.py
import search
from search import *
from PIL import Image, ImageTk
from phenImage import searchPackage
import matplotlib

images=searchPackage()
dir='packages/'
addedTypes=[]
addedParameters=[]
top=tkinter.Tk()
flickr=Search()			
entries=[]
entrytypes=['&tag=', '&text=', '&lat=', '&lon=', '&radius=', '&per_page=', '&page=']  #formatted for flickr.photos.search
imagenum=0
rating=[0, 0, 0, 0]			
L1=Label(top, text='Tag Search(cannot be used alone)').grid(row=0)
L2=Label(top, text='Text Search').grid(row=1)
L3=Label(top, text='Latitude').grid(row=2)
L4=Label(top, text='Longitude').grid(row=3)
L5=Label(top, text='Radius').grid(row=4)
L6=Label(top, text='per_page').grid(row=5)
L7=Label(top, text='page').grid(row=6)
L8=Label(top, text='Custom Flickr Search Type').grid(row=8)
L9=Label(top, text='Custom Parameter').grid(row=9)

#Below are entries and labels used for searching Flickr
E1 = Entry(top, text='enter tags?', bd =5)
E2 = Entry(top, bd =5)
E3 = Entry(top, bd =5)
E4 = Entry(top, bd =5)	
E5 = Entry(top, bd =5)
E6 = Entry(top, bd =5)
E7 = Entry(top, bd =5)
E8 = Entry(top, bd =5)
E9 = Entry(top, bd =5)
E10 = Entry(top, bd =5)
E1.grid(row=0, column=1)
E2.grid(row=1, column=1)
E3.grid(row=2, column=1)
E4.grid(row=3, column=1)
E5.grid(row=4, column=1)
E6.grid(row=5, column=1)
E7.grid(row=6, column=1)
E8.grid(row=8, column=1)
E9.grid(row=9, column=1)
E10.grid(row=10, column=0)
panel=Label(top)
panel.grid(row=1, column=5, columnspan=25, rowspan=25, padx=10, pady=10, sticky=W+E+N+S)
entries=[E1, E2, E3, E4, E5, E6, E7]
packageInfoLabel=Label(top)
packageInfoLabel.grid(row=27, column=17, columnspan=14, rowspan=2)
#Below are a set of methods used for rating through drop down menus.
#The Ratings are put into an array and then passed into flickr.package for rating with the 'Rate' button.  Ratings updated in packages/<packagename>/<packagename>.json
def setQual(q):
	rating[0]=q
lQuality=Label(top, text='Quality').grid(row=26, column=5, sticky=W+E)
quality= IntVar(top)
quality.set(0)
oQuality= OptionMenu(top, quality, 1, 2, 3, command=setQual)
oQuality.grid(row=27, column=5, sticky=W+E)
def setScene(s):
	rating[1]=s
lScene=Label(top, text='Scene').grid(row=26, column=6, sticky=W+E)
scene = IntVar(top)
scene.set(0)
oScene= OptionMenu(top, scene, 1, 2, 3, command=setScene)
oScene.grid(row=27, column=6, sticky=W+E)
def setScale(sc):
	rating[2]=sc
lScale=Label(top, text='Scale').grid(row=26, column=7, sticky=W+E)
scale= IntVar(top)
scale.set(0)
oScale= OptionMenu(top, scale, 1, 2, 3, command=setScale)
oScale.grid(row=27, column=7, sticky=W+E)
def setCov(cov):
	rating[3]=cov
lCoverage=Label(top, text='Coverage').grid(row=26, column=8, sticky=W+E)
coverage= IntVar(top)
coverage.set(0)
oCoverage= OptionMenu(top, coverage, 1, 2, 3, command=setCov)
oCoverage.grid(row=27, column=8, sticky=W+E)

#Below method used to display images from flickr.package 
def displayImage(i):
	imageTup=images.getImage(i)
	imageDict=imageTup[1]
	img=imageTup[0]
	img=img.resize((960, 540), Image.ANTIALIAS)
	im=ImageTk.PhotoImage(img)
	panel.configure(image=im)
	panel.image=im
	unrated=images.data['Total']-images.data['Rated']
	rateStatus='More rating needed to analyze'
	if unrated<5:
		rateStatus='Ready to Analyze'
	packageInfoLabel.configure(text='Package: '+images.data['Name']+'Package Rating: '+str(images.data['Overall Rating'])+'\nPhoto Date: '+imageDict['DateTaken']+'\nUnrated: '+str(unrated)+' '+rateStatus)
	packageInfoLabel.text='Package: '+images.data['Name']+'Package Rating: '+str(images.data['Overall Rating'])+'\nPhoto Date: '+imageDict['DateTaken']
"""	
def pull(): #pulls and displays next image info.. Takes images in order of flickr.ids. only accesses cached search
	jsonString=flickr.pull()
	imageInfo.insert(END, jsonString)
"""
def rate():
	images.rate(rating[0], rating[1], rating[2], rating[3])

#next and previous to set which image will be displayed from package	
def next():
	displayImage(1)
def previous():
	displayImage(-1)
#add not specified parameter
def add():
	global addedTypes
	global addedParameters
	if E9.get() != "" and E8.get() != '' :
		
		addedTypes.append('&'+E8.get())
		addedParameters.append('='+E9.get())
def search(): #Search takes parameters from entries and matches them to their types.  Information passed into search.py
	global addedTypes
	global addedParameters
	dtypes=[]
	dparameters=[]
	i=0
	while i<7:
		if entries[i].get() != '':
			dparameters.append(entries[i].get())	
			dtypes.append(entrytypes[i])
		i=i+1
	dtypes.extend(addedTypes)
	dparameters.extend(addedParameters)
	flickr.search(dtypes, dparameters)
	del addedTypes[:]
	del addedParameters[:]
def setDir():
	global dir
	dir=E10.get()	
def getPackage():
	top2=Toplevel()
	flickr.packageCreator(dir, images, top2)
	top2.wait_window()
	displayImage(0)
def geoAnalyze():
	import analysis
	from analysis import modGeo
	if images.data['Rated']<(images.data['Total']-5):
		print( "Rate more images before analyzing")
	else:
		images.writedata()
		modGeo(images, dir)
		name=images.packageName+'I'
		images.open(name, dir)

def exit():
	import sys
	sys.exit()

#Module buttons  
b=Button(top, text="SEARCH", width=10, command=search)
b1=Button(top, text="clear photos", width=10, command=flickr.clear)
#b2=Button(top, text="Show Next", width=10, command=flickr.pull)
b3=Button(top, text="Exit Program", width=10, command=exit)
b4=Button(top, text="Add", width=10, command=add)
b6=Button(top, text='> >', width=8, command=next)  #Display next photo from imported search package.  Will through error if flickr.package is null
b7=Button(top, text='< <', width=8, command=previous) #Previous image ^
b8=Button(top, text='Rate!', width=10, command=rate)
B9=Button(top, text='Save', width=10, command=images.writedata)
b10=Button(top, text='SetDirectory(careful)', width=15, command=setDir)
b11=Button(top, text='geoAnalyze', width=10, command=geoAnalyze)
creator=Button(top, text='package creator', width=10, command=getPackage)  #launches packageCreator in search.py to create or import package
b.grid(row=0, column=2)
b1.grid(row=1, column=2)
#b2.grid(row=11, column=0)
b11.grid(row=27, column=13)

b3.grid(row=27, column=15)
b4.grid(row=8, column=2)
b6.grid(row=0, column=29, columnspan=1, rowspan=1, padx=2, pady=2, sticky=N+S)
b7.grid(row=0, column=5, columnspan=1, rowspan=1, padx=2, pady=2, sticky=N+S)
b8.grid(column=9, row=27)
B9.grid(column=11, row=27)
b10.grid(row=10, column=1)
creator.grid(row=10, column=2)
top.mainloop()
