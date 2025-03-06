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
docker compose build app

# Start services
print_header "Starting services"
"$(dirname "$0")/start.sh" 