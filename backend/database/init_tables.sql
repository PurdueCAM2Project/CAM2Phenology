drop table if exists images;
drop table if exists clusters;
drop table if exists regions;


create table regions
(
	name char(25) not null primary key,
	num_images int,
	mean_point POINT
);


create table clusters
(
	id int not null primary key,
	gps POINT not null,
	region_name char(25) not null,
	foreign key (region_name)
		references regions(name),
	num_images int
);

create table images 
(
	id BIGINT not NULL primary key,
	region char(25) not null,
	foreign key(region)
		references regions(name),
	date_taken int not null,
	index (date_taken),
	date_retrieved timestamp,
	gps POINT,
	latitude FLOAT(12, 9),
	longitude FLOAT (12, 9),
	source char(25),
	cluster_id int,
	foreign key (cluster_id)
		references clusters(id)

);

