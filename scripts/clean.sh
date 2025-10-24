#!/bin/bash

# Exit in case of error
set -e
set -x

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Optional: Remove unused images
echo "Removing unused images..."
docker image prune -f

# Optional: Remove unused networks
echo "Removing unused networks..."
docker network prune -f

echo "Clean up completed."

