#!/bin/bash
# Copy BreatheEasy files to Raspberry Pi

PI_HOST="lucy@192.168.129.14"
PI_PATH="~/breatheasy"

echo "📦 Copying BreatheEasy files to Raspberry Pi..."
echo "Target: ${PI_HOST}:${PI_PATH}"
echo ""

# Create directory structure on Pi
echo "📁 Creating directories on Pi..."
ssh ${PI_HOST} "mkdir -p ${PI_PATH}/api/app/integrations ${PI_PATH}/mosquitto/config ${PI_PATH}/homeassistant ${PI_PATH}/docs"

# Copy files
echo "📋 Copying files..."

# Core files
scp docker-compose.yml deploy.sh ${PI_HOST}:${PI_PATH}/
scp DEPLOYMENT_SUMMARY.md QUICK_REFERENCE.md ${PI_HOST}:${PI_PATH}/

# API files
scp api/requirements.txt api/Dockerfile ${PI_HOST}:${PI_PATH}/api/
scp -r api/app/* ${PI_HOST}:${PI_PATH}/api/app/

# Mosquitto config
scp mosquitto/config/mosquitto.conf ${PI_HOST}:${PI_PATH}/mosquitto/config/

# Home Assistant config
scp homeassistant/configuration.yaml ${PI_HOST}:${PI_PATH}/homeassistant/

# Documentation
scp docs/HOME_ASSISTANT.md ${PI_HOST}:${PI_PATH}/docs/ 2>/dev/null || true

# Make scripts executable
echo "🔧 Making scripts executable..."
ssh ${PI_HOST} "chmod +x ${PI_PATH}/deploy.sh"

echo ""
echo "✅ Files copied successfully!"
echo ""
echo "Now on your Pi, run:"
echo "  cd ~/breatheasy"
echo "  ./deploy.sh"

