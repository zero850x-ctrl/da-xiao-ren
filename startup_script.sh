#!/bin/bash
# Daily startup script
# This script will be called by the cron job to start applications after boot

# Wait a bit for the system to fully boot
sleep 10

# Log the startup event
echo "$(date): Starting scheduled startup routine" >> /Users/gordonlui/.openclaw/workspace/logs/startup.log

# Start Google Chrome
open -a "Google Chrome"

# Wait a bit for Chrome to start
sleep 5

# Start OpenClaw browser extension connection
# This assumes OpenClaw is installed and can be started via command line
osascript -e 'tell application "Google Chrome" to activate'

# Additional commands to ensure OpenClaw browser extension is ready
# The exact implementation depends on your OpenClaw setup
echo "Startup routine completed at $(date)" >> /Users/gordonlui/.openclaw/workspace/logs/startup.log