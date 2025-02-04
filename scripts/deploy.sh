#!/bin/bash

# Build the Docker image
docker build -t bitebase-api .

# Tag the image
docker tag bitebase-api:latest your-registry/bitebase-api:latest

# Push to registry
docker push your-registry/bitebase-api:latest

# Apply Kubernetes configs
kubectl apply -f k8s/ 