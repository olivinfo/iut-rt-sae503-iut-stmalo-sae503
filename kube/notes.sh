#!/bin/bash

helm repo add traefik https://traefik.github.io/charts
helm repo update

helm install traefik traefik/traefik -f values.yaml --wait

kubectl apply -f whoami.yaml
kubectl apply -f whoami-service.yaml