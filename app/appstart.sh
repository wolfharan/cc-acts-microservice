#!/bin/bash
docker build -t acts:latest .
docker run -d  -p 8000:80 --name acts1 --link db acts:latest
