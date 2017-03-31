from data import *
import sources
from sources import *
import os
import os.path

def display():
	import display
#important variables
dataDict={}

if not os.path.isfile('preferences.txt'):
	with open('preferences.txt', 'w+') as file:
		file.write('data/')
with open('preferences.txt') as file:
	preferences=file.read().splitlines()
dir=preferences[0]
if not os.path.exists(dir):
	os.makedirs(dir)
localData=os.listdir(dir)
localData.append(' ')
def changeStorage(newDir):
	with open('preferences.txt','w+') as file:
		preferences[0]=newDir+'/'
		file.writelines(preferences)
		dir=newDir+'/'
def newLocalStorage(directory, buffer):
	import copy
	print(dir+directory)
	source=sources.makeLocalStorage(dir+directory+'/')
	newList=makeDataList(copy.copy(source), int(buffer), 'image')
	dataDict[directory]=copy.copy(newList)


def showGeo(source):
	from analysis import plotGeo
	plotGeo(source)

source=sources.makeLocalStorage(dir+'CCLargeGeo'+'/')
showGeo(source)	
#import display
