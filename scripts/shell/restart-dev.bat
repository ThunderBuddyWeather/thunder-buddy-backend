@echo off
REM Development restart script - stops containers and restarts in development mode

echo Restarting Thunder Buddy API in development mode...

REM Stop running containers using stop.bat
echo Stopping containers...
docker-compose -f docker-compose.dev.yml down

REM Start containers in development mode
echo Starting in development mode...
call %~dp0start-dev.bat 