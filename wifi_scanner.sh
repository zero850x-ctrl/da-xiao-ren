#!/bin/bash

# WiFi Scanner and Auto-Connect Script

# Add common paths for networksetup
export PATH="/usr/sbin:/sbin:$PATH"

echo "Scanning for WiFi networks..."

# Get current WiFi interface
INTERFACE=$(networksetup -listallhardwareports | grep -A 1 Wi-Fi | tail -n 1 | awk '{print $2}')
echo "WiFi Interface: $INTERFACE"

# Check if connected to any network
CURRENT_NETWORK=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
echo "Currently connected to: $CURRENT_NETWORK"

# List preferred networks
echo "Preferred networks:"
networksetup -listpreferredwirelessnetworks "$INTERFACE"

# Function to connect to a hidden network
connect_hidden_network() {
    local ssid="$1"
    local password="$2"
    
    echo "Attempting to join hidden network: $ssid"
    
    # Add the hidden network to preferred list
    networksetup -removeallpreferredwirelessnetworks "$INTERFACE" >/dev/null 2>&1 || true
    networksetup -addpreferredwirelessnetworkatindex "$INTERFACE" "$ssid" 0 WPA2 "$password" >/dev/null 2>&1 || true
    
    # Join the network
    networksetup -joinhiddennetwork "$INTERFACE" "$ssid" "$password" 2>/dev/null
    
    sleep 5
    
    # Verify connection
    RESULT=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
    if [[ "$RESULT" == *"$ssid"* ]]; then
        echo "Successfully connected to $ssid"
        return 0
    else
        echo "Failed to connect to $ssid"
        return 1
    fi
}

# Function to connect to visible network
connect_visible_network() {
    local ssid="$1"
    local password="$2"
    
    echo "Attempting to connect to: $ssid"
    
    # Join the network
    networksetup -setairportnetwork "$INTERFACE" "$ssid" "$password" 2>/dev/null
    
    sleep 5
    
    # Verify connection
    RESULT=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null)
    if [[ "$RESULT" == *"$ssid"* ]]; then
        echo "Successfully connected to $ssid"
        return 0
    else
        echo "Failed to connect to $ssid"
        return 1
    fi
}

# Function to force reconnect to current network (useful after network switches)
force_reconnect() {
    local ssid="$1"
    local password="$2"
    local interface="$3"
    
    echo "Attempting to force reconnect to: $ssid"
    
    # Turn off and on the WiFi interface
    networksetup -setairportpower "$interface" off
    sleep 3
    networksetup -setairportpower "$interface" on
    sleep 5
    
    # Reconnect to the network
    if [ -n "$password" ]; then
        networksetup -setairportnetwork "$interface" "$ssid" "$password" 2>/dev/null
    else
        networksetup -setairportnetwork "$interface" "$ssid" 2>/dev/null
    fi
    
    sleep 10
    
    # Verify connection
    RESULT=$(networksetup -getairportnetwork "$interface" 2>/dev/null)
    if [[ "$RESULT" == *"$ssid"* ]]; then
        echo "Successfully reconnected to $ssid"
        return 0
    else
        echo "Failed to reconnect to $ssid"
        return 1
    fi
}

# Function to scan networks using alternative methods
scan_networks_alternative() {
    echo "Scanning for networks using alternative method..."
    # Use system_profiler to get WiFi information
    system_profiler SPAirPortDataType 2>/dev/null | grep "Supported Networks:" -A 50 | head -20
}

scan_networks_alternative

# Example usage for known networks
# Uncomment and modify these lines with your actual network details
# connect_visible_network "YourNetworkName" "YourPassword"
# connect_hidden_network "YourHiddenNetworkName" "YourPassword"

# Force reconnect example
# force_reconnect "YourNetworkName" "YourPassword" "$INTERFACE"

echo "Scan completed."