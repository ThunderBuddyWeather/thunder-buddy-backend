#!/bin/bash
# Development rebuild script - rebuilds Docker images and restarts in development mode

set -e

echo "Rebuilding Thunder Buddy API in development mode..."

# Stop running containers using stop.sh
echo "Stopping running containers..."
"$(dirname "$0")/stop.sh"

# Remove existing Docker images to force complete rebuild
echo "Removing existing Docker images to force rebuild..."
docker compose down --rmi local

# Set development environment for docker-compose
export COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

# Build images explicitly with no cache to ensure clean build
echo "Building Docker images from scratch (no cache)..."
docker compose build --no-cache app

# Start containers in development mode
echo "Starting in development mode with auto-reload..."
"$(dirname "$0")/dev.sh" 