"""
INSTRUCTIONS ON HOW TO RUN:
-Install python3.5
-Use pip to install dependencies: PyMySql, tkinter, PIL,  etc
-Set up mysql server
-create a database
-Initialize tables with file init_tables.sql and storage_tables.sql 
(Type "SOURCE your/path/to/init_tables.sql; path/to/storage_tables.sql" in mysql command line. Do the same)
-Use db_setup.py to set up your log in to the database. Or directly modify the top of dbManager.py
-Beware of bugs. Try to follow the code when using the ui. It is not user friendly
-you cant filter images until you have images to filter in your database
-Give search functions time
-All images will be labelebed with region name "Smoky Mountains" by default at this point
-Google map will be stored as 'plots/temp.html'.  Open in web browser and refresh after every action to see how map changes
"""
import tkinter 
from tkinter import *
from PIL import Image, ImageTk
import storageUtil
import urlViewer

root=tkinter.Tk()

# ---Entries--
region=Entry(root, text='Enter Region', bd=2, width=10)
latitude=Entry(root, text='lat', bd=2, width=10)
longitude=Entry(root, text='lon', bd=2, width=10)
radius=Entry(root, text='radius', bd=2, width=10)
date1=Entry(root, text='date1', bd=2, width=10)
date2=Entry(root, bd=2, text='date2', width=10)
#------------------

# --Labels--
region_text=Label(root, text="Region")
latitude_text=Label(root, text='Latitude')
longitude_text=Label(root, text='Longitude')
radius_text=Label(root, text='Radius')
date1_text=Label(root, text="Minimum Date")
date2_text=Label(root, text="Maximum Date")
#------------------


# --Buttons-- 
search=Button(root, text='search', width=10, command= lambda: storageUtil.makeSearch(float(latitude.get()), float(longitude.get()), float(radius.get())))
filter=Button(root, text='Apply Filter', width=10, command= lambda: storageUtil.loadFilter(region.get(), latitude.get(), longitude.get(), radius.get(), date1.get(), date2.get()))
clear=Button(root, text='clear', width=10, command=storageUtil.clearAll)
sample_search=Button(root, text='Sample Search', width=10, command=storageUtil.loadSearchSample)
commit_search=Button(root, text='Commit Search', width=10, command= lambda: storageUtil.commitSearch(region.get()))
plot_circle=Button(root, text='Plot Circle', width=10, command= lambda: storageUtil.addCircle(float(latitude.get()), float(longitude.get()), float(radius.get())))
#-----------------------

# --Grid--
region.grid(row=0, column=0)
latitude.grid(row=0, column=1)
longitude.grid(row=0, column=2)
radius.grid(row=0, column=3)
date1.grid(row=0, column=4)
date2.grid(row=0, column=5)

region_text.grid(row=1, column=0)
latitude_text.grid(row=1, column=1)
longitude_text.grid(row=1, column=2)
radius_text.grid(row=1, column=3)
date1_text.grid(row=1, column=4)
date2_text.grid(row=1, column=5)

plot_circle.grid(row=2, column=0)
filter.grid(row=3, column=0)
search.grid(row=4, column=0)
sample_search.grid(row=5, column=0)
commit_search.grid(row=6, column=0)
clear.grid(row=7, column=0)
#------------------------------

#launching urlViewer in the same window
urlViewer.display(storageUtil.iterator, root=root, sub_window=True, row_offset=1, column_offset=5)
root.mainloop()















