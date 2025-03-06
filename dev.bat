@echo off
REM Launcher script for dev.bat
REM This script is maintained for backward compatibility

REM Execute the actual implementation in scripts/shell directory
call "%~dp0scripts\shell\dev.bat" %* 