import sys
import os
import cv2
import numpy as np
from skimage.morphology import binary_closing
from skimage import img_as_ubyte

def cloudCheck(pixel):
    if pixel[0] > 0 and pixel[1] > 200 and pixel[2] > 200:
        if pixel[0] < 255 and pixel[1] < 255 and pixel[2] < 255:
            return 0
    if pixel[0] > 64 and pixel[1] > 64 and pixel[2] > 64:
        if pixel[0] < 192 and pixel[1] < 192 and pixel[2] < 192:
            return 0
    return 1

def findHorizon(filepath):
    sourceImages = os.listdir(filepath)
    sourceImages.sort()
    for image in sourceImages:
        numMaskPixels = 0
        originalImage = cv2.imread(filepath + '\\' + image, 0) #load initial image in grayscale
        colorOriginal = cv2.imread(filepath + '\\' + image)
        #horizonf = open(originalImage + "line", "wb")
        edges = cv2.Canny(originalImage, 0, 80) #Detect edges
        #vx, vy, x, y = cv2.fitLine(np.argwhere(edges == 255), cv2.DIST_L2, 0, 0.01, 0.01)
        #rows, cols = edges.shape[:2]
        #lefty = int((-x * vy / vx) + y)
        #righty = int(((cols - x) * vy / vx) + y)
        #cv2.line(originalImage, (cols - 1, righty), (0, lefty), (0, 255, 255), 5)

        #horizon = cv2.HoughLinesP(edges, 1, np.pi/180, 100, originalImage.shape[1]/2, 500)
        #for x1, y1, x2, y2 in horizon[0]:
        #    cv2.line(edges, (x1, y1), (x2, y2), (0, 255, 0), 2)
        edges = binary_closing(edges) #Clean up edge lines
        edges = img_as_ubyte(edges)
        #edges = cv2.floodFill(edges, )
        #ret, edges = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY_INV)
        #print(np.argwhere(edges == 255))
        #cv2.imshow('edges', edges)
        #Find first white pixel in each column and set rest of column white
        for column in range(edges.shape[1]):
            whitePixels = np.where(edges[:,column] == 255)[0]
            if whitePixels.size is not 0:
                edges[whitePixels[0]:edges.shape[0]-1,column] = 255
                #numMaskPixels += range(edges.shape[0]) - range(whitePixels[0])
                #print(column)
                #print(whitePixels[0])
            #edges.itemset(edges[np.where(edges[:,column] == 255)[0]])
        mask = cv2.bitwise_not(edges) #Invert colors and create mask
        maskedGrayImage = cv2.bitwise_and(originalImage, mask)
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image', maskedGrayImage) #apply mask
        cv2.resizeWindow('image', 750, 1200)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        #print(numMaskPixels/(edges.shape[0] * edges.shape[1]))
        #horizonf.write("%.6f,%.6f,%.6f,%.6f\n" % (vx * 4, vy * 4, x0 * 4, y0 * 4))
if __name__ == "__main__":

    filepath = "C:\Users\Achinthya\Desktop\Projects\TextureAnalysis\Images"
    findHorizon(filepath)