# PowerShell script to stop Thunder Buddy on Windows
$ErrorActionPreference = "Stop"

Write-Host "Stopping Thunder Buddy containers..."
docker compose down

Write-Host "Thunder Buddy has been stopped." 