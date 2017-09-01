import pymysql.cursors
import atexit
from datetime import datetime
import getpass

timestamp=datetime.today()
print(timestamp)

pswd=getpass.getpass("Input Password")
connection=pymysql.connect(
	host='localhost',
	user='root',
	password=pswd,
	db='ImageDB',
	cursorclass=pymysql.cursors.DictCursor
)
user='root'
cursor=connection.cursor()

def query(sql, values=None):
	if values is None:
		cursor.execute(sql)
	else:
		cursor.execute(sql, values)
	connection.commit()
	return cursor.fetchall()
	
def insertDatasetRow(name, master=None, num_images=0):
	sql="REPLACE INTO datasets (name, master, num_images) VALUES (%s, %s, %s)"
	query(sql, (name, master, num_images))
	
def insertImageRow(dataset_name, imagehash, url=None, source=None, x_resolution=None, y_resolution=None, date_taken=None, gps=None, notes=None):
	sql="REPLACE INTO images (dataset_name, imagehash, url, source, x_resolution, y_resolution, date_taken, gps, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	if gps:
		gps=string(gps)
	query(sql, values=(dataset_name, str(imagehash), url, source, x_resolution, y_resolution, date_taken, gps, notes))
	
def insertDataset(dataset_name,  image_rows, master_dataset=None):
	num_rows=len(image_rows)
	insertDatasetRow(dataset_name, master=master_dataset, num_images=num_rows)
	for row in image_rows:
		insertImageRow(dataset_name, row['imagehash'], url=row.get('url'), source=row.get('source'), x_resolution=row.get('x_resolution'), y_resolution=row.get('y_resolution'), date_taken=row.get('date_taken'), gps=row.get('gps'), notes=row.get('notes'))
		
def newTest(test_name, dataset_name):
	sql="INSERT INTO tests (test_name, dataset_name) VALUES (%s, %s)"
	query(sql, values=(test_name, dataset_name))
		
def newTag(tag_string):
	sql="INSERT INTO tags (tag) VALUES (%s)"
	query(sql, values=(tag_string))
	
def insertTrainingTag(tag_id, image_id, test_id=None, tag_data=None, notes=None):
	sql="REPLACE INTO training_tags (tag_id, image_id, test_id, tag_data, notes, user_name) VALUES (%s, %s, %s, %s, %s, %s)"
	query(sql, values=(tag_id, image_id, test_id, tag_data, notes, user))
	
def insertCVTag(tag_id, image_id, test_id, tag_data=None):
	sql="INSERT INTO training_tags (tag_id, image_id, test_id, tag_data, user_name) VALUES (%s, %s, %s, %s, %s)"
	query(sql, values=(tag_id, image_id, test_id, tag_data, user))
	
def selectDataset(dataset):
	sql="SELECT * FROM images WHERE dataset_name LIKE %s ORDER BY date_taken"
	return query(sql, values=(dataset))
		
def getLastID():
	sql="SELECT LAST_INSERT_ID()"
	return query(sql)[0]['LAST_INSERT_ID()']
	
def getTagID(tag_name):
	sql="SELECT id FROM tags WHERE tag LIKE %s"
	return query(sql, values=(tag_name))[0]['id']
	

	

	
	


