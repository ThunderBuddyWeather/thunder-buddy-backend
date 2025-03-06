@echo off
REM Development restart script - stops containers and restarts in development mode

echo Restarting Thunder Buddy API in development mode...

REM Stop running containers using stop.bat
echo Stopping running containers...
call %~dp0stop.bat

REM Start containers in development mode
echo Starting in development mode with auto-reload...
call %~dp0dev.bat 