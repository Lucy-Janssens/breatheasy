#!/bin/bash
# Verification script for Home Assistant integration

echo "🔍 BreatheEasy + Home Assistant Integration Verification"
echo "========================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# 1. Check Docker Compose file
echo "1️⃣  Checking Docker Compose configuration..."
if [ -f "docker-compose.yml" ]; then
    if grep -q "mqtt:" docker-compose.yml && grep -q "homeassistant:" docker-compose.yml; then
        check_pass "docker-compose.yml contains MQTT and Home Assistant services"
    else
        check_fail "docker-compose.yml missing MQTT or Home Assistant services"
    fi
else
    check_fail "docker-compose.yml not found"
fi
echo ""

# 2. Check Mosquitto config
echo "2️⃣  Checking MQTT Broker configuration..."
if [ -f "mosquitto/config/mosquitto.conf" ]; then
    check_pass "Mosquitto configuration file exists"
else
    check_fail "mosquitto/config/mosquitto.conf not found"
fi
echo ""

# 3. Check Home Assistant config
echo "3️⃣  Checking Home Assistant configuration..."
if [ -f "homeassistant/configuration.yaml" ]; then
    if grep -q "mqtt:" homeassistant/configuration.yaml; then
        check_pass "Home Assistant configuration contains MQTT setup"
    else
        check_warn "Home Assistant configuration may be missing MQTT"
    fi
else
    check_fail "homeassistant/configuration.yaml not found"
fi
echo ""

# 4. Check MQTT publisher module
echo "4️⃣  Checking MQTT Publisher implementation..."
if [ -f "api/app/integrations/mqtt_publisher.py" ]; then
    if grep -q "class MQTTPublisher" api/app/integrations/mqtt_publisher.py; then
        check_pass "MQTT Publisher module implemented"
    else
        check_fail "MQTT Publisher class not found"
    fi
else
    check_fail "api/app/integrations/mqtt_publisher.py not found"
fi
echo ""

# 5. Check requirements
echo "5️⃣  Checking Python dependencies..."
if [ -f "api/requirements.txt" ]; then
    if grep -q "paho-mqtt" api/requirements.txt; then
        check_pass "paho-mqtt dependency added to requirements.txt"
    else
        check_fail "paho-mqtt not found in requirements.txt"
    fi
else
    check_fail "api/requirements.txt not found"
fi
echo ""

# 6. Check main.py integration
echo "6️⃣  Checking main.py MQTT integration..."
if [ -f "api/app/main.py" ]; then
    if grep -q "initialize_mqtt\|mqtt_publisher" api/app/main.py; then
        check_pass "main.py contains MQTT initialization"
    else
        check_fail "main.py missing MQTT initialization"
    fi
else
    check_fail "api/app/main.py not found"
fi
echo ""

# 7. Check sensor service integration
echo "7️⃣  Checking sensor service MQTT integration..."
if [ -f "api/app/services/sensor_service.py" ]; then
    if grep -q "mqtt_publisher\|publish_sensor_reading" api/app/services/sensor_service.py; then
        check_pass "Sensor service integrated with MQTT publisher"
    else
        check_fail "Sensor service missing MQTT integration"
    fi
else
    check_fail "api/app/services/sensor_service.py not found"
fi
echo ""

# 8. Check if containers are running
echo "8️⃣  Checking Docker containers..."
if command -v docker &> /dev/null; then
    if docker compose ps 2>/dev/null | grep -q "breatheasy-mqtt"; then
        if docker compose ps 2>/dev/null | grep "breatheasy-mqtt" | grep -q "Up"; then
            check_pass "MQTT container is running"
        else
            check_warn "MQTT container exists but is not running"
        fi
    else
        check_warn "MQTT container not found (run ./deploy.sh to start)"
    fi
    
    if docker compose ps 2>/dev/null | grep -q "homeassistant"; then
        if docker compose ps 2>/dev/null | grep "homeassistant" | grep -q "Up"; then
            check_pass "Home Assistant container is running"
        else
            check_warn "Home Assistant container exists but is not running"
        fi
    else
        check_warn "Home Assistant container not found (run ./deploy.sh to start)"
    fi
    
    if docker compose ps 2>/dev/null | grep -q "breatheasy-api"; then
        if docker compose ps 2>/dev/null | grep "breatheasy-api" | grep -q "Up"; then
            check_pass "API container is running"
        else
            check_warn "API container exists but is not running"
        fi
    else
        check_warn "API container not found (run ./deploy.sh to start)"
    fi
else
    check_warn "Docker command not available"
fi
echo ""

# 9. Check documentation
echo "9️⃣  Checking documentation..."
if [ -f "docs/HOME_ASSISTANT.md" ]; then
    check_pass "Home Assistant documentation created"
else
    check_warn "docs/HOME_ASSISTANT.md not found"
fi

if [ -f "DEPLOYMENT_SUMMARY.md" ]; then
    check_pass "Deployment summary created"
else
    check_warn "DEPLOYMENT_SUMMARY.md not found"
fi
echo ""

# Summary
echo "=========================================================="
echo "📊 Verification Summary"
echo "=========================================================="
echo ""
echo "If all checks passed, you're ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Run: ./deploy.sh"
echo "  2. Wait ~30 seconds for services to start"
echo "  3. Open: http://localhost:8123 (or http://rasp-breatheasy:8123)"
echo "  4. Complete Home Assistant setup"
echo "  5. Check Settings → Devices & Services for BreatheEasy sensors"
echo ""
echo "For more info, see: docs/HOME_ASSISTANT.md"

