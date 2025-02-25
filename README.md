# ThunderBuddyApp

Mobile application for tracking extreme weather events and notifying friends and family that you are safe.

## Table of Contents

- [Thunder Buddy Backend](#thunder-buddy-backend)
  - [Key Features](#key-features)
  - [Technical Stack](#technical-stack)
  - [Architecture](#architecture)
  - [Performance Features](#performance-features)
- [Docker Setup Instructions](#docker-setup-instructions)
  - [Why Containerization?](#why-containerization)
  - [For Mac Users](#for-mac-users)
  - [For Windows Users](#for-windows-users)
  - [Running the Application Locally](#running-the-application-locally)
  - [Troubleshooting](#troubleshooting)
  - [Development Best Practices](#development-best-practices)
- [Environment Variables](#environment-variables)
  - [Setting Up Environment Variables](#setting-up-environment-variables)
  - [Loading Environment Variables](#loading-environment-variables)
  - [Verifying Environment Variables](#verifying-environment-variables)
  - [Using Start/Stop Scripts](#using-startstop-scripts)
- [Local Development Guide](#local-development-guide)
  - [Container Architecture](#container-architecture)
  - [Connecting to the Database](#connecting-to-the-database)
  - [API Development Workflow](#api-development-workflow)
  - [Swagger Documentation Automation](#swagger-documentation-automation)
  - [Connecting to Remote Environments](#connecting-to-remote-environments)
  - [Common Development Tasks](#common-development-tasks)
- [Windows-Specific Development Guide](#windows-specific-development-guide)
  - [Setting Up WSL 2 (Recommended)](#setting-up-wsl-2-recommended)
  - [Windows Path and File Permissions](#windows-path-and-file-permissions)
  - [Windows PowerShell Tips](#windows-powershell-tips)
  - [Windows Troubleshooting](#windows-troubleshooting)
  - [Using Windows Terminal (Recommended)](#using-windows-terminal-recommended)

## Thunder Buddy Backend

The Thunder Buddy Backend is a robust, scalable REST API service built with modern architecture and best practices. It powers the Thunder Buddy mobile application by providing real-time weather alerts, user management, and safety notification features.

### Key Features

- Real-time weather event tracking and alerts
- User authentication and authorization
- Friend/family network management
- Push notification system for safety status updates via OneSignal
- Geolocation-based weather monitoring
- Historical weather data analytics

### Technical Stack

- **Framework**: Flask for robust web API development
- **Database**: PostgreSQL for reliable data persistence
- **Authentication**: Session-based authentication
- **Documentation**: OpenAPI (Swagger) for API documentation
- **Containerization**: Docker for consistent development and deployment
- **Weather Data**: Integration with Weatherbit API
- **Push Notifications**: OneSignal for cross-platform push notifications

### Architecture

- Monolithic architecture with modular design for maintainability
- RESTful API design principles
- Containerized application for easy deployment
- Automated CI/CD pipeline
- Comprehensive test coverage
- Designed with clear separation of concerns for potential future service decomposition

### Performance Features

- Configurable request timeouts for external API calls
- Database connection pooling via SQLAlchemy
- Containerized deployment for consistent performance
- Health check endpoints for monitoring system status
- Optimized Docker configuration with Alpine-based images

## Docker Setup Instructions

### Why Containerization?

Thunder Buddy uses Docker containerization to provide numerous benefits for both development and deployment:

#### Development Benefits

- **Consistent Environment**: Every developer works with identical dependencies, eliminating "works on my machine" problems
- **Simplified Onboarding**: New team members can start development in minutes rather than hours
- **Isolated Dependencies**: The application's dependencies are isolated from the host system, preventing version conflicts
- **Parallel Projects**: Work on multiple projects with different dependency versions without conflicts
- **Cross-Platform Compatibility**: The same containers work identically on macOS, Windows, and Linux

#### Operational Benefits

- **Deployment Consistency**: The same container image runs in development, testing, and production
- **Infrastructure as Code**: Docker Compose defines the entire application stack in a version-controlled file
- **Resource Efficiency**: Containers share OS resources while maintaining isolation
- **Scalability**: Easily scale horizontally by deploying more container instances
- **Simplified Updates**: Rolling updates with minimal downtime

#### Workflow Improvements

- **Rapid Iteration**: Make code changes and see them reflected immediately without rebuilding
- **Easy Testing**: Run tests in the same environment that will be used in production
- **Database Management**: Easily reset the database to a clean state or persist data between restarts
- **Service Integration**: Connect to dependent services (like PostgreSQL) without complex local setup
- **Environment Variables**: Manage different configurations through environment files

By using containerization, Thunder Buddy development focuses on writing code rather than managing environments, resulting in faster development cycles and more reliable deployments.

### For Mac Users

1. **Install Docker Desktop for Mac**
   - Visit [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Download the Docker.dmg file
   - Double-click the downloaded file and drag Docker to your Applications folder
   - Open Docker from Applications
   - Wait for Docker to start (you'll see the whale icon in the menu bar)

2. **System Requirements**
   - macOS 12 or newer (Monterey or later)
   - At least 4GB RAM
   - VirtualKit framework or Rosetta 2 for Apple Silicon Macs

3. **Verify Installation**

   ```bash
   docker --version
   docker compose --version
   ```

### For Windows Users

1. **Install Docker Desktop for Windows**
   - Visit [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Download Docker Desktop Installer.exe
   - Run the installer (requires admin privileges)
   - Enable WSL 2 when prompted (recommended)
   - Restart your computer when installation completes

2. **System Requirements**
   - Windows 10/11 Pro, Enterprise, or Education (64-bit)
   - WSL 2 feature enabled
   - 4GB RAM minimum
   - BIOS-level hardware virtualization support must be enabled

3. **Verify Installation**

   ```powershell
   docker --version
   docker compose --version
   ```

### Running the Application Locally

1. **Clone the Repository**

   ```bash
   git clone [repository-url]
   cd thunder-buddy-backend
   ```

2. **Build and Start Containers**

   This command reads the Dockerfile(s) and builds container images for your services.
   It compiles your application, installs dependencies, and creates optimized images
   based on the instructions in your Dockerfile.

   ```bash
   # Build the containers
   docker compose build
   ```

   The `up` command creates and starts all services defined in docker-compose.yml:
   - `-d` flag runs containers in detached mode (background)
   - Creates necessary networks and volumes
   - Starts containers in the correct order based on dependencies
   - Applies environment variables from .env file

   ```bash
   # Start the containers in development mode
   docker compose up -d
   ```

   Shows all currently running containers with useful information:
   - Container ID and Names
   - Image used
   - Current status and uptime
   - Exposed ports
   - Mounted volumes

   ```bash
   # View running containers
   docker ps
   ```

   Displays logs from all containers:
   - `-f` flag follows the log output in real-time
   - Shows application output, errors, and debugging information
   - Color-coded by service for easy reading

   ```bash
   # View logs
   docker compose logs -f
   ```

3. **Stop the Application**

   Stops and removes all containers, networks created by `up`:
   - Preserves named volumes (database data, etc.)
   - Containers are removed, but images remain cached
   - Services can be restarted without rebuilding

   ```bash
   # Stop containers but preserve data
   docker compose down
   ```

   Complete cleanup of your Docker environment:
   - Stops and removes all containers
   - Removes all volumes (including persistent data)
   - Useful for fresh start or when troubleshooting
   - WARNING: This will delete all data in volumes

   ```bash
   # Stop containers and remove volumes (clean slate)
   docker compose down -v
   ```

### Troubleshooting

- **Mac Users**:
  - If Docker Desktop fails to start, ensure you have the latest version
  - Check System Preferences → Security & Privacy if prompted
  - For M1/M2 Macs, ensure Rosetta 2 is installed

- **Windows Users**:
  - Ensure WSL 2 is properly installed and configured
  - Check Windows Features to ensure 'Virtual Machine Platform' is enabled
  - Run PowerShell as Administrator and execute `wsl --update` if needed

### Development Best Practices

- Always pull the latest images before starting development:

  ```bash
  docker compose pull
  ```

- Use `docker compose up -d` for development to run in detached mode
- Monitor logs with `docker compose logs -f [service-name]`
- Clean up unused resources periodically:

  ```bash
  docker system prune
  ```

### Environment Variables

Thunder Buddy uses environment variables for configuration. A template file `.env.example` is provided in the repository.

### Setting Up Environment Variables

1. Copy the example file to create your local environment file:
   ```bash
   cp .env.example .env.local
   ```

2. Edit `.env.local` and update the values with your actual configuration.

### Loading Environment Variables

#### Linux/macOS

You can load the environment variables from `.env.local` using one of these methods:

**Method 1: Using `export` with `grep` and `sed`**
```bash
export $(grep -v '^#' .env.local | xargs)
```

**Method 2: Using `source` with a helper script**
```bash
# Create a helper script
cat > load_env.sh << 'EOF'
#!/bin/bash
set -a
source .env.local
set +a
EOF

# Make it executable
chmod +x load_env.sh

# Source it
source ./load_env.sh
```

**Method 3: Using `direnv` (recommended for development)**
```bash
# Install direnv (if not already installed)
# macOS:
brew install direnv

# Ubuntu/Debian:
sudo apt-get install direnv

# Create .envrc file
echo "dotenv .env.local" > .envrc

# Allow the directory
direnv allow
```

#### Windows

**Method 1: Using PowerShell**
```powershell
# Create and run a helper script
$envFile = ".env.local"
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($name -and $value) {
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}
```

**Method 2: Using Command Prompt (batch file)**
```batch
@echo off
for /f "tokens=*" %%a in (.env.local) do (
    set line=%%a
    if not "!line:~0,1!"=="#" (
        if "!line:~0,1!" NEQ "" (
            for /f "tokens=1,2 delims==" %%b in ("!line!") do (
                set %%b=%%c
            )
        )
    )
)
```

**Note:** For the batch file method, you need to run your command prompt with `cmd /V:ON` or include `setlocal enabledelayedexpansion` at the beginning of your script to enable delayed expansion.

### Verifying Environment Variables

To verify that your environment variables have been set correctly:

**Linux/macOS:**
```bash
env | grep DB_
```

**Windows PowerShell:**
```powershell
Get-ChildItem Env: | Where-Object { $_.Name -like "DB_*" }
```

**Windows Command Prompt:**
```batch
set DB_
```

### Using Start/Stop Scripts

For convenience, Thunder Buddy provides platform-specific scripts to start and stop the application.

#### On Linux/macOS
```bash
# Start the application (automatically selects available port)
./start.sh

# Stop the application
docker compose down
```

#### On Windows (PowerShell)
```powershell
# Start the application (automatically selects available port)
.\start.ps1

# Stop the application
.\stop.ps1
```

#### On Windows (Command Prompt)
```cmd
# Start the application (automatically selects available port)
start.bat

# Stop the application
stop.bat
```

These scripts provide the following benefits:
- Automatically check for port conflicts (uses port 5000 if available, falls back to 5001)
- Load environment variables from `.env.local`
- Validate required environment variables
- Update the HOST_PORT in your environment file
- Start containers in detached mode
- Provide clear status messages

## Local Development Guide

This section provides detailed instructions for backend developers working with the Thunder Buddy containers locally.

### Container Architecture

The Thunder Buddy backend consists of two main containers:

1. **API Service Container**
   - Flask application serving the REST endpoints
   - Runs on port 5000 by default
   - Auto-reloads when code changes are detected in development mode
   - Swagger UI available at <http://localhost:5000/apidocs>

2. **PostgreSQL Database Container**
   - Persistent data storage
   - Runs on port 5432 by default
   - Data persisted in a Docker volume

### Connecting to the Database

#### Local Development Connection

You can connect to the PostgreSQL database using any database client (pgAdmin, DBeaver, DataGrip, etc.) with these credentials:

```bash
Host: localhost
Port: 5432
Database: thunderbuddy
Username: [from .env file]
Password: [from .env file]
```

For command-line access to the database:

```bash
# Connect to the PostgreSQL container
docker compose exec db psql -U [username] -d thunderbuddy

# Run SQL commands directly
docker compose exec db psql -U [username] -d thunderbuddy -c "SELECT * FROM users LIMIT 5;"

# Import data from SQL file
docker compose exec -T db psql -U [username] -d thunderbuddy < ./path/to/data.sql
```

#### Data Persistence

- **Data Persistence Between Restarts**:
  - When using `docker compose down`, database data is preserved in a named volume
  - When using `docker compose down -v`, all data is deleted (clean slate)
  - Development data persists through regular restarts and rebuilds

- **Database Backup and Restore**:

  ```bash
  # Backup the database
  docker compose exec db pg_dump -U [username] -d thunderbuddy > backup.sql
  
  # Restore from backup
  docker compose exec -T db psql -U [username] -d thunderbuddy < backup.sql
  ```

### API Development Workflow

1. **Code Changes**:
   - Edit code in your local IDE
   - The API container uses volume mounting to reflect changes immediately
   - Flask's debug mode restarts the server automatically when code changes
   - No need to rebuild containers for most code changes

2. **Accessing API Logs**:

   ```bash
   # View API logs
   docker compose logs -f api
   ```

3. **Running Tests**:

   ```bash
   # Run tests inside the container
   docker compose exec api pytest
   
   # Run tests with coverage
   docker compose exec api pytest --cov=app
   ```

4. **Database Migrations**:

   ```bash
   # Create a new migration
   docker compose exec api alembic revision --autogenerate -m "description"
   
   # Run migrations
   docker compose exec api alembic upgrade head
   ```

5. **When to Rebuild or Restart Containers**:

   During development, you'll encounter situations where you need to either rebuild images or restart containers:

   **When to Rebuild Docker Images** (`docker compose build`):
   - After modifying the `Dockerfile` or build configuration
   - When adding new dependencies to `requirements.txt`
   - When changing system-level configurations
   - After updating environment variables that affect the build process

   ```bash
   # Rebuild a specific service
   docker compose build app
   
   # Rebuild all services without using cache (complete rebuild)
   docker compose build --no-cache
   ```

   **When to Restart Containers** (`docker compose restart`):
   - After making configuration changes that aren't automatically detected
   - When services become unresponsive but don't require a full rebuild
   - After manually updating environment variables in `.env.local`
   - When you need to reset the application state without losing data

   ```bash
   # Restart a specific service
   docker compose restart app
   
   # Restart all services
   docker compose restart
   ```

   **When Neither is Needed**:
   - For most code changes during development (Flask's debug mode auto-reloads)
   - When modifying static files or templates
   - When making database changes through migrations
   - When updating documentation or non-executable files

   **Why This Matters**:
   - **Efficiency**: Rebuilding images is time-consuming and unnecessary for most code changes
   - **Data Persistence**: Proper restart practices preserve your development data
   - **Dependency Management**: Ensures all services have the correct dependencies
   - **Debugging**: Helps isolate issues related to configuration vs. code

### Swagger Documentation Automation

Thunder Buddy uses OpenAPI/Swagger for API documentation, with several automation features to ensure documentation stays in sync with the codebase:

1. **Generating Swagger Documentation**:

   ```bash
   # Generate Swagger documentation manually
   make swagger
   ```

2. **Automated Documentation Updates**:
   - **Git Hooks**: Pre-commit hooks automatically update Swagger docs when Python files change
   - **CI Pipeline**: Swagger generation is validated in the CI pipeline
   - **GitHub Actions**: Swagger docs are automatically updated on the main branch

3. **Installing Git Hooks**:

   ```bash
   # For Linux/macOS
   ./scripts/install-hooks.sh
   
   # For Windows (PowerShell)
   ./scripts/install-hooks.ps1
   ```

4. **How It Works**:
   - The system analyzes Flask routes and docstrings to generate OpenAPI specifications
   - Route parameters, response types, and status codes are automatically detected
   - Generated documentation is stored in `static/swagger.yaml`
   - Swagger UI is available at <http://localhost:5000/apidocs> when the app is running

   **Example Docstring Format**:

   ```python
   @app.route("/weather", methods=["GET"])
   def get_weather():
       """Get current weather data for a location.
       
       This endpoint retrieves real-time weather data based on location parameters.
       It returns temperature, conditions, and other meteorological information.
       
       Headers:
           - Accept (optional): Application format (application/json)
           - X-API-Key (required): Your API authentication key
       
       Query Parameters:
           - zip (required): ZIP/postal code for the location
           - country (optional): Country code, defaults to "US"
           - units (optional): Unit system, one of: "metric", "imperial", defaults to "metric"
       
       Returns:
           JSON: Weather data including temperature, conditions, and forecast
               - 200: Successful response with weather data
               - 400: Bad request when parameters are invalid
               - 401: Unauthorized when API key is missing or invalid
               - 500: Server error when weather service is unavailable
       """
       # Check for API key
       api_key = request.headers.get("X-API-Key")
       if not api_key:
           return jsonify({"error": "API key is required"}), 401
       
       # Get and validate parameters
       zip_code = request.args.get("zip", None)
       country = request.args.get("country", "US")
       units = request.args.get("units", "metric")
       
       if not zip_code:
           return jsonify({"error": "ZIP code is required"}), 400
           
       if units not in ["metric", "imperial"]:
           return jsonify({"error": "Units must be either 'metric' or 'imperial'"}), 400
           
       # ... implementation ...
       
       return jsonify(weather_data)
   ```

   The generator will extract:
   - Endpoint summary from the first line of the docstring
   - Detailed description from the rest of the docstring
   - Headers from the "Headers" section and `request.headers.get()` calls
   - Parameters from the "Query Parameters" section and `request.args.get()` calls
   - Response types from return statements and docstring "Returns" section
   - Status codes (200, 400, 401, 500) from the docstring and return statements

   **Example with Path Parameters and Request Body**:

   ```python
   @app.route("/users/<user_id>/alerts", methods=["POST"])
   def create_user_alert(user_id):
       """Create a new weather alert for a specific user.
       
       This endpoint creates a customized weather alert for the specified user.
       The alert will notify the user when weather conditions match their criteria.
       
       Headers:
           - Content-Type (required): Must be application/json
           - Authorization (required): Bearer token for authentication
           - X-Client-Version (optional): Client application version
       
       Path Parameters:
           - user_id (str, required): The unique identifier of the user
       
       Request Body:
           - alert_type (str, required): Type of weather alert (rain, snow, extreme)
           - threshold (float, required): Numerical threshold to trigger the alert
           - location (dict, required): Location information with keys:
               - zip (str, required): ZIP/postal code
               - country (str, optional): Country code, defaults to US
           - notify_contacts (bool, optional): Whether to notify emergency contacts, defaults to false
           - expiration (str, optional): ISO 8601 date when the alert expires
       
       Example Request:
           ```json
           {
               "alert_type": "extreme",
               "threshold": 95.5,
               "location": {
                   "zip": "90210",
                   "country": "US"
               },
               "notify_contacts": true,
               "expiration": "2023-12-31T23:59:59Z"
           }
           ```
       
       Returns:
           JSON: The created alert object with status information
               - 201: Alert successfully created
               - 400: Invalid request parameters
               - 401: Unauthorized, missing or invalid token
               - 403: Forbidden, insufficient permissions
               - 404: User not found
               - 500: Server error
       
       Example Response (201):
           ```json
           {
               "id": "alert_12345",
               "user_id": "user_789",
               "alert_type": "extreme",
               "threshold": 95.5,
               "location": {
                   "zip": "90210",
                   "country": "US"
               },
               "status": "active",
               "created_at": "2023-06-15T14:22:10Z"
           }
           ```
       """
       # Validate authorization
       auth_header = request.headers.get("Authorization")
       if not auth_header or not auth_header.startswith("Bearer "):
           return jsonify({"error": "Valid Bearer token required"}), 401
       
       # Parse request body
       data = request.get_json()
       if not data:
           return jsonify({"error": "Request body must be valid JSON"}), 400
       
       # Validate required fields
       if "alert_type" not in data:
           return jsonify({"error": "alert_type is required"}), 400
       if "threshold" not in data:
           return jsonify({"error": "threshold is required"}), 400
       if "location" not in data or "zip" not in data["location"]:
           return jsonify({"error": "location with zip is required"}), 400
       
       # Implementation details...
       return jsonify(new_alert), 201
   ```

5. **Benefits**:
   - Documentation always stays in sync with code
   - Reduces manual documentation effort
   - Provides a consistent interface for API consumers
   - Enables API-first development practices

### Connecting to Remote Environments

#### Connecting to Remote Database

For accessing the deployed database in staging/production environments:

1. **SSH Tunnel Method** (Recommended for security):

   ```bash
   # Create SSH tunnel to remote database
   ssh -L 5433:localhost:5432 user@remote-server
   
   # Then connect locally to port 5433
   psql -h localhost -p 5433 -U [username] -d thunderbuddy
   ```

2. **Direct Connection** (If VPN/firewall rules allow):
   - Use your database client with the remote credentials provided by your DevOps team
   - Always use SSL mode for secure connections

#### Interacting with Remote API

1. **Swagger Documentation**:
   - Access the remote API documentation at <https://api.thunderbuddy.example.com/apidocs>

2. **API Testing**:

   ```bash
   # Using curl
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.thunderbuddy.example.com/users
   
   # Using httpie (more readable)
   http GET https://api.thunderbuddy.example.com/users "Authorization: Bearer YOUR_TOKEN"
   ```

### Common Development Tasks

- **Rebuilding Containers After Dependencies Change**:

  ```bash
  docker compose build --no-cache
  docker compose up -d
  ```

- **Viewing Container Resource Usage**:

  ```bash
  docker stats
  ```

- **Debugging Database Performance**:

  ```bash
  # Connect to database and analyze query performance
  docker compose exec db psql -U [username] -d thunderbuddy -c "EXPLAIN ANALYZE SELECT * FROM users WHERE email LIKE '%example.com';"
  ```

- **Accessing Container Shell**:

  ```bash
  # API container shell
  docker compose exec api bash
  
  # Database container shell
  docker compose exec db bash
  ```

### Windows-Specific Development Guide

#### Setting Up WSL 2 (Recommended)

WSL 2 (Windows Subsystem for Linux 2) provides better performance for Docker on Windows:

1. **Enable WSL 2 in Windows Features**
   ```powershell
   # Run in PowerShell as Administrator
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. **Restart your computer**

3. **Install WSL 2 Linux kernel update**
   - Download and install the [WSL 2 Linux kernel update package](https://aka.ms/wsl2kernel)

4. **Set WSL 2 as default**
   ```powershell
   wsl --set-default-version 2
   ```

5. **Install a Linux distribution from Microsoft Store**
   - Ubuntu 20.04 LTS is recommended

6. **Verify WSL 2 installation**
   ```powershell
   wsl -l -v
   ```

#### Windows Path and File Permissions

When working with Docker on Windows, be aware of these path and permission considerations:

1. **Path Length Limitations**
   - Windows has a 260-character path length limit
   - Place your project in a short path (e.g., `C:\Dev\thunder-buddy`)
   - Use WSL 2 to avoid path length issues

2. **File Permissions**
   - Windows and Linux handle file permissions differently
   - When using volume mounts, you may encounter permission issues
   - Solution: Use WSL 2 backend for Docker Desktop

3. **Line Endings**
   - Configure Git to handle line endings properly:
     ```powershell
     git config --global core.autocrlf input
     ```
   - Add a `.gitattributes` file to your project:
     ```
     # Set default behavior to automatically normalize line endings
     * text=auto
     
     # Explicitly declare text files to be normalized
     *.py text
     *.md text
     *.yml text
     *.yaml text
     *.json text
     *.sh text eol=lf
     *.bat text eol=crlf
     *.ps1 text eol=crlf
     ```

#### Windows PowerShell Tips

1. **Running Scripts**
   - By default, PowerShell restricts running scripts
   - To allow script execution:
     ```powershell
     # Run as Administrator
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

2. **PowerShell Profiles**
   - Create a PowerShell profile to automate environment setup:
     ```powershell
     # Check if profile exists
     Test-Path $PROFILE
     
     # Create profile if it doesn't exist
     if (!(Test-Path $PROFILE)) {
         New-Item -Type File -Path $PROFILE -Force
     }
     
     # Edit profile
     notepad $PROFILE
     ```
   
   - Add these lines to your profile:
     ```powershell
     # Function to load .env.local file
     function Load-EnvLocal {
         param (
             [string]$envFile = ".env.local"
         )
         if (Test-Path $envFile) {
             Get-Content $envFile | ForEach-Object {
                 if ($_ -match '^([^#][^=]+)=(.*)$') {
                     $name = $matches[1].Trim()
                     $value = $matches[2].Trim()
                     if ($name -and $value) {
                         [Environment]::SetEnvironmentVariable($name, $value, "Process")
                         Write-Host "Set $name"
                     }
                 }
             }
             Write-Host "Environment variables loaded from $envFile"
         } else {
             Write-Host "Environment file $envFile not found"
         }
     }
     
     # Function to start Thunder Buddy
     function Start-ThunderBuddy {
         $projectPath = "C:\path\to\thunder-buddy-backend"
         if (Test-Path $projectPath) {
             Set-Location $projectPath
             & .\start.ps1
         } else {
             Write-Host "Thunder Buddy project not found at $projectPath"
         }
     }
     ```

#### Windows Troubleshooting

1. **Docker Desktop Won't Start**
   - Ensure Hyper-V and WSL 2 are properly enabled
   - Check Windows Features to verify 'Virtual Machine Platform' is enabled
   - Run PowerShell as Administrator and execute:
     ```powershell
     wsl --update
     ```
   - Restart Docker Desktop with admin privileges

2. **Port Conflicts**
   - Windows may have services using common ports (80, 443, 5000)
   - Check for port conflicts:
     ```powershell
     netstat -ano | findstr :5000
     ```
   - Find the process using a port:
     ```powershell
     Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess
     ```
   - Configure the application to use alternative ports in `.env.local`

3. **Performance Issues**
   - Ensure Docker Desktop is using WSL 2 backend
   - Allocate more resources to Docker in Settings
   - Exclude Docker directories from Windows Defender scanning
   - Add these directories to Windows Defender exclusions:
     - `%LOCALAPPDATA%\Docker`
     - `%PROGRAMDATA%\Docker`
     - Your project directory

4. **Windows Firewall Blocking Connections**
   - Check if Windows Firewall is blocking Docker connections
   - Add Docker to allowed applications in Windows Firewall
   - Run as Administrator:
     ```powershell
     New-NetFirewallRule -DisplayName "Docker Engine" -Direction Inbound -Program "C:\Program Files\Docker\Docker\resources\dockerd.exe" -Action Allow
     ```

#### Using Windows Terminal (Recommended)

Windows Terminal provides a better experience for working with Docker and WSL:

1. **Install Windows Terminal**
   - Install from [Microsoft Store](https://aka.ms/terminal)
   - Or install with PowerShell:
     ```powershell
     winget install Microsoft.WindowsTerminal
     ```

2. **Configure Windows Terminal for Docker Development**
   - Open Settings (Ctrl+,)
   - Add a new profile for your WSL distribution
   - Configure the starting directory to your project folder

3. **Create a Custom Command Palette**
   - Add custom commands to your `settings.json`:
     ```json
     "actions": [
         {
             "name": "Start Thunder Buddy",
             "command": "wsl -d Ubuntu-20.04 -e bash -c 'cd /path/to/thunder-buddy-backend && ./start.sh'",
             "keys": "ctrl+shift+t"
         },
         {
             "name": "Stop Thunder Buddy",
             "command": "wsl -d Ubuntu-20.04 -e bash -c 'cd /path/to/thunder-buddy-backend && docker compose down'",
             "keys": "ctrl+shift+s"
         }
     ]
     ```
