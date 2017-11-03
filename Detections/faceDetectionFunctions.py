import numpy as np #cv uses this?
import cv2 #needed for image processing

#possible cascades to use to 
#had to use full file path or could not locate data
face_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_smile.xml')
full_body_cascade = cv2.CascadeClassifier('C:/opencv/sources/data/haarcascades/haarcascade_fullbody.xml')

#if any body is detected by the Haar cascade, returns 1
def detectBody(img):
    #assume image has been read in
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to gray for cascade
    #gray is the image, 1.3 is the scale factor (30%), minNeighbors)
    bodies = full_body_cascade.detectMultiScale(gray, 1.2, 5)
    if len(bodies) >= 1:
        return True
    else:
        return False

#if any face is detected by the Haar cascade, returns 1
def detectFace(img):
    #assume image has been read in
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to gray for cascade
    #gray is the image, 1.3 is the scale factor (30%), minNeighbors)
    faces = face_cascade.detectMultiScale(gray, 1.2, 3)
    if len(faces) >= 1:
        return True
    else:
        return False

def percentageFace(img):
    #get image size
    height, width, channels = img.shape
    imageSize = height * width
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to gray for cascade
    faces = face_cascade.detectMultiScale(gray, 1.2, 3)
    faceArea = 0
    for (x, y, w, h) in faces:
        faceArea += h*w
    return float(faceArea)/imageSize
        
def percentagePeople(img):
    #get image size
    imageHeight, imageWidth, channels = img.shape
    imageSize = imageHeight * imageWidth
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to gray for cascade
    faces = face_cascade.detectMultiScale(gray, 1.2, 3)
    bodies = full_body_cascade.detectMultiScale(gray, 1.1, 5)
    peopleArea = 0
    #get rectangular area for each component
    for (x, y, w, h) in faces:
        faceArea = h*w
        peopleArea += faceArea
    for (x, y, w, h) in bodies:
        bodyArea = h*w
        peopleArea += bodyArea
    percentagePeople = float(peopleArea)/imageSize * 100
    return percentagePeople

