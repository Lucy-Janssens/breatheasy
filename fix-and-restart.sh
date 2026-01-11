#!/bin/bash
# Quick fix and restart script for Raspberry Pi

echo "🔧 Fixing Docker Compose and restarting services..."
echo ""

# Stop all containers
echo "🛑 Stopping containers..."
docker compose down

# Build images (if needed)
echo "🔨 Building images..."
docker compose build api client 2>&1 | tail -20

# Start services
echo ""
echo "🚀 Starting services..."
docker compose up -d

# Wait a moment
sleep 5

# Check status
echo ""
echo "📊 Container Status:"
echo "==================="
docker compose ps

# Check Home Assistant specifically
echo ""
echo "🏠 Home Assistant Status:"
echo "========================"
if docker compose ps | grep -q "homeassistant.*Up"; then
    echo "✅ Home Assistant is running!"
    echo ""
    PI_IP=$(hostname -I | awk '{print $1}')
    echo "🌐 Access at: http://${PI_IP}:8123"
    echo "   Or: http://rasp-breatheasy.local:8123"
    echo ""
    echo "📱 Next steps:"
    echo "1. Open http://${PI_IP}:8123 in a web browser"
    echo "2. Complete the initial setup wizard"
    echo "3. Then connect with your mobile app"
else
    echo "❌ Home Assistant is not running"
    echo ""
    echo "🔍 Checking logs..."
    docker compose logs --tail=30 homeassistant
fi

