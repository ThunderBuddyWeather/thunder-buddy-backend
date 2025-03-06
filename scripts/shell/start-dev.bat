@echo off
setlocal enabledelayedexpansion

echo Starting Thunder Buddy API in development mode with auto-reload...

REM Check if .env.local exists
if not exist .env.local (
    echo Creating .env.local from .env...
    copy .env .env.local

    REM Add development-specific variables if they don't exist
    findstr /c:"FLASK_ENV=" .env.local >nul || echo FLASK_ENV=development >> .env.local
    findstr /c:"FLASK_DEBUG=" .env.local >nul || echo FLASK_DEBUG=1 >> .env.local
    findstr /c:"FLASK_APP_RELOAD=" .env.local >nul || echo FLASK_APP_RELOAD=true >> .env.local
)

REM Set development environment for docker-compose
set COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml

REM Run the regular start script but override with our development compose file
echo Using development configuration with auto-reload
call %~dp0start.bat

REM Check if containers started successfully
if %errorlevel% equ 0 (
    echo.
    echo Development server started with auto-reload enabled!
    echo Any changes to Python files in ./app or ./scripts will trigger an automatic reload.
    echo.
    echo To view logs: docker compose logs -f app
    echo To stop: %~dp0stop.bat
    echo.
)

endlocal 