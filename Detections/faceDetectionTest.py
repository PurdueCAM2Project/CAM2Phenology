from time import time #use to test how long the runtime is

startTime = time()

import numpy as np #cv uses this?
import cv2 #needed for image processing
from os import listdir
from os.path import isfile, join
from faceDetectionFunctions import *


#specified file path to grab images from
mypath = 'C:/Python27/babysteps/web_iu_test'

#grabs all files in a specified file path (2 lines above)
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

'''#possible cascades to use to 
#had to use full file path or could not locate data
face_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_smile.xml')
full_body_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_fullbody.xml')'''

namesAndPercentages = {};

for filename1 in onlyfiles:
    filename = mypath+'/'+filename1
    #read in the image
    img = cv2.imread(filename)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    percentage = 0
    haveFaceBool = detectFace(img)
    if (haveFaceBool == True):
        percentage = percentageFace(img)
    #print filename + ': %.4f' % percentage
    namesAndPercentages[filename[12:-4]] = percentage
           

#print namesAndPercentages
cv2.destroyAllWindows()

runtimeSeconds = time() - startTime
runtimeMinutes = runtimeSeconds/60
print "runtime in seconds " + ': %.4f' % runtimeSeconds
print "runtime in minutes " + ': %.4f' % runtimeMinutes
