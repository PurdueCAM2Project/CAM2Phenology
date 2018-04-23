import interface
import core


print("ENTER PASSWORD")
password="PASSWORD"
core.login(password)
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
	#Passed 04/02/18
	
def testAddSearchTag():
	vars['tagname']['value']="TESTTAG"
	print("Inserting search tag 'TESTTAG'")
	interface.executeCommand('ast', True)
	
def testSearchTagSearch():
	vars['tagname']['value']="Carlos C Campbell Overlook"
	interface.executeCommand('sts', True)
	print("Tag 'Carlos C Campbell Overlook' searched for.")
	
def testLocationSearch():
	vars['latitude']['value']=35.6583
	vars['longitude']['value']=-83.52
	vars['radius']['value']=1
	interface.executeCommand('ls', True)
	print("Location searched for")
	
	
def testLastInsertIDThread():
	#Testing that the sql maintains the proper last_insert_id relative to the process
	
	from multiprocessing import Process, Queue
	#core.db.query("create table last_insert_test(id bigint not null primary key auto_increment, value bigint);")

	def thr1(q):
		core.db.query("insert into last_insert_test (value) values (0)")
		while True:
			if not q.empty():
				other_last_insert=q.get()
				result=core.db.query("Select last_insert_id() as test")[0]['test']
				print("This threads last_insert_id: "+str(result)+" Alternate process last_insert_id: "+str(other_last_insert))
				break
	q=Queue()
	proc=Process(target=thr1, args=(q,))
	proc.start()
	core.db.query("insert into last_insert_test (value) values(1)")
	result=core.db.query("select last_insert_id() as test")[0]['test']
	print(str(result))
	q.put(result)
	proc.join()
	core.db.query("drop table last_insert_test")
	

	

	
	
if __name__=="__main__":
	#testDownloadWithExif()
	#testAddSearchTag()
	testLocationSearch()
	testSearchTagSearch()
	#testLastInsertIDThread()