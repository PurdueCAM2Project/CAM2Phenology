import pymysql.cursors
import getpass



pswd=getpass.getpass("Input password:")
connection=pymysql.connect(host='localhost',
							user='root',
							password=pswd,
							db='Phenology')
							
cursor=connection.cursor()							

def insertRegion(name, num_images=0, mean_point=None):
	#with connection.cursor() as cursor:
	sql= "INSERT IGNORE INTO regions (name, num_images, mean_point) VALUES (%s, %s, %s)"
	cursor.execute(sql, (name, num_images, mean_point))
	connection.commit()
		
	
def insertImage(id, region, date_taken, date_retrieved, gps, latitude, longitude, source=None, cluster_id=None):
	print(str(gps))
	sql="REPLACE INTO images (id, region, date_taken, date_retrieved, gps,  latitude, longitude, source, cluster_id) VALUES (%s, %s, %s, %s, point"+str(gps)+", %s, %s, %s, %s)"
	cursor.execute(sql, (id, region, date_taken, date_retrieved, latitude, longitude, source, cluster_id))
	sql="UPDATE regions SET num_images= num_images+1 WHERE name LIKE '"+str(region)+"'"
	cursor.execute(sql)
	connection.commit()
	
	
	

	

	
"""insertRegion('test')
insertImage(3432, 'test', 20090626, 20160405, (4, 4))							
connection.close()"""

