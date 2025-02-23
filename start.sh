#!/bin/bash

# Check if .env file exists
if [ ! -f .env.local ] && [ ! -f .env ]; then
    echo "Error: No .env file found. Please create .env.local or .env file"
    echo "You can copy .env.example as a template"
    exit 1
fi

# Source the environment variables from .env.local
if [ -f .env.local ]; then
    echo "Loading environment variables from .env.local"
    set -a  # automatically export all variables
    source .env.local
    set +a
fi

# Check for required environment variables
required_vars=(
    "POSTGRES_PASSWORD"
    "DB_PASSWORD"
    "DOCKER_USERNAME"
)

missing_vars=0
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in environment"
        missing_vars=1
    fi
done

if [ $missing_vars -eq 1 ]; then
    echo "Please set all required environment variables and try again"
    exit 1
fi

# Export variables for docker compose
export DOCKER_USERNAME DB_PASSWORD POSTGRES_PASSWORD

docker compose --env-file .env.local up 