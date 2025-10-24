#!/bin/bash

# Exit in case of error
set -e

# Check OS
if [[ "$(uname -s)" == "Linux" ]]; then
  python3 -m venv .venv
  source .venv/bin/activate

elif [[ "$(uname -s)" == "Darwin" ]]; then
  python3 -m pip install virtualenv
  python3 -m virtualenv .venv
  source ./venv/bin/activate

elif [[ "$(uname -s)" == "CYGWIN"  || "$(uname -s)" == "MINGW"* ]]; then
  python -m venv .venv
  .venv\Scripts\activate

else
  echo "Unknown OS"
fi


# Upgrade pip inside venv
pip install --upgrade pip

# Install uv inside venv
pip install --upgrade uv

# Run uv
uv run
