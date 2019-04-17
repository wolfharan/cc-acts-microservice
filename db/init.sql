CREATE DATABASE selflessacts1;
use selflessacts1;

DROP TABLE IF EXISTS acts;

DROP TABLE IF EXISTS category;
CREATE TABLE category (catno integer AUTO_INCREMENT PRIMARY KEY, catname VARCHAR(50), catcount INTEGER);
CREATE TABLE acts (actid integer PRIMARY KEY, votes integer, comments VARCHAR(300), caption VARCHAR(300), uname VARCHAR(100), catno1 INTEGER, imgpath VARCHAR(800), times DATETIME,  FOREIGN KEY(catno1) REFERENCES category(catno));

