#!/bin/bash
# Restart Home Assistant with network access

echo "🔄 Restarting Home Assistant with network access..."
echo ""

# Stop existing containers
echo "🛑 Stopping containers..."
docker compose down

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait a moment
sleep 5

# Check status
echo ""
echo "📊 Container Status:"
echo "==================="
docker compose ps

# Get Raspberry Pi IP
PI_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 Home Assistant should be accessible at:"
echo "   - http://${PI_IP}:8123"
echo "   - http://rasp-breatheasy.local:8123"
echo "   - http://192.168.129.14:8123"
echo ""
echo "📱 On your phone (same WiFi network):"
echo "   - Open Home Assistant app"
echo "   - Add new server: http://${PI_IP}:8123"
echo "   - Or use: http://rasp-breatheasy.local:8123"
echo ""
echo "🔍 Checking Home Assistant logs..."
echo "==================================="
docker compose logs --tail=20 homeassistant

