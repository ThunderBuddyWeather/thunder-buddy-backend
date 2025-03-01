#!/bin/bash

echo "Restarting Thunder Buddy services..."

# Execute stop.sh
echo "Stopping services..."
./stop.sh

# Execute start.sh
echo "Starting services..."
./start.sh

echo "Restart completed successfully!" 