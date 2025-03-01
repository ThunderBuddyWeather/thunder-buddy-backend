#!/bin/bash
# Launcher script for rebuild.sh
# This script is maintained for backward compatibility

# Execute the actual implementation in scripts/shell directory
"$(dirname "$0")/scripts/shell/rebuild.sh" "$@" 