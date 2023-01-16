#!/bin/sh
docker pull balrundev/flask-counter
docker stop counter-app
docker rm counter-app
docker run -d -p 80:80 --name counter-app balrundev/flask-counter
