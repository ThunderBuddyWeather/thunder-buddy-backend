# PowerShell script to restart Thunder Buddy on Windows
$ErrorActionPreference = "Stop"

Write-Host "Restarting Thunder Buddy services..."

# Execute stop.ps1
Write-Host "Stopping services..."
& "$PSScriptRoot/stop.ps1"

# Execute start.ps1
Write-Host "Starting services..."
& "$PSScriptRoot/start.ps1"

Write-Host "Restart completed successfully!" 