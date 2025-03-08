# PowerShell script to stop Thunder Buddy on Windows
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