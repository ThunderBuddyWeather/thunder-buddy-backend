@echo off
setlocal enabledelayedexpansion

REM Print section header function
:print_header
echo ----------------------------------------
echo %~1
echo ----------------------------------------
goto :eof

REM Source environment variables
if exist .env.local (
    echo Loading environment variables from .env.local
    for /f "tokens=*" %%a in (.env.local) do (
        set line=%%a
        if not "!line:~0,1!"=="#" (
            if "!line:~0,1!" NEQ "" (
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

REM Stop running containers
call :print_header "Stopping containers"
call %~dp0stop.bat

REM Remove static volume to ensure fresh swagger.yaml
call :print_header "Removing static volume"
docker volume rm thunder_buddy_static 2>nul || echo Volume not found, continuing...

REM Rebuild the image
call :print_header "Rebuilding Docker image"
docker compose build app

REM Start services
call :print_header "Starting services"
call %~dp0start.bat

endlocal 