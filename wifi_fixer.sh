#!/bin/bash

# WiFi Auto-Fixer Script for Hidden Networks

export PATH="/usr/sbin:/sbin:$PATH"

INTERFACE=$(networksetup -listallhardwareports | grep -A 1 Wi-Fi | tail -n 1 | awk '{print $2}')
echo "$(date): Checking WiFi connection status..."

CURRENT_NETWORK=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)

if [[ "$CURRENT_NETWORK" == *"not associated"* ]]; then
    echo "$(date): WiFi is disconnected. Attempting to reconnect..."
    
    # Get the list of preferred networks
    PREFERRED_NETWORKS=$(networksetup -listpreferredwirelessnetworks "$INTERFACE" 2>/dev/null | grep -v "Preferred networks on")
    
    # Try to connect to the first available preferred network
    for NETWORK in $PREFERRED_NETWORKS; do
        if [ ! -z "$NETWORK" ]; then
            echo "$(date): Attempting to connect to preferred network: $NETWORK"
            
            # Try connecting without password first (for networks that might have saved credentials)
            networksetup -setairportnetwork "$INTERFACE" "$NETWORK" 2>/dev/null
            
            # Wait a bit to see if it connects
            sleep 10
            NEW_STATUS=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
            
            if [[ "$NEW_STATUS" != *"not associated"* ]]; then
                echo "$(date): Successfully connected to $NETWORK"
                break
            else
                echo "$(date): Failed to connect to $NETWORK without password"
            fi
        fi
    done
    
    # If still not connected, try force-reconnecting
    if [[ "$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)" == *"not associated"* ]]; then
        echo "$(date): Still not connected. Performing WiFi power cycle..."
        
        # Power cycle the WiFi adapter
        networksetup -setairportpower "$INTERFACE" off
        sleep 5
        networksetup -setairportpower "$INTERFACE" on
        sleep 10
        
        # Try preferred networks again
        for NETWORK in $PREFERRED_NETWORKS; do
            if [ ! -z "$NETWORK" ]; then
                echo "$(date): Trying again to connect to: $NETWORK"
                networksetup -setairportnetwork "$INTERFACE" "$NETWORK" 2>/dev/null
                sleep 10
                
                NEW_STATUS=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
                if [[ "$NEW_STATUS" != *"not associated"* ]]; then
                    echo "$(date): Successfully connected to $NETWORK after power cycle"
                    break
                fi
            fi
        done
    fi
else
    echo "$(date): WiFi is connected to: $CURRENT_NETWORK"
fi

FINAL_STATUS=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
if [[ "$FINAL_STATUS" == *"not associated"* ]]; then
    echo "$(date): ERROR: Could not establish WiFi connection"
    exit 1
else
    echo "$(date): SUCCESS: WiFi connection established"
    exit 0
fi