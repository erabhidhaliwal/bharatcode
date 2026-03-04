#!/bin/bash

# Project Directory Structure Creator

# Define the directory structure
directories=(
    "src"
    "src/main"
    "src/test"
    "lib"
    "bin"
    "build"
    "dist"
    "docs"
    "config"
    "logs"
    "tmp"
)

# Create directories
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created: $dir"
    else
        echo "Exists: $dir"
    fi
done

echo "Directory structure creation complete!"