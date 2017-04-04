import tkinter
from tkinter import *
from PIL import Image, ImageTk
import frontEnd
from frontEnd import *
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


root=tkinter.Tk()
f = Figure(figsize=(4, 3), dpi=70)
a=f.add_subplot(111)
pltCanvas = FigureCanvasTkAgg(f, master=root)
pltCanvas.get_tk_widget().grid(row=0, column=22)
pltCanvas._tkcanvas.grid(row=0, column=22)

# a tk.DrawingArea
plotFlag=0
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

def plot():
	plotAllPoints(sourceVar.get(), a)
	pltCanvas.show()	
def configureDisplay(image):
	addPoint(sourceVar.get(), a)	
	pltCanvas.show()
	image=image.resize((960, 540), Image.ANTIALIAS)
	im=ImageTk.PhotoImage(image)
	canvas.image=im
	canvas.create_image(0, 0, image=canvas.image, anchor='nw')

def next():
	imageTup=frontEnd.dataDict[sourceVar.get()].getNext(1)
	configureDisplay(imageTup[0])
def previous():
	imageTup=frontEnd.dataDict[sourceVar.get()].getNext(-1)
	configureDisplay(imageTup[0])
def updateDisplay(source):
	print(source)
	initialPlot(sourceVar.get(), a)
	imageTup=frontEnd.dataDict[sourceVar.get()].getNext(0)
	configureDisplay(imageTup[0])
	location=getGPS(imageTup[1])
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
next=Button(root, text='>>>', width=5, command=next)
pre=Button(root, text='<<<', width=5, command=previous)
plot=Button(root, text='Plot Geo', width=5, command=plot)
plot.grid(row=16, column=18)
next.grid(row=16, column=19)
pre.grid(row=16, column=5)
root.mainloop()
