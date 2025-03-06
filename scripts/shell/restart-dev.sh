#!/bin/bash
# Development restart script - stops containers and restarts in development mode

set -e

echo "Restarting Thunder Buddy API in development mode..."

# Stop running containers using stop.sh
echo "Stopping running containers..."
"$(dirname "$0")/stop.sh"

# Start containers in development mode
echo "Starting in development mode with auto-reload..."
"$(dirname "$0")/dev.sh" 