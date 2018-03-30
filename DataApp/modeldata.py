#functions to create graphical models of data



def plotGoogleMap(coordinate_groups=[], circles=[], center=None, circle_groups=[], polygon_groups=[], marker_groups=[], plot_name='temp.html'):
	#Plotting data on google map
	import gmplot
	import gmplot.color_dicts
	import random
	
	colors=['k']
	colors.extend(list(gmplot.color_dicts.html_color_codes.keys()))
	#colors.remove('r')
	#colors.remove('g')
	if center is None:
		avglat=0;
		avglong=0
		total=0
		for group in polygon_groups:
			for coord in group:
				avglat+=coord[0]
				avglong+=coord[1]
				total+=1
		for group in coordinate_groups:
			for coord in group:
				avglat+=coord[0]
				avglong+=coord[1]
				total+=1
		for circle_group in circle_groups:
			for circle in circle_group:
				#print(str(circle[0]))
				avglat+=circle[0]
				avglong+=circle[1]
				#print(circle[1])
				total+=1
		for marker_group in marker_groups:
			for marker in marker_group:
				avglat+=marker[0]
				avglong+=marker[1]
				total+=1
		avglat=avglat/total
		avglong=avglong/total
		center=(avglat, avglong)
	gmap=gmplot.GoogleMapPlotter(35.6183, -83.52, 13)
	i=0
	for group in coordinate_groups:
		#color=colors[i%len(colors)]
		color='k'
		i+=1
		lats, longs=zip(*group)
		gmap.scatter(lats, longs, color, size=35, marker=False)
		color=colors[i%len(colors)]
	i=0
	for circle_group in circle_groups:
		color=colors[i%len(colors)]
		for circle in circle_group:
			print(str(circle))
			gmap.circle(circle[0], circle[1], circle[2], color=color)
		i+=1
	i=0
	for polygon in polygon_groups:
		color=colors[random.randint(0, len(colors)-1)]
		#color='k'
		lats, longs=zip(*polygon)
		gmap.plot(lats, longs, color, edge_width=8, opacity=.5)
	i=0
	colors=['g', 'r']
	for marker_group in marker_groups:
		color=colors[i%len(colors)]
		lats, longs=zip(*marker_group)
		gmap.scatter(lats, longs, color, size=40,  opacity=1, marker=False)
		i+=1
	gmap.draw(plot_name)
	
def plotGoogleMapByTime(buckets):
	i=0
	for bucket in buckets:
		plotGoogleMap(coordinate_groups=[bucket], plot_name='TimeSliders/t'+str(i)+'.html')
		i+=1
		
def graph(buckets, delimeter):
	import matplotlib.pyplot as plt
	plot_array=[]
	print(buckets)
	for b in buckets:
		plot_array.append(len(b))
	plt.xlabel(delimeter)
	if delimeter=='weekday':
		x=[0, 1, 2, 3, 4, 5, 6]
		plt.xticks(x, ['M.', 'Tu.', 'Wed.', 'Th.', 'Fri.', 'Sat.', 'Sun.'])
	if delimeter=='month':
		x=[i for i in range(0, 12)]
		plt.xticks(x, ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'])
	plt.ylabel('Number of Images')
	plt.plot(plot_array)
	plt.show()
			
		
