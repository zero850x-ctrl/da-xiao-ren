#!/bin/bash
# Script to check for OpenClaw updates and install if available
echo "$(date): Checking for OpenClaw updates..." >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log

# Change to the OpenClaw workspace directory
cd /Users/gordonlui/.openclaw/workspace

# Check for updates
UPDATE_AVAILABLE=$(openclaw version --check 2>&1)

if [[ "$UPDATE_AVAILABLE" == *"update available"* ]] || [[ "$UPDATE_AVAILABLE" == *"Upgrade available"* ]]; then
    echo "$(date): Update found. Installing..." >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log
    
    # Attempt to update OpenClaw
    UPDATE_RESULT=$(openclaw update 2>&1)
    
    if [[ $? -eq 0 ]]; then
        echo "$(date): OpenClaw updated successfully." >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log
        
        # Restart the OpenClaw service to apply updates
        openclaw gateway restart
        
        echo "$(date): OpenClaw service restarted after update." >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log
    else
        echo "$(date): Failed to update OpenClaw: $UPDATE_RESULT" >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log
    fi
else
    echo "$(date): No updates available." >> /Users/gordonlui/.openclaw/workspace/logs/update_check.log
fi