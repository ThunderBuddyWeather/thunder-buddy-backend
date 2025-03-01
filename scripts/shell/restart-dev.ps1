# PowerShell script to restart Thunder Buddy in development mode
# Development restart script - stops containers and restarts in development mode
$ErrorActionPreference = "Stop"

Write-Host "Restarting Thunder Buddy API in development mode..."

# Stop running containers using stop.ps1
Write-Host "Stopping running containers..."
& "$PSScriptRoot/stop.ps1"

# Start containers in development mode
Write-Host "Starting in development mode with auto-reload..."
& "$PSScriptRoot/dev.ps1" 