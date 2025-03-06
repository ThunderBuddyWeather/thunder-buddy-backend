@echo off
setlocal enabledelayedexpansion

echo Starting Thunder Buddy...

REM Check if .env file exists
if not exist .env.local (
    if not exist .env (
        echo Error: No .env file found. Please create .env.local or .env file
        echo You can copy .env.example as a template
        exit /b 1
    )
)

REM Load environment variables from .env.local
if exist .env.local (
    echo Loading environment variables from .env.local
    for /f "tokens=*" %%a in (.env.local) do (
        set line=%%a
        if not "!line:~0,1!"=="#" (
            if "!line:~0,1!" NEQ "" (
                REM Check if line contains equal sign and is a valid variable name
                echo !line! | findstr /r /c:"^[a-zA-Z_][a-zA-Z0-9_]*=" >nul
                if !errorlevel! equ 0 (
                    for /f "tokens=1,2 delims==" %%b in ("!line!") do (
                        set %%b=%%c
                    )
                )
            )
        )
    )
)

REM Check for required environment variables
set missing_vars=0
for %%v in (POSTGRES_PASSWORD DB_PASSWORD DOCKER_USERNAME) do (
    if "!%%v!"=="" (
        echo Error: %%v is not set in environment
        set missing_vars=1
    )
)

if "!missing_vars!"=="1" (
    echo Please set all required environment variables and try again
    exit /b 1
)

REM Check if port 5000 is available
netstat -ano | findstr :5000 > nul
if %errorlevel% equ 0 (
    echo Port 5000 is already in use. Using port 5001 instead.
    set HOST_PORT=5001
) else (
    echo Port 5000 is available. Using it.
    set HOST_PORT=5000
)

REM Update .env.local with the selected port
powershell -Command "(Get-Content .env.local) -replace 'HOST_PORT=.*', 'HOST_PORT=%HOST_PORT%' | Set-Content .env.local"

REM Start the containers
echo Stopping any existing containers...
docker compose down

echo Starting containers...
docker compose up -d

echo Thunder Buddy is now running on http://localhost:%HOST_PORT%
endlocal 