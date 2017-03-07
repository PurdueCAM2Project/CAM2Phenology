from bs4 import BeautifulSoup
import urllib.request
import re

def htmlParse(url):

    monthDict = {'January': 1,
                 'February': 2,
                 'March': 3,
                 'April': 4,
                 'May': 5,
                 'June': 6,
                 'July': 7,
                 'August': 8,
                 'September': 9,
                 'October': 10,
                 'November': 11,
                 'December': 12,
                 }

    html = urllib.request.urlopen(url)
    html = html.read()
    #doc = open('test.txt', 'wb')
    #doc.write(html)
    soup = BeautifulSoup(html, 'html.parser')
    imageLink = soup.find("meta", property="og:image")
    date = soup.find("span", class_ = "date-taken-label")
    #print(imageLink['content'])
    #print(str(date.contents[0]))
    dateString = r'Taken on (\w+) (\d+), (\d+)\n\t\t'
    date = re.search(dateString, str(date.contents[0]))
    #print (monthDict[date.group(1)])
    if date is not None:
        return [imageLink['content'], [date.group(3), monthDict[date.group(1)], date.group(2)]] #return url to image and date in [year, month, day] format
    return None


if __name__ == "__main__":
    url = "https://www.flickr.com/photos/rebekahnewton/29446013094/"
    print(htmlParse(url))

