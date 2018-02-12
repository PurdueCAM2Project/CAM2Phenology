#Threads to send API queries and retrieve data

from multiprocessing import Process, Queue
from urllib.error import URLError, HTTPError
import urllib.request
			
request_queue=Queue()
return_queue=Queue()

def getRequest(url):
	i=0
	while i<5:
		i=i+1
		try:
			response=urllib.request.urlopen(url)
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		except Exception as e:
			print(e.message)
		else:
			response=response.read()
			return response
			
def processRequests(request_queue, return_queue):
	while not request_queue.empty():
		request=request_queue.get()
		for key in request[2].keys():
			response=getRequest(request[2][key])
			request[2][key]=response
		return_queue.put(request)
	print('thread closed')	
	
processes=[Process(target=processRequests, args=(request_queue, return_queue, )),
			Process(target=processRequests, args=(request_queue, return_queue, )),
			Process(target=processRequests, args=(request_queue, return_queue, )),
			Process(target=processRequests, args=(request_queue, return_queue, ))]
			
def collectData(requests, numthreads=2):
	#requests=[(source, id, {datakey1: url, datakey2: url, ...}), ...]
	for request in requests:
		request_queue.put(request)
	for i in range(0, numthreads):
		processes[i].start()
	return return_queue
	
def isFinished():
	if processes[0].is_alive() or processes[0].is_alive() or processes[0].is_alive() or processes[0].isalive():
		return False
	print('Finished')
	return True
	
	

	