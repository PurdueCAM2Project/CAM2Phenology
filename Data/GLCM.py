from skimage.feature import greycomatrix, greycoprops
from skimage import data
import os
import cv2

def imageFeed(outputFile, filepath):
    sourceImages = os.listdir(filepath)
    cloudy, blueSky, other = [],[],[]
    for image in sourceImages:
        originalImage = cv2.imread(filepath + '\\' + image, 0)
        skyImage = originalImage[0: originalImage.shape[0] / 2]  # get top half of image
        #print(skyImage.shape)
        glcm = greycomatrix(skyImage, [5], [1, 2], 256)
        print(greycoprops(glcm,prop = 'dissimilarity'))
"""filepath = "\home\emars\home\PhenologyGit\Data\Images"
outputFile = open("tiers.txt", 'w')
imageFeed(outputFile, filepath)
outputFile.close()"""

#Overall plan:
#Use homogeneity to see how uniform sky region is
#Mean glcm value to have cloud/sky color threshold
