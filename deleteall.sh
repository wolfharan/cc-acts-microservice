#!/bin/bash
docker container stop $(docker ps -a -q)
docker container rm $(docker ps -a -q)
echo 'y' | docker image prune -a
echo 'y' | docker system prune --volumes

