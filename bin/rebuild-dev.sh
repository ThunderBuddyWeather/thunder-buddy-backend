#!/bin/bash
# Launcher script for rebuild-dev.sh
# This script is maintained for backward compatibility

# Execute the actual implementation in scripts/shell directory
"$(dirname "$0")/../scripts/shell/rebuild-dev.sh" "$@" 