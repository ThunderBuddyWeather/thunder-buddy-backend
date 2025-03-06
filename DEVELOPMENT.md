# Development Guide

This guide explains how to run the Thunder Buddy API in development mode with auto-reload enabled.

## Quick Start

To start the application in development mode with auto-reload:

```bash
./dev.sh
```

This script:

1. Creates `.env.local` from `.env` if it doesn't exist and adds development variables
2. Sets up Docker Compose to use both the main config and development overrides
3. Runs the standard `start.sh` script with development configuration enabled

## Development Scripts

The following scripts are available for development:

| Script | Description |
|--------|-------------|
| `./dev.sh` | Start the application in development mode with auto-reload |
| `./restart-dev.sh` | Stop running containers and restart in development mode |
| `./rebuild-dev.sh` | Rebuild Docker images from scratch and restart in development mode |
| `./stop.sh` | Stop all running containers |

Use `rebuild-dev.sh` when:

- You've made changes to the Dockerfile
- You've updated dependencies in requirements.txt
- You're experiencing strange behavior that might be caused by cached Docker layers

## How Auto-Reload Works

When running in development mode:

1. Local code directories are mounted into the container through `docker-compose.dev.yml`:
   - `./app` → `/app/app`
   - `./run.py` → `/app/run.py`
   - `./scripts` → `/app/scripts`

2. When you modify any Python file in these directories, Flask will detect the change and automatically restart the server.

3. You'll see the reload message in the logs: `* Detected change in '/app/app/...'` followed by `* Restarting with stat`.

## Viewing Logs

Since the containers run in detached mode, you can view the logs with:

```bash
docker compose logs -f app
```

## Manual Setup

If you prefer not to use the script, you can start development mode manually:

```bash
# Set up the compose files to use
export COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

# Use the standard start script
./start.sh
```

## Stopping the Application

Use the standard stop script:

```bash
./stop.sh
```

## Troubleshooting

If auto-reload isn't working:

1. Make sure the environment variable `COMPOSE_FILE` includes `docker-compose.dev.yml`
2. Check container logs for any errors: `docker compose logs app`
3. Verify that the volumes are correctly mounted: `docker compose exec app ls -la /app`
4. Ensure that your `.env.local` file has `FLASK_DEBUG=1` and `FLASK_ENV=development`
5. Try completely rebuilding the container: `./rebuild-dev.sh`

## Production vs Development

- **Development**: Uses volume mounts to sync code changes for auto-reload
- **Production**: Copies code into the container at build time for security and stability
