# PowerShell script for Thunder Buddy development actions
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

# PowerShell script to start Thunder Buddy in development mode with auto-reload
$ErrorActionPreference = "Stop"

Write-Host "Starting Thunder Buddy API in development mode with auto-reload..."

# Check if .env.local exists
if (-not (Test-Path -Path ".env.local")) {
    Write-Host "Creating .env.local from .env..."
    Copy-Item .env .env.local
    
    # Add development-specific variables if they don't exist
    $envContent = Get-Content ".env.local"
    
    if (-not ($envContent -match "FLASK_ENV=")) {
        Add-Content -Path ".env.local" -Value "FLASK_ENV=development"
    }
    
    if (-not ($envContent -match "FLASK_DEBUG=")) {
        Add-Content -Path ".env.local" -Value "FLASK_DEBUG=1"
    }
    
    if (-not ($envContent -match "FLASK_APP_RELOAD=")) {
        Add-Content -Path ".env.local" -Value "FLASK_APP_RELOAD=true"
    }
}

# Set development environment for docker-compose
$env:COMPOSE_FILE = "docker-compose.yml:docker-compose.dev.yml"

# Run the regular start script but override with our development compose file
Write-Host "Using development configuration with auto-reload"
& "$PSScriptRoot/start.ps1"

# Check if containers started successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Development server started with auto-reload enabled!"
    Write-Host "Any changes to Python files in ./app or ./scripts will trigger an automatic reload."
    Write-Host ""
    Write-Host "To view logs: docker compose logs -f app"
    Write-Host "To stop: $PSScriptRoot/stop.ps1"
    Write-Host ""
} 