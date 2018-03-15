#functions to create graphical models of data



def plotGoogleMap(coordinate_groups=[], circles=[], center=None, plot_name='temp.html'):
	#Plotting data on google map
	import gmplot
	import gmplot.color_dicts
	if center is None:
		avglat=0;
		avglong=0
		total=0
		for group in coordinate_groups:
			for coord in group:
				avglat+=coord[0]
				avglong+=coord[1]
				total+=1
		for circle in circles:
			avglat+=circle[0]
			avglong+=circle[1]
			total+=1
		avglat=avglat/total
		avglong=avglong/total
		center=(avglat, avglong)
	gmap=gmplot.GoogleMapPlotter(center[0], center[1], 12)
	colors=list(gmplot.color_dicts.html_color_codes.keys())
	i=0
	color='k'
	for group in coordinate_groups:
		i+=1
		lats, longs=zip(*group)
		gmap.scatter(lats, longs, color, size=35, marker=False)
		color=colors[i%len(colors)]
	gmap.draw('temp.html')
		