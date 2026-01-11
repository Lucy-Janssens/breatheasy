#!/bin/bash
# Deploy BreatheEasy with Home Assistant to Raspberry Pi

echo "🚀 Deploying BreatheEasy with Home Assistant Integration"
echo "========================================================="

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# BreatheEasy Environment Configuration

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database Configuration
DATABASE_URL=sqlite:///./data/breatheasy.db

# Sensor Configuration
SENSOR_POLL_INTERVAL=30

# MQTT Configuration
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=breatheasy-api
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker compose down

# Pull latest images
echo ""
echo "⬇️  Pulling latest images..."
docker compose pull homeassistant || echo "⚠️  Home Assistant image pull may take a while on first run"

# Build API image
echo ""
echo "🔨 Building API image..."
docker compose build api

# Start all services
echo ""
echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

# Check status
echo ""
echo "📊 Service Status:"
echo "=================="
docker compose ps

# Show logs
echo ""
echo "📋 Recent Logs:"
echo "==============="
docker compose logs --tail=20 api mqtt homeassistant

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🌐 Access Points:"
echo "  - BreatheEasy Web Client: http://localhost:3000"
echo "  - BreatheEasy API:        http://localhost:8000"
echo "  - Home Assistant:         http://localhost:8123"
echo "  - MQTT Broker:            localhost:1883"
echo ""
echo "📝 Next Steps:"
echo "  1. Open Home Assistant at http://localhost:8123"
echo "  2. Complete the initial setup wizard"
echo "  3. Navigate to Settings > Devices & Services"
echo "  4. Your BreatheEasy sensors should appear automatically!"
echo ""
echo "🔍 To view logs: docker compose logs -f api mqtt homeassistant"

