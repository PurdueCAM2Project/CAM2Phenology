import json
import urllib.request
import htmlParser
import EXIFmodder

def search(searchString, numberImages, location):
    #print("Enter search query types and parameters.  Type 'done' to exit")
    pages = 0
    photos = getPageUrl(searchString, 0)
    '''search_type = input('Enter next search type ')

    while search_type != 'done':
        parameter = input("Enter parameters: ")
        parameter = parameter.replace(" ", "%20")
        parameter = parameter.replace(',', '%C')
        url += '&' + search_type + '=' + parameter
        search_type = input('Enter next search type ')'''


    '''print(url)
    response = urllib.request.urlopen(url)
    response = response.read()
    testtext = open("test.txt", 'w')
    testtext.write(response.decode())
    testtext.close()
    data = json.loads(response.decode())
    #print(data)
    photos = data['photos']'''
    #print(data['photos']['total'])
    #yn=input("Pull next photo? (y/n) ")
    #while yn is 'y':
    #linklist = open('linklist.txt', 'w')
    for j in range(numberImages):
        if not j % 500 and j is not 0:
            pages += 1 #go to next page if j has exhausted the page
            photos = getPageUrl(searchString, pages)
        id = photos['photo'][j - (pages * 500)]['id']
        #print(id)
        url2 = 'https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9&photo_id=' + id + '&format=json&nojsoncallback=1'
        #print(url2)
        photo_response = urllib.request.urlopen(url2)
        photo_response = photo_response.read()
        data2 = json.loads(photo_response.decode())
        urls = data2['photo']['urls']
        #linklist.write(urls['url'][0]['_content'] + '\n')
        print(urls['url'][0]['_content'])
        print(htmlParser.htmlParse(urls['url'][0]['_content']))
        picInfo = htmlParser.htmlParse(urls['url'][0]['_content'])
        if picInfo is not None:
            EXIFmodder.EXIFedit(picInfo[0], picInfo[1], location)
        #yn = input("Pull next photo? (y/n) ")

def getPageUrl(searchString, page):
    url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=0fb2ef4f2a015b331d5cbab58f7f05e9'
    url += searchString + '&page=' + str(page + 1) + '&format=json&nojsoncallback=1'
    response = urllib.request.urlopen(url)
    response = response.read()
    data = json.loads(response.decode())
    # print(data)
    photos = data['photos']
    print(url)
    return photos
if __name__ == "__main__":
    pass
    #search()