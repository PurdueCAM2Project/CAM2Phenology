
drop table if exists tag_links;
drop table if exists permissions;
drop table if exists users;
drop table if exists tags;
drop table if exists images;
drop table if exists project_data;
drop table if exists projects;
drop table if exists datasets;


create table datasets
(
	id bigint not null primary key auto_increment,
	name varchar(50) not null unique key

);

create table projects
(
	id bigint not null primary key auto_increment,
	name varchar(50),
	description varchar(500)
);

create table project_data
(
	project_id bigint not null,
	foreign key(project_id) references projects(id),
	dataset_id bigint not null,
	foreign key(dataset_id) references datasets(id),
	primary key(project_id, dataset_id)
);
create table tags
(
	id bigint not null primary key auto_increment,
	tag_type varchar(25),
	tag varchar(25) unique key
);

create table images
(
	id bigint not null primary key auto_increment,
	time_added timestamp default current_timestamp,
	dataset_id bigint not null,
	foreign key(dataset_id) references datasets(id),
	imagehash varchar(25) not null,
	unique key(imagehash, dataset_id),
	url varchar(2083),
	source varchar(50),
	x_resolution int,
	y_resolution int,
	date_taken datetime,
	index (date_taken),
	gps point,
	notes varchar(500)
);

create table users
(
	id bigint not null primary key auto_increment,
	user_name varchar(20) not null,
	time_added timestamp default current_timestamp
);

create table permissions
(
	user_id bigint not null,
	foreign key(user_id) references users(id),
	dataset_id bigint,
	foreign key(dataset_id) references datasets(id),
	primary key(user_id, dataset_id)
);

create table tag_links
(
	tag_id bigint not null,
	foreign key(tag_id) references tags(id),
	image_id bigint not null,
	foreign key(image_id) references images(id),
	user_id bigint not null,
	foreign key(user_id) references users(id),
	primary key (tag_id, image_id, user_id),
	time_tagged timestamp default current_timestamp,
	notes varchar(100),
	tag_data json

);

insert into datasets (name) values("test1");
insert into datasets (name) values ('test2');
insert into users(user_name) values("test user1");
insert into users(user_name) values("test user2");
insert into users(user_name) values("test user3");
insert into users(user_name) values("test user4");
insert into permissions(user_id, dataset_id) values(1, 1);

	
	
	