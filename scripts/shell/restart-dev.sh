#!/bin/bash
# Development restart script - stops containers and restarts in development mode

set -e

echo "Restarting Thunder Buddy API in development mode..."

# Set development environment for docker-compose
export COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

# Stop running containers
echo "Stopping containers..."
docker compose down

# Start containers in development mode
echo "Starting in development mode..."
"$(dirname "$0")/start-dev.sh" 