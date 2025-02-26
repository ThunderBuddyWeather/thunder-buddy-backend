#!/bin/bash
# Deployment script for Thunder Buddy application
# This script handles the deployment process for the Thunder Buddy application

set -e  # Exit on error

# Print a message with a timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  log "Error: Docker is not installed. Please install Docker before running this script."
  exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
  log "Error: Docker Compose is not installed. Please install Docker Compose before running this script."
  exit 1
fi

log "Starting deployment process..."

# Stop and remove existing containers (but preserve volumes)
log "Stopping existing containers (preserving volumes)..."
docker compose down || true

# Remove any dangling images
log "Cleaning up dangling images..."
docker image prune -f

# Build the application image
log "Building application image..."
docker compose build app

# Start the containers
log "Starting containers..."
docker compose up -d

# Wait for the database to be ready
log "Waiting for database to be ready..."
max_retries=30
counter=0
while ! docker exec thunder-buddy-db pg_isready -U postgres && [ $counter -lt $max_retries ]; do
  log "Waiting for database connection... ($counter/$max_retries)"
  sleep 2
  counter=$((counter+1))
done

if [ $counter -eq $max_retries ]; then
  log "Error: Could not connect to database after $max_retries attempts"
  log "Continuing anyway, as the application might still start..."
fi

# Wait for the application to be healthy
log "Waiting for application to become healthy..."
max_retries=60
counter=0
while [ "$(docker inspect --format='{{.State.Health.Status}}' thunder-buddy)" != "healthy" ] && [ $counter -lt $max_retries ]; do
  log "Waiting for application to become healthy... ($counter/$max_retries)"
  sleep 5
  counter=$((counter+1))
  
  # Print the health check logs
  if [ $((counter % 5)) -eq 0 ]; then
    log "Health check logs:"
    docker inspect --format='{{json .State.Health}}' thunder-buddy | jq
  fi
done

if [ $counter -eq $max_retries ]; then
  log "Warning: Application did not become healthy after $max_retries attempts"
  log "Container logs:"
  docker logs thunder-buddy
  log "Continuing anyway, as the application might still be functional..."
fi

# Print the container status
log "Container status:"
docker ps -a | grep thunder-buddy

# Print the application URL
app_port=$(docker port thunder-buddy 5000/tcp | cut -d ':' -f 2)
log "Application is available at: http://localhost:$app_port"

log "Deployment completed successfully!" 