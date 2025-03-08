@echo off
:: Launcher script for stop.bat
:: This script is maintained for backward compatibility
::
:: ARCHITECTURE INFO:
:: This is a wrapper script that provides a simple entry point in the bin/ directory.
:: The actual implementation resides in scripts/shell/stop.bat.
:: 
:: This separation allows:
:: - Consistent user interface through the bin/ directory
:: - Platform-specific implementations (.sh, .bat, .ps1)
:: - Better organization and maintainability
:: - Backward compatibility if implementation details change

:: Execute the actual implementation in scripts/shell directory
"%~dp0..\scripts\shell\stop.bat" %* 