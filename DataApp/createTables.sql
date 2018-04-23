drop table if exists tag_links;
drop table if exists search_tags;
drop table if exists tags;
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
	searched int default 0,
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
	id bigint not null primary key auto_increment,
	source_id bigint not null,
	source varchar(10) not null,
	unique key(source_id, source),
	date_taken datetime,
	index (date_taken),
	date_retrieved timestamp default current_timestamp,
	gps POINT,
	latitude FLOAT(12, 9),
	longitude FLOAT (12, 9),
	url VARCHAR(2083),
	cluster_id bigint,
	foreign key (cluster_id)
		references clusters(id),
	alt_id BIGINT,
	userid varchar(20),
	haspeople int default 0,
	useable int default 0,
	imagehash varchar (25) default null,
	downloaded int default 0,
	x_resolution int default null,
	y_resolution int default null,
	camera varchar(30) default null,
	notes varchar(500) default null
);


create table tags
(
	id bigint not null primary key auto_increment,
	tagname varchar(50) not null unique key
);

create table search_tags
(
	tag_id bigint not null primary key,
	foreign key(tag_id) references tags(id),
	searched int default 0
);

create table tag_links
(
	tag_id bigint not null,
	foreign key(tag_id) references tags(id),
	image_id bigint not null,
	foreign key(image_id) references images(id),
	primary key(tag_id, image_id),
	tag_value float(12, 9),
	tag_data json
);
