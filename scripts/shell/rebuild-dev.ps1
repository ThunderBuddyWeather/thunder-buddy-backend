# PowerShell script to rebuild Thunder Buddy in development mode
# 
# ARCHITECTURE INFO:
# This is an implementation script that lives in the scripts/shell directory.
# It can be called directly or via a wrapper script from the bin/ directory.
# 
# This architecture allows:
# - Implementation details to be separated from user-facing scripts
# - Cross-platform support via different implementations (.sh, .bat, .ps1)
# - Better organization and maintainability
# - Changes to implementation without affecting the user interface
#

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