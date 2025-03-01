@echo off
REM Launcher script for start.bat
REM This script is maintained for backward compatibility

REM Execute the actual implementation in scripts/shell directory
call "%~dp0scripts\shell\start.bat" %* 