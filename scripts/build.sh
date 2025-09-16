#!/bin/bash

# Exit in case of error
set -e

# Create venv

if [ ! -d ".venv" ]; then
  echo "Creating venv..."
  python -m venv .venv
fi

# Activate the venv 
if [[ "$(uname -s)" == "Linux" ]]; then
	source .venv/bin/activate

elif [[ "$(uname -s)" == "Darwin" ]]; then
	source ./venv/bin/activate

elif [[ "$(uname -s)" == "CYGWIN"  || "$(uname -s)" == "MINGW"* ]]; then
	source .venv\Scripts\activate
else
	echo "Unknown OS"
fi

# Upgrade pip inside venv
pip install --upgrade pip

# Install uv inside venv
pip install --upgrade uv

# Run uv
uv run
