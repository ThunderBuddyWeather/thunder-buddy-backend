#!/bin/bash

# Source environment variables to ensure proper container names
if [ -f .env.local ]; then
    set -a
    source .env.local
    set +a
fi

echo "Stopping Docker containers..."
docker compose down --remove-orphans

echo "Cleaning up any dangling containers..."
docker container prune -f

echo "Services stopped successfully" 