# PowerShell script to rebuild Thunder Buddy in development mode
# Development rebuild script - rebuilds Docker images and restarts in development mode
$ErrorActionPreference = "Stop"

Write-Host "Rebuilding Thunder Buddy API in development mode..."

# Stop running containers using stop.ps1
Write-Host "Stopping running containers..."
& "$PSScriptRoot/stop.ps1"

# Remove existing Docker images to force complete rebuild
Write-Host "Removing existing Docker images to force rebuild..."
docker compose down --rmi local

# Set development environment for docker-compose
$env:COMPOSE_FILE = "docker-compose.yml:docker-compose.dev.yml"

# Build images explicitly with no cache to ensure clean build
Write-Host "Building Docker images from scratch (no cache)..."
docker compose build --no-cache app

# Start containers in development mode
Write-Host "Starting in development mode with auto-reload..."
& "$PSScriptRoot/dev.ps1" 