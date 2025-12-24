#!/bin/bash

# Exit on any error
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

# Remove stopped containers
log_info "Removing stopped containers..."
docker container prune -f

# Optional: Remove unused images
log_info "Removing unused images..."
docker image prune -f

# Optional: Remove unused networks
log_info "Removing unused networks..."
docker network prune -f

log_info "Clean up completed."