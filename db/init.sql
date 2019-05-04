SET GLOBAL wait_timeout=259200;
SET GLOBAL interactive_timeout=259200;
CREATE DATABASE selflessacts1;
use selflessacts1;

DROP TABLE IF EXISTS acts;

DROP TABLE IF EXISTS category;
CREATE TABLE category (catno INTEGER AUTO_INCREMENT PRIMARY KEY, catname VARCHAR(50), catcount INTEGER);
CREATE TABLE acts (actid BIGINT PRIMARY KEY, votes BIGINT, comments VARCHAR(300), caption VARCHAR(1000), uname VARCHAR(100), catno1 INTEGER, imgpath VARCHAR(8000), times DATETIME,  FOREIGN KEY(catno1) REFERENCES category(catno));

