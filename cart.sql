create table category(
	id  int not null AUTO_INCREMENT,
	name varchar(200) NOT NUll,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id)
);

create table product(
	id  int not null AUTO_INCREMENT,
	name varchar(200) NOT NUll,
	description text NOT NULL,
	price int(11) NOT NULL,
	category_id int(11) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id),
	FOREIGN KEY (category_id) REFERENCES category(id)
);

create table user(
	id  int not null AUTO_INCREMENT,
	name varchar(200) NOT NUll,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id)
);	

create table cart(
	id  int not null AUTO_INCREMENT,
	user_id int(11) NOT NULL,
	product_id int(11) NOT NULL,
	quantity  int(11) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES user(id),
	FOREIGN KEY (product_id) REFERENCES product(id)
);

create table orders(
	id  int not null AUTO_INCREMENT,
	user_id int(11) NOT NULL,
	total_amount int(11) NOT NULL,
	discount int(11) NULL,
	status INT(11)	DEFAULT 1,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES user(id)
);

create table order_product(
	id  int not null AUTO_INCREMENT,
	order_id int(11) NOT NULL,
	product_id int(11) NOT NULL,
	quantity  int(11) NOT NULL,
	amount int(11) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES orders(id),
	FOREIGN KEY (product_id) REFERENCES product(id)
);

ALTER TABLE `category` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

