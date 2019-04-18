docker build -t custom-sql .
docker run -d -p 3306:3306 --name db custom-sql
