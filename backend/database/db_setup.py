import json

pref={}

pref['user name']=input("Specify user name: ")
pref['database']=input("Specify database ('Phenology' or 'Test'): ")

print("To change these setting run db_setup.py") 

with open('preferences.json', 'w+') as file:
	json.dump(pref, file)
file.close()

