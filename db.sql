CREATE TYPE interest AS ENUM ('Buyer', 'Seller');
CREATE TYPE condition AS ENUM ('Excellent', 'Very Good', 'Good', 'Fair', 'Poor');

create table users(
 id serial primary key,  
 username  varchar(50) ,
 password  varchar(50) ,                      
 first_name varchar(50),                       
 last_name  varchar(50,                      
 age        integer,                     
 email      varchar(50),                    
 phone      varchar(12), 
 city       varchar(50),
 state      varchar(50),
 zip        varchar(10),                 
 created    timestamp  default now()
)

create table books(
id serial primary key,
isbn varchar(50),
isbn13 varchar(50),
title varchar(120),
author varchar(50),
condition condition not null,
interest interest not null,
price numeric(10, 2),
userid integer references users,
created timestamp default now()
)

create table games(
	id serial primary key,
	title varchar(120),
	console varchar(50),
	condition condition not null,
	interest interest not null,
	price numeric(10,2),
	userid integer references users,
	created timestamp default now()

)