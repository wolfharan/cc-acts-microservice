#!/bin/bash
docker build -t acts-app .
docker run -d  -p 80:80 --name acts1 --link db acts-app
