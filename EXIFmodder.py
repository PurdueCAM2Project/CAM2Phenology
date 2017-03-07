import urllib.request
from PIL import Image
import piexif
import os.path

def getImage(url, filename):
    urllib.request.urlretrieve(url, filename)

def EXIFedit(url, date, location):
    urllib.request.urlretrieve(url, location + "temp.jpg")
    offset = 0
    '''zeroth_ifd = {piexif.ImageIFD.Make: u"Canon",
                  piexif.ImageIFD.XResolution: (96, 1),
                  piexif.ImageIFD.YResolution: (96, 1),
                  piexif.ImageIFD.Software: u"piexif"
                  }
    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u"2099:09:29 10:10:10",
                piexif.ExifIFD.LensMake: u"LensMake",
                piexif.ExifIFD.Sharpness: 65535,
                piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
                }
    gps_ifd = {piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
               piexif.GPSIFD.GPSAltitudeRef: 1,
               piexif.GPSIFD.GPSDateStamp: u"1999:99:99 99:99:99",
               }
    first_ifd = {piexif.ImageIFD.Make: u"Canon",
                 piexif.ImageIFD.XResolution: (40, 1),
                 piexif.ImageIFD.YResolution: (40, 1),
                 piexif.ImageIFD.Software: u"piexif"
                 }'''
    dateString = str(date[0]) + ":" + str(date[1]) + ":" + str(date[2])
    dateNameString = dateString.replace(":", "-")
    #print(dateString)
    #print(dateNameString)
    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: dateString}
    exif_bytes = piexif.dump({"Exif": exif_ifd})
    im = Image.open(location + "temp.jpg")
    while True:
        if not os.path.isfile(location + dateNameString + "-" + str(offset) + ".jpg"):
            im.save(location + dateNameString + "-" + str(offset) + ".jpg", exif=exif_bytes)
            break
        else:
            offset += 1 #allows for same day photos


if __name__ == "__main__":
    filename = "test.jpg"
    getImage("https://c2.staticflickr.com/8/7655/16740777466_9737965312_b.jpg", filename)
    EXIFedit(filename)
    image = Image.open('out.jpg', 'r')
    print(image._getexif())