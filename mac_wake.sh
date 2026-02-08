#!/bin/bash
# Script to handle morning wake routine
echo "$(date): Starting morning routine" >> /Users/gordonlui/.openclaw/workspace/logs/mac_schedule.log

# Wait a bit for system to stabilize after waking
sleep 10

# Start Google Chrome
open -a "Google Chrome"

# Wait for Chrome to start
sleep 5

# Ensure OpenClaw browser extension is ready
osascript -e 'tell application "Google Chrome" to activate'

echo "$(date): Morning routine completed" >> /Users/gordonlui/.openclaw/workspace/logs/mac_schedule.log