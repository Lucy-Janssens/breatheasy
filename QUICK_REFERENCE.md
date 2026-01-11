# 🚀 BreatheEasy + Home Assistant - Quick Reference

## 📦 Deployment

```bash
# On Raspberry Pi
cd ~/breatheasy
./deploy.sh
```

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| Home Assistant | http://rasp-breatheasy:8123 |
| BreatheEasy Web | http://rasp-breatheasy:3000 |
| BreatheEasy API | http://rasp-breatheasy:8000 |

## 📊 Sensors in Home Assistant

| Entity ID | Sensor | Unit |
|-----------|--------|------|
| `sensor.breatheasy_temperature` | Temperature | °C |
| `sensor.breatheasy_humidity` | Humidity | % |
| `sensor.breatheasy_pm25` | PM2.5 | µg/m³ |
| `sensor.breatheasy_pm10` | PM10 | µg/m³ |
| `sensor.breatheasy_co2` | CO2 | ppm |
| `sensor.breatheasy_voc` | VOC | ppb |

## 🔧 Useful Commands

```bash
# View logs
docker compose logs -f api
docker compose logs -f mqtt
docker compose logs -f homeassistant

# Restart services
docker compose restart api
docker compose restart homeassistant

# Check status
docker compose ps

# Stop all
docker compose down

# Start all
docker compose up -d
```

## 🐛 Quick Troubleshooting

### Sensors not showing in HA?
```bash
docker compose restart homeassistant
docker compose logs api | grep -i "mqtt\|discovery"
```

### MQTT connection issues?
```bash
docker compose logs mqtt
docker compose logs api | grep -i "mqtt"
```

### Check what's published to MQTT
```bash
docker exec -it breatheasy-mqtt mosquitto_sub -v -t '#'
```

## 📝 First Time Setup

1. Deploy: `./deploy.sh`
2. Open HA: http://rasp-breatheasy:8123
3. Create admin account
4. Go to Settings → Devices & Services
5. Find "BreatheEasy Monitor" under MQTT
6. Create dashboard with your sensors!

## 📚 Full Documentation

- Detailed guide: `docs/HOME_ASSISTANT.md`
- Deployment summary: `DEPLOYMENT_SUMMARY.md`

