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

# Source environment variables from .env.local
if [ -f .env.local ]; then
    echo "Loading environment variables from .env.local"
    set -a
    source .env.local
    set +a
fi

# Build images explicitly with no cache to ensure clean build
echo "Building Docker images from scratch (no cache)..."
# Use platform-specific build for Apple Silicon Macs
if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    echo "Detected Apple Silicon (ARM64), building native image..."
    DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose build --no-cache app
else
    docker compose build --no-cache app
fi

# Start containers in development mode
echo "Starting in development mode..."
"$(dirname "$0")/start-dev.sh" 