CREATE TYPE interest AS ENUM ('Buyer', 'Seller');
CREATE TYPE condition AS ENUM ('Excellent', 'Very Good', 'Good', 'Fair', 'Poor');

create table users(
 id serial primary key,  
 username  varchar(50) unique,
 password  varchar(50) ,                      
 first_name varchar(50),                       
 last_name  varchar(50),                      
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



select u.id as userid, u.username, u.email, b.id as itemid, b.title, b.price, b.condition, b.isbn as identifier, 'book' as type
from users u, books b
where u.id = b.userid
union
select u.id as userid, u.username, u.email, g.id as itemid, g.title, g.price, g.condition , g.console as identifier, 'game' as type
from users u, games g
where u.id = g.userid
