import tkinter
from tkinter import *
from PIL import Image, ImageTk
import frontEnd
from frontEnd import *

root=tkinter.Tk()
sourceVar=StringVar(root)
dataVar=StringVar(root)

def imp():
	import frontEnd, data, sources

#Image Canvas+management(under image) 
canvas=Canvas(root, width=960, height=540)
canvas.grid(row=0, column=5, rowspan=15, columnspan=15)
canvas.configure(background='blue')

#Left management widgets
L1=Label(root, text='management here')
L1.grid(row=7, column=0, sticky='n')
bufferEntry=Entry(root, bd=5)
bufferEntry.grid(row=10, column=0)
localData=os.listdir('data')

def configureDisplay(image):
	image=image.resize((960, 540), Image.ANTIALIAS)
	im=ImageTk.PhotoImage(image)
	canvas.image=im
	canvas.create_image(0, 0, image=canvas.image, anchor='nw')

def next():
	configureDisplay(frontEnd.dataDict[sourceVar.get()].getNext(1))

def previous():
	configureDisplay(frontEnd.dataDict[sourceVar.get()].getNext(-1))

def updateDisplay(source):
	print(source)
	configureDisplay(frontEnd.dataDict[sourceVar.get()].getNext(0))
	sourceMenu()

def sourceMenu():
	menu=OptionMenu(root, sourceVar, *list(frontEnd.dataDict.keys()), command=updateDisplay)
	menu.grid(row=16, column=13)

def newLocal(source):
	frontEnd.newLocalStorage(dataVar.get(), bufferEntry.get())
	sourceVar.set(dataVar.get())
	updateDisplay(dataVar.get())

dataMenu=OptionMenu(root, dataVar, *frontEnd.localData, command=newLocal)
dataMenu.grid(row=8, column=0)
next=Button(root, text='>>>', width=5, command=previous)
pre=Button(root, text='<<<', width=5, command=next)
next.grid(row=16, column=19)
pre.grid(row=16, column=5)
root.mainloop()
