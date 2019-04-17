import mysql.connector

mydb2 = mysql.connector.connect(host = "db", port = 3306, user = 'root', password = 'root')
mycursor2 = mydb2.cursor()
mycursor2.execute("DROP DATABASE IF EXISTS selflessacts1")
mycursor2.execute("CREATE DATABASE selflessacts1")
mydb1 = mysql.connector.connect(host = "db", port = 3306, user = 'root', password = 'root', database = 'selflessacts1')

mycursor1 = mydb1.cursor()
mycursor1.execute("""DROP TABLE IF EXISTS acts""")

mycursor1.execute("""DROP TABLE IF EXISTS category""")

mycursor1.execute("""CREATE TABLE category (catno integer AUTO_INCREMENT PRIMARY KEY, catname VARCHAR(50), catcount INTEGER)""")
mycursor1.execute("""CREATE TABLE acts (actid integer PRIMARY KEY, votes integer, comments VARCHAR(300), caption VARCHAR(300), uname VARCHAR(100), catno1 INTEGER, imgpath VARCHAR(800), times DATETIME,  FOREIGN KEY(catno1) REFERENCES category(catno))""")


