@echo off
REM Launcher script for start-dev.bat
REM This script is maintained for backward compatibility

REM Execute the actual script from the scripts/shell directory
call "%~dp0scripts\shell\start-dev.bat" %* 