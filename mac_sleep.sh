#!/bin/bash
# Script to put Mac to sleep at night
echo "$(date): Putting Mac to sleep" >> /Users/gordonlui/.openclaw/workspace/logs/mac_schedule.log
# Put Mac to sleep
osascript -e 'tell application "Finder" to sleep'