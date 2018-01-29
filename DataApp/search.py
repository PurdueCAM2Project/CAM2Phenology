#master search class.  Inherits all API query functions.

import flickrsearch
import apirequest
import time
import json

apis={'flickr': flickrsearch} #api modules

def search(params):
	#Using API services to search a given area
	#params={paramname: param, ...}

	#params={'lat': <latitude>, 'lon': <longitude>, 'radius': <radius>}
	ids={}
	for api in apis.keys():
		ids[api]=apis[api].searchIds(params)
	return ids

def compileData(ids):
	#compiling metadata for given ids. ids={<api>: [ids], ...}
	#Returning array of images' metadata ready to be committed to database
	data=[] 
	for api in ids.keys():
		for id in ids[api]:
			data.append(apis[api].processID(id))
			#print(str(data[-1]))
	return data
	
def compileData_thread(ids, numthreads=4):
	#Using multiple threads to compile metadata.
	#Significantly faster than single thread version
	from multiprocessing import Process, Queue
	def thread(inputq, resultq):
		while not inputq.empty():
			id=inputq.get()
			resultq.put(apis[id[0]].processID(id[1]))
	inputq=Queue()
	resultq=Queue()
	for api in ids.keys():
		for id in ids[api]:
			inputq.put((api, id)) #(source, id) Example: ('flickr', 21323243)
	processes=[]
	for i in range(0, numthreads):
		p=Process(target=thread, args=(inputq, resultq,))
		processes.append(p)
		p.start()
	while not inputq.empty():
		time.sleep(5)
		print(str(inputq.qsize()))
	time.sleep(5)
	for p in processes:
		p.terminate()
	print('t')
	data=[]
	while not resultq.empty():
		data.append(resultq.get())
	return data

		
	
	
if __name__=='__main__':
	ids=search({'lat': 35.6582, 'lon': -83.52, 'radius': 1})
	print(str(len(ids)))
	t1=time.time()
	data=compileData_thread(ids)
	print(str(len(data)))
	print(str(time.time()-t1))
	with open('testdata.json', 'w+') as file:
		json.dumps(data, file)
	file.close()
	"""t1=time.time()
	data=compileData(ids)
	print(str(len(data)))
	print(str(time.time()-t1))"""