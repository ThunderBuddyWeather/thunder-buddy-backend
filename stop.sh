#!/bin/bash
# Launcher script for stop.sh
# This script is maintained for backward compatibility

# Execute the actual implementation in scripts/shell directory
"$(dirname "$0")/scripts/shell/stop.sh" "$@" 