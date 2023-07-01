#!/bin/bash

# Define variables
REPO_URL="https://github.com/ojsef39/uptimekuma-maintenance-mode-api.git"
TARGET_DIR="/root"
GIT_DIR="/tmp/uptimekuma-maintenance-mode-api"
SNIPPETS_DIR="/var/lib/vz/snippets"
PROXMOX=false

# Parse command-line arguments
for arg in "$@"
do
    case $arg in
        --proxmox)
        PROXMOX=true
        shift # remove --proxmox from processing
        ;;
    esac
done

# Remove existing directory (if it exists)
if [ -d "$GIT_DIR" ]; then
    rm -rf "$GIT_DIR"
fi

# Clone the repository
git clone "$REPO_URL" "$GIT_DIR"

# Move the python script to target directory
mv "$GIT_DIR/uptime-api.py" "$TARGET_DIR"

# If the --proxmox argument was provided, set up the Proxmox script
if [ "$PROXMOX" = true ]; then
    # Create snippets directory if it does not exist
    mkdir -p "$SNIPPETS_DIR"

    # Move the Proxmox script to snippets directory and make it executable
    mv "$GIT_DIR/use-with-proxmox/script-runner-uptime-api.pl" "$SNIPPETS_DIR"
    chmod +x "$SNIPPETS_DIR/script-runner-uptime-api.pl"
fi

# Cleaning up
rm -rf "$GIT_DIR"
