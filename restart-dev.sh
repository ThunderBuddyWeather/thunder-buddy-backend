#!/bin/bash
# Launcher script for restart-dev.sh
# This script is maintained for backward compatibility

# Execute the actual implementation in scripts/shell directory
"$(dirname "$0")/scripts/shell/restart-dev.sh" "$@" 