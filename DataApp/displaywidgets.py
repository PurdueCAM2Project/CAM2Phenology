#All graphical modules
import tkinter
from tkinter import *
from PIL import Image, ImageTk
import utility as util


#variables set to reference interface globals
images=[]
commands={}
variables={}

#entries and labels
entries={}
labels={}

#larger display widgets
displays={}


def getInput(arg_keys, disp):
	args=[]
	for key in arg_keys:
		arg=entries[key].get()
		if arg=="":
			variables[key]['value']=None
		else:
			variables[key]['value']=arg
		if(variables[key]['value']!=None):
			args.append(variables[key]['cast'](variables[key]['value']))
	return args

def executeCommand(command):
	args=getInput(commands[command]['arg_keys'])
	try:
		if commands[command]['printout']:
			print(str(commands[command]['function'](*args)))
		else:
			commands[command]['function'](*args)
	except Exception as e:
		print("Error: "+str(e))

def initialize():
	#initializing window and widgets
	root=tkinter.Tk()
	canvas=Canvas(root, width=960, height=540)
	canvas.configure(background='blue')
	displays['canvas']=canvas

	#creating entries and labels for all variables set by interface
	for var in variables.keys():
		entries[var]=Entry(root, bd=2, width=10)
		labels[var]=Label(root, text=str(var))
	
	close=Button(root, text="close", width=5, command=root.destroy)
	close.grid(row=0, column=0)
	return root

def configureDisplay(im):
	#displaying image <im>
	image=im.resize((960, 540), Image.ANTIALIAS)
	tkim=ImageTk.PhotoImage(image)
	displays['canvas'].image=tkim
	displays['canvas'].create_image(0, 0, image=displays['canvas'].image, anchor='nw')

class ImageViewer():
	
	def __init__(self, root=None, r=1, c=1):
		if(len(images)==0):
			print("No Images to display")
			return None
		mainloop_flag=False
		if root is None:
			root=initialize()
			mainloop_flag=True

		self.index=-1
		next=Button(root, text='Next', width=5, command=self.next)
		previous=Button(root, text='Previous', width=5, command=self.previous)
		self.date_taken_label=Label(root)
		self.gps_label=Label(root)
		self.source_label=Label(root)
		displays['canvas'].grid(row=r, column=c, rowspan=15, columnspan=15)
		next.grid(row=16+r, column=c+16)
		previous.grid(row=r+16, column=c+15)
		self.date_taken_label.grid(row=r+17, column=c+8)
		self.gps_label.grid(row=r+18, column=c+8)
		self.source_label.grid(row=r+19, column=c+8)
		if mainloop_flag:
			root.mainloop()
		
	def alterDisplay(self):
		metadata=images[self.index]
		im=util.getImage(metadata)
		self.date_taken_label.configure(text=str(metadata['date_taken']))
		self.gps_label.configure(text="Latitude: "+str(metadata['latitude'])+", Longitude: "+str(metadata['longitude']))
		self.source_label.configure(text=str(metadata['source']))
		configureDisplay(im)	

	def next(self):
		self.index+=1
		self.alterDisplay()
		
	def previous(self):
		self.index-=1
		self.alterDisplay()		
		
def displayAll():
	root.mainloop()

