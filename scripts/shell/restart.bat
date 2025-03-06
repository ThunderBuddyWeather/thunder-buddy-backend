@echo off
echo Restarting Thunder Buddy services...

REM Execute stop.bat
echo Stopping services...
call %~dp0stop.bat

REM Execute start.bat
echo Starting services...
call %~dp0start.bat

echo Restart completed successfully! 