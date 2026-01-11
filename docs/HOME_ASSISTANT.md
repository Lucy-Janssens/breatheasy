# Home Assistant Integration Guide

This guide explains how to use BreatheEasy with Home Assistant for advanced home automation and monitoring.

## Overview

BreatheEasy integrates with Home Assistant using MQTT with automatic discovery. All sensor data is automatically published to Home Assistant, where you can:

- View real-time sensor data in dashboards
- Create automations based on air quality
- Receive notifications when thresholds are exceeded
- View historical data and graphs
- Access remotely via Home Assistant mobile app

## Architecture

```
BME680 Sensor → BreatheEasy API → MQTT Broker → Home Assistant
                      ↓
                LCD Display
                      ↓
                  SQLite DB
                      ↓
               React Web Client
```

## Quick Start

### 1. Deploy All Services

```bash
cd ~/breatheasy
./deploy.sh
```

This will:
- Create environment configuration
- Start MQTT broker (Mosquitto)
- Start Home Assistant
- Start BreatheEasy API with MQTT integration
- Start BreatheEasy web client

### 2. Access Home Assistant

Open `http://rasp-breatheasy:8123` (or `http://localhost:8123` if local)

Complete the initial setup:
- Create your admin account
- Set your location and time zone
- Skip the analytics prompt if desired

### 3. Verify Sensor Discovery

1. Navigate to **Settings** → **Devices & Services**
2. You should see "MQTT" integration automatically configured
3. Click on MQTT integration
4. You should see **BreatheEasy Monitor** device with 6 sensors:
   - Temperature (°C)
   - Humidity (%)
   - PM2.5 (µg/m³)
   - PM10 (µg/m³)
   - CO2 (ppm)
   - VOC (ppb)

## Sensors Available

| Sensor | Unit | Update Rate | Home Assistant Device Class |
|--------|------|-------------|----------------------------|
| Temperature | °C | 30s | temperature |
| Humidity | % | 30s | humidity |
| PM2.5 | µg/m³ | 30s | pm25 |
| PM10 | µg/m³ | 30s | pm10 |
| CO2 | ppm | 30s | carbon_dioxide |
| VOC | ppb | 30s | volatile_organic_compounds |

## Creating a Dashboard

### Simple Dashboard Example

1. Go to **Overview** (home page)
2. Click **Edit Dashboard** (top right)
3. Click **+ Add Card**
4. Select **Entities Card**
5. Add your BreatheEasy sensors:
   - sensor.breatheasy_temperature
   - sensor.breatheasy_humidity
   - sensor.breatheasy_pm25
   - sensor.breatheasy_co2

### Advanced Dashboard with Gauges

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.breatheasy_temperature
    name: Temperature
  - type: gauge
    entity: sensor.breatheasy_humidity
    name: Humidity
    min: 0
    max: 100
  - type: gauge
    entity: sensor.breatheasy_pm25
    name: PM2.5
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 35
      red: 55
  - type: gauge
    entity: sensor.breatheasy_co2
    name: CO2
    min: 400
    max: 2000
    severity:
      green: 400
      yellow: 1000
      red: 1500
```

## Creating Automations

### Example: Air Quality Alert

Notify when PM2.5 exceeds safe levels:

```yaml
alias: Air Quality Alert
description: Send notification when PM2.5 is high
trigger:
  - platform: numeric_state
    entity_id: sensor.breatheasy_pm25
    above: 35
action:
  - service: notify.notify
    data:
      title: Air Quality Warning
      message: PM2.5 is at {{ states('sensor.breatheasy_pm25') }} µg/m³
mode: single
```

### Example: High CO2 Reminder

Remind to open windows when CO2 is high:

```yaml
alias: High CO2 Reminder
description: Remind to ventilate when CO2 is high
trigger:
  - platform: numeric_state
    entity_id: sensor.breatheasy_co2
    above: 1000
action:
  - service: notify.notify
    data:
      title: Ventilation Needed
      message: CO2 level is high ({{ states('sensor.breatheasy_co2') }} ppm). Consider opening windows.
mode: single
```

## Troubleshooting

### Sensors Not Appearing

1. Check MQTT broker is running:
   ```bash
   docker compose logs mqtt
   ```

2. Check API is publishing to MQTT:
   ```bash
   docker compose logs api | grep -i mqtt
   ```

3. Restart Home Assistant:
   ```bash
   docker compose restart homeassistant
   ```

### MQTT Connection Issues

Check environment variables in `.env`:
```bash
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883
```

View MQTT traffic (requires mosquitto-clients):
```bash
docker exec -it breatheasy-mqtt mosquitto_sub -v -t '#'
```

### Home Assistant Can't Connect to MQTT

1. Check Home Assistant logs:
   ```bash
   docker compose logs homeassistant | grep -i mqtt
   ```

2. Verify MQTT configuration in Home Assistant:
   - Go to Settings → Devices & Services
   - Find MQTT integration
   - Check broker is set to `localhost:1883`

## Advanced Configuration

### Custom MQTT Topics

Edit `api/app/integrations/mqtt_publisher.py` to customize topics:

```python
state_topic = f"breatheasy/sensor/{sensor_type}"
```

### Change Update Frequency

Edit `.env`:
```bash
SENSOR_POLL_INTERVAL=60  # Update every 60 seconds
```

### MQTT Authentication

Edit `mosquitto/config/mosquitto.conf`:
```conf
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
```

Create password file:
```bash
docker exec -it breatheasy-mqtt mosquitto_passwd -c /mosquitto/config/passwd username
```

Update `.env`:
```bash
MQTT_USERNAME=username
MQTT_PASSWORD=yourpassword
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Home Assistant | 8123 | Home automation platform |
| MQTT Broker | 1883 | Mosquitto MQTT broker |
| BreatheEasy API | 8000 | FastAPI backend |
| BreatheEasy Client | 3000 | React frontend |

## Useful Commands

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f homeassistant
docker compose logs -f mqtt
docker compose logs -f api

# Restart services
docker compose restart homeassistant
docker compose restart mqtt
docker compose restart api

# Stop all services
docker compose down

# Start all services
docker compose up -d

# Check service status
docker compose ps
```

## Further Reading

- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [MQTT Integration Guide](https://www.home-assistant.io/integrations/mqtt/)
- [Creating Automations](https://www.home-assistant.io/docs/automation/)
- [Dashboard Cards](https://www.home-assistant.io/dashboards/)

