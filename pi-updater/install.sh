#!/bin/bash

# Breatheasy Raspberry Pi Installation Script
# This script sets up the complete deployment environment on a Raspberry Pi

set -e

LOG_FILE="/home/pi/breatheasy/install.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting Breatheasy installation..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    log "WARNING: This script is designed for Raspberry Pi. Continuing anyway..."
fi

# Update system packages
log "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
log "Installing required packages..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    i2c-tools \
    docker.io \
    docker-compose-plugin

# Enable I2C (required for sensors)
log "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Add user to docker group
log "Adding user to docker group..."
sudo usermod -aG docker pi

# Create project directory
log "Creating project directory..."
mkdir -p /home/pi/breatheasy
cd /home/pi/breatheasy

# Clone repository (replace with your actual repo URL)
if [ -z "$REPO_URL" ]; then
    REPO_URL="https://github.com/YOUR_USERNAME/breatheasy.git"
fi

log "Cloning repository from $REPO_URL..."
git clone "$REPO_URL" .

# Set up Python virtual environment for webhook server
log "Setting up Python virtual environment..."
python3 -m venv pi-updater/venv
source pi-updater/venv/bin/activate
pip install -r pi-updater/requirements.txt

# Install sensor libraries in the main environment (for Docker)
log "Installing sensor libraries..."
pip install smbus2 adafruit-circuitpython-bme680 adafruit-circuitpython-ssd1322

# Create .env file
if [ ! -f .env ]; then
    log "Creating .env file..."
    cp .env.example .env
    log "Please edit .env file with your configuration"
fi

# Create data directory
log "Creating data directory..."
mkdir -p data

# Make scripts executable
log "Making scripts executable..."
chmod +x pi-updater/auto-update.sh
chmod +x pi-updater/install.sh
chmod +x pi-updater/test_sensors.py
chmod +x pi-updater/display_temp.py

# Set up webhook service (optional)
read -p "Do you want to set up webhook-based updates? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Setting up webhook service..."
    sudo cp pi-updater/webhook.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable breatheasy-webhook
    log "Webhook service installed. Remember to set WEBHOOK_SECRET in the service file."
fi

# Set up cron job for polling updates (optional)
read -p "Do you want to set up cron-based auto-updates? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Setting up cron job for auto-updates..."
    (crontab -l ; echo "*/10 * * * * /home/pi/breatheasy/pi-updater/auto-update.sh >> /home/pi/breatheasy/update.log 2>&1") | crontab -
    log "Cron job installed - will check for updates every 10 minutes"
fi

# Login to GitHub Container Registry
if [ -n "$GITHUB_USERNAME" ] && [ -n "$GITHUB_TOKEN" ]; then
    log "Logging in to GitHub Container Registry..."
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
else
    log "WARNING: GITHUB_USERNAME and GITHUB_TOKEN not set. Please login manually:"
    log "echo \$GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin"
fi

# Start services
log "Starting Breatheasy services..."
docker compose up -d

# Wait for services to start
log "Waiting for services to start..."
sleep 30

# Check if services are running
if docker compose ps | grep -q "Up"; then
    log "Services started successfully!"
else
    log "ERROR: Services failed to start. Check logs with: docker compose logs"
    exit 1
fi

# Test sensors (optional)
read -p "Do you want to test the sensors now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Testing sensors..."
    if python3 pi-updater/test_sensors.py; then
        log "Sensor tests passed!"
    else
        log "WARNING: Some sensor tests failed. Check sensor connections and try again."
    fi
fi

log "Installation completed successfully!"
log ""
log "Next steps:"
log "1. Edit .env file with your configuration"
log "2. Access the application at http://localhost:3000"
log "3. Check logs with: docker compose logs -f"
log "4. Test sensors with: python3 pi-updater/test_sensors.py"
log "5. Display temperature with: python3 pi-updater/display_temp.py"
log "6. If using webhook updates, start the service with: sudo systemctl start breatheasy-webhook"

# Print service status
log ""
log "Current service status:"
docker compose ps
