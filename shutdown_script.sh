#!/bin/bash
# Daily shutdown script
# This script will be called by the cron job to shut down the computer

# Log the shutdown event
echo "$(date): Initiating scheduled shutdown" >> /Users/gordonlui/.openclaw/workspace/logs/shutdown.log

# Attempt to shut down the system
# Note: This may require additional configuration to run with proper privileges
osascript -e 'tell app "System Events" to shut down'

# Close Chrome if running
osascript -e 'tell application "Google Chrome" to quit'

# Stop OpenClaw service if needed
# This would need to be configured based on your OpenClaw installation