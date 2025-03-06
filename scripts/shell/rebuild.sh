#!/bin/bash
set -e

# Print section header
print_header() {
    echo "----------------------------------------"
    echo "$1"
    echo "----------------------------------------"
}

# Source environment variables
if [ -f .env.local ]; then
    echo "Loading environment variables from .env.local"
    set -a
    source .env.local
    set +a
fi

# Stop running containers
print_header "Stopping containers"
"$(dirname "$0")/stop.sh"

# Remove static volume to ensure fresh swagger.yaml
print_header "Removing static volume"
docker volume rm thunder_buddy_static || true

# Rebuild the image
print_header "Rebuilding Docker image"
# Use platform-specific build for Apple Silicon Macs
if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    echo "Detected Apple Silicon (ARM64), building native image..."
    DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose build app
else
    docker compose build app
fi

# Start services
print_header "Starting services"
"$(dirname "$0")/start.sh" 