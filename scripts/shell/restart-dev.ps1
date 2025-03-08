# PowerShell script to restart Thunder Buddy in development mode
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

# Development restart script - stops containers and restarts in development mode
$ErrorActionPreference = "Stop"

Write-Host "Restarting Thunder Buddy API in development mode..."

# Stop running containers using stop.ps1
Write-Host "Stopping running containers..."
& "$PSScriptRoot/stop.ps1"

# Start containers in development mode
Write-Host "Starting in development mode with auto-reload..."
& "$PSScriptRoot/dev.ps1" 