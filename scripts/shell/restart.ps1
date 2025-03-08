# PowerShell script to restart Thunder Buddy on Windows
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

Write-Host "Restarting Thunder Buddy services..."

# Execute stop.ps1
Write-Host "Stopping services..."
& "$PSScriptRoot/stop.ps1"

# Execute start.ps1
Write-Host "Starting services..."
& "$PSScriptRoot/start.ps1"

Write-Host "Restart completed successfully!" 