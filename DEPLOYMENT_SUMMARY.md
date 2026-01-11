# Home Assistant Integration - Implementation Summary

## ✅ Completed Tasks

All planned tasks have been successfully implemented:

### 1. Docker Compose Configuration
- ✅ Added MQTT broker (Mosquitto) service
- ✅ Added Home Assistant service  
- ✅ Configured networking and dependencies
- ✅ Added volume mounts for persistence

**File**: `docker-compose.yml`

### 2. MQTT Broker Configuration
- ✅ Created Mosquitto configuration with persistence
- ✅ Set up logging and data directories
- ✅ Configured anonymous access (can be secured later)

**Files**: 
- `mosquitto/config/mosquitto.conf`
- `mosquitto/data/` (created)
- `mosquitto/log/` (created)

### 3. MQTT Publisher Implementation
- ✅ Created comprehensive MQTT publisher module
- ✅ Implemented Home Assistant MQTT Discovery protocol
- ✅ Added device classes for all sensor types
- ✅ Configured state topics and discovery topics
- ✅ Added connection management and error handling

**Files**:
- `api/app/integrations/__init__.py`
- `api/app/integrations/mqtt_publisher.py`
- `api/requirements.txt` (added paho-mqtt==1.6.1)

### 4. Sensor Service Integration
- ✅ Updated sensor service to use MQTT publisher
- ✅ Added MQTT publishing after each sensor reading
- ✅ Maintained database persistence alongside MQTT

**File**: `api/app/services/sensor_service.py`

### 5. Main Application Updates
- ✅ Added MQTT initialization on startup
- ✅ Added graceful shutdown handler for MQTT
- ✅ Configured environment variable support
- ✅ Added availability status publishing

**File**: `api/app/main.py`

### 6. Home Assistant Configuration
- ✅ Created configuration.yaml with MQTT discovery
- ✅ Enabled default integrations
- ✅ Configured recorder for history
- ✅ Set up logging and system health

**File**: `homeassistant/configuration.yaml`

### 7. Deployment Tools
- ✅ Created automated deployment script
- ✅ Added environment configuration template
- ✅ Created comprehensive documentation

**Files**:
- `deploy.sh`
- `docs/HOME_ASSISTANT.md`

## 📊 System Overview

### Services Deployed

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| MQTT Broker | breatheasy-mqtt | 1883 | Message broker for sensor data |
| Home Assistant | homeassistant | 8123 | Home automation platform |
| BreatheEasy API | breatheasy-api | 8000 | FastAPI backend with sensors |
| BreatheEasy Client | breatheasy-client | 3000 | React web interface |
| Watchtower | watchtower | - | Auto-update containers |

### Data Flow

```
BME680 Sensor
    ↓
BreatheEasy API
    ├→ SQLite Database (local storage)
    ├→ LCD Display (local display)
    ├→ React Client (web interface)
    └→ MQTT Broker
         └→ Home Assistant
              ├→ Web Dashboard
              ├→ Mobile App
              └→ Automations
```

### Sensors Published to Home Assistant

All sensors are published with proper Home Assistant device classes:

1. **Temperature** (°C) - `sensor.breatheasy_temperature`
2. **Humidity** (%) - `sensor.breatheasy_humidity`
3. **PM2.5** (µg/m³) - `sensor.breatheasy_pm25`
4. **PM10** (µg/m³) - `sensor.breatheasy_pm10`
5. **CO2** (ppm) - `sensor.breatheasy_co2`
6. **VOC** (ppb) - `sensor.breatheasy_voc`

## 🚀 Deployment Instructions

### On Raspberry Pi

```bash
# 1. Copy all files to Raspberry Pi
scp -r /Users/lucyjanssens/dev/breatheasy/* lucy@rasp-breatheasy:~/breatheasy/

# 2. SSH to Raspberry Pi
ssh lucy@rasp-breatheasy

# 3. Deploy with automated script
cd ~/breatheasy
./deploy.sh

# 4. Wait for services to start (~30 seconds)

# 5. Access Home Assistant
# Open browser to: http://rasp-breatheasy:8123
```

### Manual Deployment (Alternative)

```bash
cd ~/breatheasy

# Stop existing services
docker compose down

# Build API with MQTT support
docker compose build api

# Pull Home Assistant image
docker compose pull homeassistant

# Start all services
docker compose up -d

# Monitor logs
docker compose logs -f
```

## 🔧 Configuration

### Environment Variables

The following environment variables are used (`.env` file):

```env
# MQTT Configuration
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=breatheasy-api

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SENSOR_POLL_INTERVAL=30
```

### MQTT Topics

**Discovery Topics** (retained):
- `homeassistant/sensor/breatheasy_temperature/config`
- `homeassistant/sensor/breatheasy_humidity/config`
- `homeassistant/sensor/breatheasy_pm25/config`
- `homeassistant/sensor/breatheasy_pm10/config`
- `homeassistant/sensor/breatheasy_co2/config`
- `homeassistant/sensor/breatheasy_voc/config`

**State Topics** (real-time):
- `breatheasy/sensor/temperature`
- `breatheasy/sensor/humidity`
- `breatheasy/sensor/pm25`
- `breatheasy/sensor/pm10`
- `breatheasy/sensor/co2`
- `breatheasy/sensor/voc`

**Availability**:
- `breatheasy/status` (online/offline)

## ✅ Verification Steps

After deployment, verify the integration:

### 1. Check Container Status
```bash
docker compose ps
```
All containers should be "Up" and healthy.

### 2. Check MQTT Connection
```bash
docker compose logs api | grep -i mqtt
```
Should see: "Successfully connected to MQTT broker"

### 3. Check Discovery Messages
```bash
docker compose logs api | grep -i "discovery"
```
Should see discovery messages sent for all 6 sensors.

### 4. Access Home Assistant
1. Open `http://rasp-breatheasy:8123`
2. Complete initial setup wizard
3. Go to Settings → Devices & Services
4. Verify MQTT integration exists
5. Click MQTT → Should see "BreatheEasy Monitor" device
6. Device should have 6 entities (all sensors)

### 5. View Sensor Data
1. Go to Developer Tools → States
2. Search for "breatheasy"
3. All 6 sensors should be listed with current values

## 🎨 Next Steps

### Create Dashboard
1. Go to Overview
2. Edit Dashboard
3. Add cards for your sensors
4. Customize layout

### Create Automations
Examples in `docs/HOME_ASSISTANT.md`:
- Air quality alerts
- High CO2 notifications
- Ventilation reminders

### Mobile Access
1. Install Home Assistant Companion app
2. Connect to your instance
3. View sensors on the go

## 📝 Files Modified/Created

### Modified Files
- `docker-compose.yml` - Added MQTT and Home Assistant services
- `api/requirements.txt` - Added paho-mqtt dependency
- `api/app/main.py` - Added MQTT initialization and shutdown
- `api/app/services/sensor_service.py` - Added MQTT publishing

### Created Files
- `api/app/integrations/__init__.py` - Integration module init
- `api/app/integrations/mqtt_publisher.py` - MQTT publisher implementation
- `mosquitto/config/mosquitto.conf` - MQTT broker configuration
- `homeassistant/configuration.yaml` - Home Assistant configuration
- `deploy.sh` - Automated deployment script
- `docs/HOME_ASSISTANT.md` - Comprehensive documentation
- `DEPLOYMENT_SUMMARY.md` - This file

## 🐛 Troubleshooting

### MQTT Not Connecting
- Check `MQTT_BROKER_HOST` in `.env`
- Verify MQTT container is running: `docker compose ps mqtt`
- Check logs: `docker compose logs mqtt`

### Sensors Not Appearing in HA
- Restart Home Assistant: `docker compose restart homeassistant`
- Check MQTT integration in HA Settings
- Verify discovery messages: `docker compose logs api | grep discovery`

### Network Issues
- Home Assistant uses `network_mode: host`
- Ensure ports 8123, 1883 are not blocked by firewall
- Check container connectivity: `docker compose exec api ping mqtt`

## 📚 Documentation

Full documentation available in:
- `docs/HOME_ASSISTANT.md` - Complete integration guide
- Home Assistant UI - Settings → Devices & Services
- MQTT Explorer - For debugging MQTT messages

## 🎉 Success!

Your BreatheEasy system is now fully integrated with Home Assistant! All sensor data is automatically published and discoverable. You can now:

✅ View real-time air quality in Home Assistant
✅ Create custom dashboards
✅ Set up automations based on sensor values
✅ Access remotely via mobile app
✅ View historical data and graphs
✅ Integrate with other smart home devices

Enjoy your enhanced air quality monitoring system! 🌱

