drop table if exists cv_tags;
drop table if exists training_tags;
drop table if exists tags;
drop table if exists images;
drop table if exists tests;
drop table if exists datasets;


create table datasets
(
	name varchar(50) not null primary key,
	master varchar(50),
	num_images int
);

create table tests
(
	id bigint not null primary key auto_increment,
	module_name varchar(50) not null,
	module_version int not null,
	time_tested timestamp default current_timestamp,
	dataset_name varchar(50) not null,
	foreign key(dataset_name)
		references datasets(name),
	success_rate decimal(5, 4)
);

create table tags
(
	id bigint not null primary key auto_increment,
	tag varchar(25) unique key
	
);

create table images
(
	id bigint not null primary key auto_increment,
	time_added timestamp default current_timestamp,
	dataset_name varchar(50) not null,
	foreign key(dataset_name)
		references datasets(name),
	imagehash varchar(25) not null,
	url varchar(2083),
	source varchar(50),
	x_resolution int,
	y_resolution int,
	date_taken datetime,
	index (date_taken),
	gps point,
	notes varchar(500)
);

create table cv_tags
(
	tag_id bigint not null,
	foreign key(tag_id)
		references tags(id),
	image_id bigint not null,
	foreign key(image_id)
		references images(id),
	test_id bigint,
	foreign key(test_id)
		references tests(id),
	primary key (tag_id, image_id, test_id),
	user_name varchar(20),
	tag_data json
);

create table training_tags
(
	tag_id bigint not null,
	foreign key(tag_id)
		references tags(id),
	image_id bigint not null,
	foreign key(image_id)
		references images(id),
	primary key (tag_id, image_id),
	test_id bigint,
	foreign key(test_id)
		references tests(id),
	hit_rate decimal(5, 4),
	notes varchar(100),
	user_name varchar(20),
	tag_data json
	/*all tag data stored in json format.  
	This makes for flexible tag types that can be defined as they are used. */
);

	
	
	