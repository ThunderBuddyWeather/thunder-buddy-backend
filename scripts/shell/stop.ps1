# PowerShell script to stop Thunder Buddy on Windows
$ErrorActionPreference = "Stop"

# Source environment variables to ensure proper container names
if (Test-Path -Path ".env.local") {
    Get-Content ".env.local" | ForEach-Object {
        if (-not $_.StartsWith("#") -and $_.Contains("=")) {
            # Only process lines that are valid variable assignments
            if ($_ -match "^[a-zA-Z_][a-zA-Z0-9_]*=.+") {
                $key, $value = $_.Split("=", 2)
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
}

Write-Host "Stopping Docker containers..."
docker compose down --remove-orphans

Write-Host "Cleaning up any dangling containers..."
docker container prune -f

Write-Host "Services stopped successfully" 