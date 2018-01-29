#command line application to access all functions
import core
import getpass
import sys

def queryDatabase():
	sql=""
	print("Querying database.  Type 'c' to exit.")
	sql=input("mysql > ")
	while sql!='c':
		print(str(core.db.query(sql=sql)))
		sql=input("mysql > ")
		
def addRegion():
	region_name=input('Enter Region Name: ')
	latitude=input('Enter Latitude: ')
	longitude=input("Enter Longitude: ")
	core.db.addRegion(region_name, latitude, longitude)
	
def addLocation():
	latitude=input('Enter Latitude: ')
	longitude=input('Enter Longitude:' )
	radius=input('Enter Radius: ')
	core.db.addLocation(float(latitude), float(longitude), float(radius))
	
parameters={'latitude': None, 'longitude': None, 'radius': None}
functions={'q': queryDatabase, 'al': addLocation, 'ar': addRegion, 'e': sys.exit}		
if __name__=='__main__':
	core.login(getpass.getpass("Input password: "))
	while True:
		func=input("Input Function: ")
		functions[func]()
	#queryDatabase()