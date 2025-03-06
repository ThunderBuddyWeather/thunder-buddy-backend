#!/bin/bash
# Launcher script for start-dev.sh
set -e

# Execute the actual script from the scripts/shell directory
"$(dirname "$0")/../scripts/shell/start-dev.sh" "$@" 