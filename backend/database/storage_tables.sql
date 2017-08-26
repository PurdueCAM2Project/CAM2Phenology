drop table if exists storedImages;
drop table if exists requests;

create table storedImages
(
	id bigint not null primary key,
	image_hash varchar(20) not null,
	url varchar(2083)
);
