#!/bin/bash

echo "Restarting Thunder Buddy services..."

# Execute stop.sh
echo "Stopping services..."
"$(dirname "$0")/stop.sh"

# Execute start.sh
echo "Starting services..."
"$(dirname "$0")/start.sh"

echo "Restart completed successfully!" 