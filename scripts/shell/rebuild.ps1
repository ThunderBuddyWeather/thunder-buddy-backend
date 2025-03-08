# PowerShell script to rebuild Thunder Buddy on Windows
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

$ErrorActionPreference = "Stop"

# Print section header function
function Print-Header {
    param (
        [string]$title
    )
    Write-Host "----------------------------------------"
    Write-Host $title
    Write-Host "----------------------------------------"
}

# Source environment variables
if (Test-Path -Path ".env.local") {
    Write-Host "Loading environment variables from .env.local"
    Get-Content ".env.local" | ForEach-Object {
        if (-not $_.StartsWith("#") -and $_.Contains("=")) {
            # Only process lines that are valid variable assignments
            if ($_ -match "^[a-zA-Z_][a-zA-Z0-9_]*=.+") {
                $key, $value = $_.Split("=", 2)
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
                # Also set in current PowerShell session
                Set-Item -Path "env:$key" -Value $value
            }
        }
    }
}

# Stop running containers
Print-Header "Stopping containers"
& "$PSScriptRoot/stop.ps1"

# Remove static volume to ensure fresh swagger.yaml
Print-Header "Removing static volume"
docker volume rm thunder_buddy_static -f 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Volume not found, continuing..."
}

# Rebuild the image
Print-Header "Rebuilding Docker image"
docker compose build app

# Start services
Print-Header "Starting services"
& "$PSScriptRoot/start.ps1" 