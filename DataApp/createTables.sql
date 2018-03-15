drop table if exists images;
drop table if exists clusters;
drop table if exists locations;
drop table if exists regions;


create table regions
(
	name char(30) not null primary key,
	num_images int,
	mean_point POINT,
	area POLYGON,
	radius int
);

create table locations
(
	id bigint not null primary key auto_increment,
	region char(30) not null,
	foreign key (region)
		references regions(name),
	gps POINT not null,
	radius FLOAT(12, 9),
	unique key(gps, radius),
	last_updated datetime,
	num_images bigint,
	notes varchar(100) default null
);

create table clusters
(
	id bigint not null primary key auto_increment,
	gps POINT not null,
	radius FLOAT(12, 9),
	region char(30) not null,
	foreign key (region)
		references regions(name),
	num_images int
);

create table images
(
	id BIGINT not null,
	source varchar(10) not null,
	primary key(id, source),
	region char(30),
	foreign key (region)
		references regions(name),
	/*location_id bigint not null,
	foreign key(location_id)
		references locations(id),*/
	date_taken datetime not null,
	index (date_taken),
	date_retrieved timestamp default current_timestamp,
	gps POINT,
	latitude FLOAT(12, 9),
	longitude FLOAT (12, 9),
	url VARCHAR(2083) not null,
	cluster_id bigint,
	foreign key (cluster_id)
		references clusters(id),
	alt_id BIGINT,
	userid varchar(20),
	haspeople int default 0,
	useable int default 0,
	camera varchar(30) default null,
	notes varchar(500) default null

);
