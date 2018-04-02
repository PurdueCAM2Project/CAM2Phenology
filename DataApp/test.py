import interface
import core


print("ENTER PASSWORD")
core.login("YOURPASSWORDHERE")
vars=interface.variables

def testDownloadWithExif():
	#04/02/18
	#Downloading images and saving their exif data
	radius=.1/111
	vars['query string']['value']="SELECT * FROM images WHERE ST_WITHIN(images.gps, st_buffer(point(35.6583, -83.52), "+str(radius)+"))=1"
	vars['name_by_date']['value']="True"
	interface.executeCommand('ldq', True)
	print("Downloading "+str(len(interface.meta.image_list)))
	interface.executeCommand('di', True)
	
	print("test complete")
	
	
if __name__=="__main__":
	testDownloadWithExif()