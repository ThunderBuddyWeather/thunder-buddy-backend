# PowerShell wrapper script for restart-dev.ps1
# This script is maintained for consistency with the architecture pattern
#
# ARCHITECTURE INFO:
# This is a wrapper script that provides a simple entry point in the bin/ directory.
# The actual implementation resides in scripts/shell/restart-dev.ps1.
# 
# This separation allows:
# - Consistent user interface through the bin/ directory
# - Platform-specific implementations (.sh, .bat, .ps1)
# - Better organization and maintainability
# - Backward compatibility if implementation details change

# Get the directory of the current script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Execute the actual implementation in scripts/shell directory
& "$scriptDir\..\scripts\shell\restart-dev.ps1" @args 