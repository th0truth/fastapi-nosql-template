#!/bin/bash

# Exit on any error
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Detect OS
OS_TYPE="$(uname -s)"

log_info "Detected OS: $OS_TYPE"

# Initialize virtual environment
if [[ "$OS_TYPE" == "Linux" || "$OS_TYPE" == "Darwin" ]]; then
  log_info "Installing uv package manager..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  log_info "Creating virtual environment..."
  uv venv
  
  log_info "Activating virtual environment..."
  source .venv/bin/activate
  
elif [[ "$OS_TYPE" == "CYGWIN" || "$OS_TYPE" == "MINGW"* ]]; then
  log_info "Setting up Python virtual environment for Windows..."
  python -m venv .venv
  
  log_info "Activating virtual environment..."
  source .venv/Scripts/activate
  
else
  log_error "Unsupported OS: $OS_TYPE"
  exit 1
fi

# Generate lock file
log_info "Generating dependency lock file..."
uv lock

# Sync environment
log_info "Syncing dependencies..."
uv sync

# Build info
log_info "Build completed successfully!"
echo ""
log_info "Environment ready. To activate:"
if [[ "$OS_TYPE" == "Linux" || "$OS_TYPE" == "Darwin" ]]; then
  echo "  source .venv/bin/activate"
else
  echo "  source .venv/Scripts/activate"
fi
