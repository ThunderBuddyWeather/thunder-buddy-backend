#!/bin/bash
# Development startup script with auto-reload using start.sh

set -e

echo "Starting Thunder Buddy API in development mode with auto-reload..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Creating .env.local from .env..."
    cp .env .env.local
    
    # Add development-specific variables if they don't exist
    grep -q "FLASK_ENV=" .env.local || echo "FLASK_ENV=development" >> .env.local
    grep -q "FLASK_DEBUG=" .env.local || echo "FLASK_DEBUG=1" >> .env.local
    grep -q "FLASK_APP_RELOAD=" .env.local || echo "FLASK_APP_RELOAD=true" >> .env.local
fi

# Set development environment for docker-compose
export COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

# Run the regular start script but override with our development compose file
echo "Using development configuration with auto-reload"
"$(dirname "$0")/start.sh"

# Check if containers started successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "Development server started with auto-reload enabled!"
    echo "Any changes to Python files in ./app or ./scripts will trigger an automatic reload."
    echo ""
    echo "To view logs: docker compose logs -f app"
    echo "To stop: $(dirname "$0")/stop.sh"
    echo ""
fi 