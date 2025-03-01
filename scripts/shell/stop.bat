@echo off
setlocal enabledelayedexpansion

REM Source environment variables to ensure proper container names
if exist .env.local (
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

echo Stopping Docker containers...
docker compose down --remove-orphans

echo Cleaning up any dangling containers...
docker container prune -f

echo Services stopped successfully
endlocal 