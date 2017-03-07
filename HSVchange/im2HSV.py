import cv2
import numpy as np
import os

def cloudCheck(originalImage):
    skyImage = originalImage[0: originalImage.shape[0] / 2]  # get top half of image
    lower_range = np.array([0, 200, 200], dtype=np.uint8)
    upper_range = np.array([255, 255, 255], dtype=np.uint8)  # white
    whiteCheck = cv2.inRange(skyImage, lower_range, upper_range)
    lower_range = np.array([64, 64, 64], dtype=np.uint8)
    upper_range = np.array([192, 192, 192], dtype=np.uint8)  # gray
    grayCheck = cv2.inRange(skyImage, lower_range, upper_range)

    return cv2.sumElems(whiteCheck), cv2.sumElems(grayCheck)

def tierWrite(outputFile, gray, white, other):
    outputFile.write("Cloudy Images\n")
    for image in gray:
        outputFile.write(image)
        outputFile.write("\n")
    outputFile.write("\nBlue Sky Images\n")
    for image in white:
        outputFile.write(image)
        outputFile.write("\n")
    outputFile.write("\nUnknown\n")
    for image in other:
        outputFile.write(image)
        outputFile.write("\n")

def imageFeed(outputFile, filepath):
    sourceImages = os.listdir(filepath)
    cloudy, blueSky, other = [],[],[]
    for image in sourceImages:
        originalImage = cv2.imread(filepath + '\\' + image)
        whiteCheck, grayCheck = cloudCheck(originalImage)
        if grayCheck[0] >= 45000000:
            cloudy += [image]
        elif grayCheck[0] >= 10000000:
            blueSky += [image]
        else:
            other += [image]
    tierWrite(outputFile, cloudy, blueSky, other)
    return

if __name__ == "__main__":

    filepath = "C:\Users\Achinthya\Desktop\Projects\EXIFmodder\Bunion_Pics\Landscape"

    outputFile = open("tiers.txt", 'w')
    imageFeed(outputFile, filepath)
    outputFile.close()

    '''
    originalImage = cv2.imread("2016-6-4-51.jpg")
    skyImage = originalImage[0 : originalImage.shape[0]/2] #get top half of image
    lower_range = np.array([0, 200, 200], dtype=np.uint8)
    upper_range = np.array([255, 255, 255], dtype=np.uint8) #white
    whiteCheck = cv2.inRange(skyImage, lower_range, upper_range)
    #hsv = cv2.cvtColor(originalImage, cv2.COLOR_RGB2HSV)
    #lower_range = np.array([0, 0, 0], dtype=np.uint8)
    #upper_range = np.array([24, 255, 255], dtype=np.uint8)
    #mask = cv2.inRange(hsv, lower_range, upper_range)
    #cv2.imwrite("hsv2.jpg", hsv)
    #cv2.imwrite("mask2.jpg", mask)
    #cv2.imwrite("range3.jpg", rangecheck)
    print(cv2.sumElems(whiteCheck))
    lower_range = np.array([64, 64, 64], dtype=np.uint8)
    upper_range = np.array([192, 192, 192], dtype=np.uint8)  # gray
    grayCheck = cv2.inRange(skyImage, lower_range, upper_range)
    print(cv2.sumElems(grayCheck))
    cv2.imwrite("gray1.jpg", grayCheck) '''