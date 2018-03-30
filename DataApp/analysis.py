#Analysis functions

import random

def eucDist(p1, p2):
	#returning euclidean distance between points p1 and p2
	return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**.5
	
def avgPoint(points):
	#getting average point in set of points
	if len(points)==0:
		return 0
	avgx=0
	avgy=0
	for p in points:
		avgx=avgx+p[0]
		avgy=avgy+p[1]
	return (avgx/len(points), avgy/len(points))
	
def maxAvgDist(center, points):
	#calculating the maximum distance of a point in points to center. (radius) as well as the average distance of all points to center
	if len(points)==0:
		return 0, 0
	max_dist=0
	avgdist=0
	for p in points:
		dist=eucDist(p, center)
		avgdist=avgdist+dist
		if dist>max_dist:
			max_dist=dist
	return avgdist/len(points), max_dist
	
def kMeansCluster(k, points):
	#clustering <points> into k cluster centroids.  
	#k needs to be determined on a case-by-case basis.  Another algorithm is needed to determine k
	
	#randomly initializing centroids
	if k==1:
		avgdist, maxdist=maxAvgDist(avgPoint(points), points)
		return [[avgPoint(points), maxdist, points]]
	centroids=[]
	for i in range(0, k):
		centroids.append([0, 0, []])
	for i in range(0, len(points)):
		p=points[i]
		if i<len(centroids):
			centroid=centroids[i]
		else:
			centroid=centroids[random.randint(0, k-1)]
		centroid[2].append(p)
	wcd=0 #within cluster distance (average)
	pwcd=10000000000 #previous within cluster distance
	for centroid in centroids:
		centroid[0]=avgPoint(centroid[2])
		avgdist, maxdist=maxAvgDist(centroid[0], centroid[2])
		centroid[1]=maxdist
		wcd=wcd+(avgdist)**2
	wcd=wcd/len(centroids)	
	while (pwcd-wcd)>.1:  #while the wcd is converging, put points into appropriate cluster centroid and recalculate means, wcd, and pwcd.
		#print(str(centroids))
		pwcd=wcd
		wcd=0
		for c in centroids: #clearing centroid points
			del c[2][:]
		for p in points:    #reassigning points to centroids
			mindist=100000000000
			minindex=0
			for i in range(0, len(centroids)):
				dist=eucDist(centroids[i][0], p)
				if dist<mindist:
					mindist=dist
					minindex=i
			centroids[minindex][2].append(p)
		for centroid in centroids:
			centroid[0]=avgPoint(centroid[2])
			avgdist, maxdist=maxAvgDist(centroid[0], centroid[2])
			centroid[1]=maxdist
			wcd=wcd+avgdist**2
		wcd=wcd/len(centroids)
		
	return centroids
		
	
	
#print(str(kMeansCluster(4, [(1, 2), (5, 7), (10, 11), (15, 16)])))

def clusterUserDays(query_result):
	#clustering the first and last photos that users take on a given day
	#This is to show (in theory) where people enter a park and where they leave, or stop taking photos.
	#see database.getUserDayOrderByTime to see how <query_result> is formatted
	
	start_clusters=[]
	end_clusters=[]
	start_data=[]
	end_data=[]
	userid=None
	date=None
	previous=None
	start=True
	start_data.append((query_result[0]['latitude'], query_result[0]['longitude']))
	userid=query_result[0]['userid']
	date=query_result[0]['date']
	for row in query_result:
		if row['userid']!=userid or row['date']!=date:
			end_data.append(previous)
			start_data.append((row['latitude'], row['longitude']))
			userid=row['userid']
			date=row['date']
		previous=(row['latitude'], row['longitude'])
	end_data.append(previous)
	print(str(len(start_data)))
	print(str(len(end_data)))
	
	start_clusters=kMeansCluster(1, start_data)
	end_clusters=kMeansCluster(1, end_data)
	return start_clusters, end_clusters