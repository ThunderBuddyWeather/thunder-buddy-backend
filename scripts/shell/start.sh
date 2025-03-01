#!/bin/bash
set -e

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

# Check if port 5000 is available
if nc -z localhost 5000 2>/dev/null; then
  echo "Port 5000 is already in use. Using port 5001 instead."
  export HOST_PORT=5001
else
  echo "Port 5000 is available. Using it."
  export HOST_PORT=5000
fi

# Update .env.local with the selected port
sed -i.bak "s/HOST_PORT=.*/HOST_PORT=$HOST_PORT/" .env.local
rm -f .env.local.bak

# Export all environment variables from .env.local, but safely
# Only export valid shell variable assignments (KEY=VALUE format)
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    if [[ ! $key =~ ^#.*$ ]] && [[ ! -z "$key" ]]; then
        # Check if key is a valid shell variable name (alphanumeric and underscore)
        if [[ $key =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
            export "$key=$value"
        fi
    fi
done < .env.local

# Start the containers
docker compose down
docker compose up -d

echo "Thunder Buddy is now running on http://localhost:$HOST_PORT" 