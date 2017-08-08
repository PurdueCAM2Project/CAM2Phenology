from storageUtil import *
import urlViewer
from urlViewer import UrlIterator
import os
"""makeSearch(35.654, -83.52, 1)
commitSearch()"""

"""storeImage(23225707735, 'flickr')
storeImage(23225707735, 'flickr')"""

sample=dbManager.sampleImages()
urlViewer.iterator.images=sample

urlViewer.display()




