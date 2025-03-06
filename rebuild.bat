@echo off
REM Launcher script for rebuild.bat
REM This script is maintained for backward compatibility

REM Execute the actual implementation in scripts/shell directory
call "%~dp0scripts\shell\rebuild.bat" %* 