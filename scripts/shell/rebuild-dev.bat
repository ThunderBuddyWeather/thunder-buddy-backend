@echo off
REM Development rebuild script - rebuilds Docker images and restarts in development mode
setlocal enabledelayedexpansion

echo Rebuilding Thunder Buddy API in development mode...

REM Stop running containers using stop.bat
echo Stopping running containers...
call %~dp0stop.bat

REM Remove existing Docker images to force complete rebuild
echo Removing existing Docker images to force rebuild...
docker compose down --rmi local

REM Set development environment for docker-compose
set COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

REM Build images explicitly with no cache to ensure clean build
echo Building Docker images from scratch (no cache)...
docker compose build --no-cache app

REM Start containers in development mode
echo Starting in development mode...
call %~dp0start-dev.bat

endlocal 