#!/bin/bash
# Home Assistant Diagnostic Script

echo "🔍 Home Assistant Diagnostic"
echo "============================"
echo ""

# Get Pi IP
PI_IP=$(hostname -I | awk '{print $1}')

echo "1️⃣  Container Status"
echo "-------------------"
docker compose ps homeassistant
echo ""

echo "2️⃣  Home Assistant Logs (last 30 lines)"
echo "----------------------------------------"
docker compose logs --tail=30 homeassistant | grep -E "(ERROR|WARNING|INFO|onboarding|http)" || docker compose logs --tail=30 homeassistant
echo ""

echo "3️⃣  Check if Home Assistant is responding"
echo "-----------------------------------------"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8123 | grep -q "200\|302"; then
    echo "✅ Home Assistant is responding on port 8123"
else
    echo "❌ Home Assistant is NOT responding on port 8123"
    echo "   HTTP Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8123)"
fi
echo ""

echo "4️⃣  Check onboarding status"
echo "---------------------------"
if [ -f ~/breatheasy/homeassistant/.storage/onboarding ]; then
    echo "✅ Onboarding file exists - setup may be complete"
    echo "   File: ~/breatheasy/homeassistant/.storage/onboarding"
else
    echo "⚠️  Onboarding file not found - setup not completed yet"
    echo "   You need to complete setup in a web browser first"
fi
echo ""

echo "5️⃣  Network Access"
echo "-----------------"
echo "Home Assistant should be accessible at:"
echo "  - http://${PI_IP}:8123"
echo "  - http://rasp-breatheasy.local:8123"
echo "  - http://localhost:8123 (from Pi itself)"
echo ""

echo "6️⃣  Port Check"
echo "-------------"
if netstat -tlnp 2>/dev/null | grep -q ":8123"; then
    echo "✅ Port 8123 is listening"
    netstat -tlnp 2>/dev/null | grep ":8123"
else
    echo "❌ Port 8123 is NOT listening"
fi
echo ""

echo "📝 Next Steps"
echo "============"
echo ""
echo "If Home Assistant is running but you can't connect:"
echo "1. Open http://${PI_IP}:8123 in a web browser"
echo "2. Complete the initial setup wizard"
echo "3. Then try connecting with the mobile app"
echo ""
echo "If Home Assistant is not running:"
echo "1. Check logs: docker compose logs homeassistant"
echo "2. Restart: docker compose restart homeassistant"
echo ""

