#!/usr/bin/bash

docker build -t citations_haddock .
docker run -p 5000:5000 --name flask-redis-app flask-redis-app


