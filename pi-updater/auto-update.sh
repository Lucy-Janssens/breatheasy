#!/bin/bash

# Breatheasy Auto-Update Script
# This script checks for updates and pulls the latest Docker images

LOG_FILE="/home/pi/breatheasy/update.log"
PROJECT_DIR="/home/pi/breatheasy"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Navigate to project directory
cd "$PROJECT_DIR" || {
    log "ERROR: Cannot change to project directory $PROJECT_DIR"
    exit 1
}

log "Starting auto-update check..."

# Check if required environment variables are set
if [ -z "$GITHUB_USERNAME" ] || [ -z "$GITHUB_TOKEN" ]; then
    log "ERROR: GITHUB_USERNAME and GITHUB_TOKEN environment variables must be set"
    exit 1
fi

# Login to GitHub Container Registry
log "Logging in to GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

if [ $? -ne 0 ]; then
    log "ERROR: Failed to login to GitHub Container Registry"
    exit 1
fi

# Pull latest images
log "Pulling latest Docker images..."
docker compose pull

if [ $? -eq 0 ]; then
    log "New images available, updating services..."

    # Restart services with new images
    docker compose up -d

    if [ $? -eq 0 ]; then
        log "Services updated successfully"

        # Clean up old images
        docker image prune -f
        log "Old images cleaned up"
    else
        log "ERROR: Failed to restart services"
        exit 1
    fi
else
    log "No updates available or pull failed"
fi

log "Auto-update check completed"
