#!/bin/bash

docker compose down
docker compose up --build

# pytest citations_haddock/test_citations_haddock.py