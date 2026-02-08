#!/bin/bash
# Script to check WhatsApp connection status and restart if disconnected

# Check if OpenClaw gateway is running
if ! pgrep -f "openclaw.*gateway" > /dev/null; then
    openclaw gateway start
    sleep 10
fi

# Check the current status of WhatsApp channel
STATUS_OUTPUT=$(openclaw status 2>&1)
WHATSAPP_STATUS=$(echo "$STATUS_OUTPUT" | grep -i whatsapp)

if [[ "$WHATSAPP_STATUS" != *"OK"* ]]; then
    # Restart the WhatsApp service
    openclaw gateway restart
    sleep 15
fi