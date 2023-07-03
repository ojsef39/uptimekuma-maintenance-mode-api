# Copyright 2023 Josef Hofer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#!/bin/bash

# Define variables
REPO_URL="https://github.com/ojsef39/uptimekuma-maintenance-mode-api.git"
TARGET_DIR="/root"
GIT_DIR="/tmp/uptimekuma-maintenance-mode-api"
SNIPPETS_DIR="/var/lib/vz/snippets"
PROXMOX=false
DEV=false

# Parse command-line arguments
for arg in "$@"
do
    case $arg in
        --proxmox)
        PROXMOX=true
        shift # remove --proxmox from processing
        ;;
        --dev)
        DEV=true
        shift # remove --dev from processing
        ;;
    esac
done

# Remove existing directory (if it exists)
if [ -d "$GIT_DIR" ]; then
    echo "Status: Removing existing directory..."
    rm -rf "$GIT_DIR"
fi

# Clone the repository
echo "Status: Cloning repository: $REPO_URL..."
# git reset --hard "main" ##TODO: Uncomment this line
if [ "$DEV" = true ]; then
    
    ## NEXT LINES FOR TESTING!
    git clone "$REPO_URL" "$GIT_DIR"
    echo "Status: Switching to branch"
    git switch "dev-update-prepare"
    echo "Status: Pulling latest changes..."
    git reset --hard "dev-update-prepare"
    git pull
fi

# Move the python script to target directory and make it executable
echo "Status: Moving python script to target directory: $TARGET_DIR..."
# remove file before moving new one
echo "Status: Removing file if it exists and moving new one..."
rm -f "$TARGET_DIR/uptime-api.py"
mv "$GIT_DIR/uptime-api.py" "$TARGET_DIR"
echo "Status: Making python script executable..."
chmod +x "$TARGET_DIR/uptime-api.py"

# If the --proxmox argument was provided, set up the Proxmox script
if [ "$PROXMOX" = true ]; then
    # Create snippets directory if it does not exist
    echo "Status: Creating snippets directory $SNIPPETS_DIR..."
    mkdir -p "$SNIPPETS_DIR"

    # Move the Proxmox script to snippets directory and make it executable
    echo "Status: Moving Proxmox script to snippets directory: $SNIPPETS_DIR..."
    # remove file before moving new one
    echo "Status: Removing file if it exists and moving new one..."
    rm -f "$SNIPPETS_DIR/script-runner-uptime-api.sh"
    mv "$GIT_DIR/use-with-proxmox/script-runner-uptime-api.sh" "$SNIPPETS_DIR"
    echo "Status: Making Proxmox script executable..."
    chmod +x "$SNIPPETS_DIR/script-runner-uptime-api.sh"
fi

# Cleaning up
echo "Status: Cleaning up..."
rm -rf "$GIT_DIR"
echo "Status: Done!"