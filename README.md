# ThunderBuddyApp

Mobile application for tracking extreme weather events and notifying friends and family that you are safe.

## Thunder Buddy Backend

The Thunder Buddy Backend is a robust, scalable REST API service built with modern architecture and best practices. It powers the Thunder Buddy mobile application by providing real-time weather alerts, user management, and safety notification features.

### Key Features

- Real-time weather event tracking and alerts
- User authentication and authorization
- Friend/family network management
- Push notification system for safety status updates
- Geolocation-based weather monitoring
- Historical weather data analytics

### Technical Stack

- **Framework**: FastAPI for high-performance async operations
- **Database**: PostgreSQL for reliable data persistence
- **Authentication**: JWT-based secure authentication
- **Documentation**: OpenAPI (Swagger) for API documentation
- **Containerization**: Docker for consistent development and deployment
- **Weather Data**: Integration with multiple weather service providers

### Architecture

- Microservices-based architecture for scalability
- RESTful API design principles
- Event-driven architecture for real-time updates
- Containerized services for easy deployment
- Automated CI/CD pipeline
- Comprehensive test coverage

### Performance Features

- Optimized database queries
- Efficient caching strategies
- Asynchronous task processing
- Load balancing ready
- Horizontal scaling capability

## Docker Setup Instructions

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

Make sure to create a `.env` file in the project root with the necessary environment variables before starting the containers. See `.env.example` for required variables.

## Local Development Guide

This section provides detailed instructions for backend developers working with the Thunder Buddy containers locally.

### Container Architecture

The Thunder Buddy backend consists of two main containers:

1. **API Service Container**
   - FastAPI application serving the REST endpoints
   - Runs on port 8000 by default
   - Auto-reloads when code changes are detected
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
   - FastAPI's auto-reload feature restarts the server automatically
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
