#!/bin/bash
# This script exports the PDM project dependencies to a requirements.txt file
# Ensure PDM is installed
if ! command -v pdm &> /dev/null
then
    echo "PDM could not be found. Please install PDM first."
    exit 1
fi

pdm export --without-hashes --format requirements > requirements.txt

pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully."
else
    echo "Failed to install dependencies."
    exit 1
fi