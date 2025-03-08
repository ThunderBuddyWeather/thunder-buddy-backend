# PowerShell script to start Thunder Buddy on Windows
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
# Set error action preference to stop on any error
$ErrorActionPreference = "Stop"

# Check if .env file exists
if (-not (Test-Path -Path ".env.local") -and -not (Test-Path -Path ".env")) {
    Write-Error "Error: No .env file found. Please create .env.local or .env file"
    Write-Host "You can copy .env.example as a template"
    exit 1
}

# Load environment variables from .env.local
if (Test-Path -Path ".env.local") {
    Write-Host "Loading environment variables from .env.local"
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

# Check for required environment variables
$requiredVars = @("POSTGRES_PASSWORD", "DB_PASSWORD", "DOCKER_USERNAME")
$missingVars = 0

foreach ($var in $requiredVars) {
    if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($var))) {
        Write-Error "Error: $var is not set in environment"
        $missingVars = 1
    }
}

if ($missingVars -eq 1) {
    Write-Error "Please set all required environment variables and try again"
    exit 1
}

# Check if port 5000 is available
$portAvailable = $true
try {
    $testConnection = New-Object System.Net.Sockets.TcpClient
    $testConnection.Connect("localhost", 5000)
    $testConnection.Close()
    $portAvailable = $false
} catch {
    $portAvailable = $true
}

if (-not $portAvailable) {
    Write-Host "Port 5000 is already in use. Using port 5001 instead."
    [Environment]::SetEnvironmentVariable("HOST_PORT", "5001", "Process")
} else {
    Write-Host "Port 5000 is available. Using it."
    [Environment]::SetEnvironmentVariable("HOST_PORT", "5000", "Process")
}

# Update .env.local with the selected port
$envContent = Get-Content ".env.local"
$envContent = $envContent -replace "HOST_PORT=.*", "HOST_PORT=$([Environment]::GetEnvironmentVariable('HOST_PORT'))"
$envContent | Set-Content ".env.local"

# Export environment variables for docker compose
$env:DOCKER_USERNAME = [Environment]::GetEnvironmentVariable("DOCKER_USERNAME")
$env:DB_PASSWORD = [Environment]::GetEnvironmentVariable("DB_PASSWORD")
$env:POSTGRES_PASSWORD = [Environment]::GetEnvironmentVariable("POSTGRES_PASSWORD")
$env:HOST_PORT = [Environment]::GetEnvironmentVariable("HOST_PORT")

# Start the containers
Write-Host "Stopping any existing containers..."
docker compose down

Write-Host "Starting containers..."
docker compose up -d

Write-Host "Thunder Buddy is now running on http://localhost:$($env:HOST_PORT)" 