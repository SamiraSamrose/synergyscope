# File: scripts/deploy.sh

#!/bin/bash
set -e

echo "Deploying SynergyScope..."

# Build Docker image
docker build -t synergyscope:latest -f infrastructure/docker/Dockerfile .

# Tag for registry
docker tag synergyscope:latest your-registry/synergyscope:latest

# Push to registry
docker push your-registry/synergyscope:latest

# Deploy to ECS/EKS
# kubectl apply -f k8s/deployment.yaml

echo "Deployment complete!"