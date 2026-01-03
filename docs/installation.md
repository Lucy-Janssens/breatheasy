# Breatheasy Installation Guide

This guide covers the installation and setup process for Breatheasy on different platforms.

## Local Development Setup

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git**

### Backend Setup (API)

```bash
# Navigate to API directory
cd api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Client)

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

## Production Deployment

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/breatheasy.git
cd breatheasy

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Option 2: Manual Installation

#### Backend

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Install GPIO libraries (Raspberry Pi only)
sudo apt-get install python3-rpi.gpio i2c-tools

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Install Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install dependencies and build
npm install
npm run build

# Serve with nginx
sudo cp -r dist/* /var/www/html/
sudo systemctl restart nginx
```

## Raspberry Pi Specific Setup

### Enable Interfaces

```bash
# Enable I2C (required for some sensors)
sudo raspi-config nonint do_i2c 0

# Enable SPI (if needed)
sudo raspi-config nonint do_spi 0

# Enable GPIO access
sudo usermod -a -G gpio $USER
```

### GPIO Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Reboot or logout/login for changes to take effect
sudo reboot
```

### Hardware Connections

Connect your sensors according to the pin configuration in `.env`:

- **Temperature/Humidity Sensor** (DHT22): GPIO 4
- **Air Quality Sensor**: GPIO 17
- **Motion Sensor** (PIR): GPIO 27
- **OLED Display** (SSD1322): I2C, Reset on GPIO 24

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_HOST` | Server host | `0.0.0.0` | No |
| `API_PORT` | Server port | `8000` | No |
| `DEBUG` | Debug mode | `false` | No |
| `DATABASE_URL` | Database connection | `sqlite:///./breatheasy.db` | No |
| `TEMPERATURE_SENSOR_PIN` | GPIO pin for temp sensor | `4` | No |
| `AIR_QUALITY_SENSOR_PIN` | GPIO pin for air quality | `17` | No |
| `MOTION_SENSOR_PIN` | GPIO pin for motion sensor | `27` | No |
| `OLED_RESET_PIN` | GPIO pin for OLED reset | `24` | No |
| `SENSOR_POLL_INTERVAL` | Seconds between readings | `30` | No |
| `DISPLAY_TIMEOUT` | Seconds before display timeout | `60` | No |

### Database Setup

SQLite is used by default and requires no additional setup. The database file will be created automatically in the `data/` directory.

## Testing the Installation

### API Health Check

```bash
# Test API health endpoint
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "message": "Breatheasy API is running"}
```

### Frontend Access

Open your browser and navigate to:
- **Development**: `http://localhost:5173`
- **Production**: `http://localhost:3000`

### Sensor Testing

```bash
# Test sensor readings (may show mock data initially)
curl http://localhost:8000/api/readings/latest
```

## Troubleshooting

### Common Issues

**"Permission denied" for GPIO access:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
sudo reboot
```

**"Port already in use":**
```bash
# Find process using port
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Database errors:**
```bash
# Delete and recreate database
rm data/breatheasy.db
# Restart the API server
```

**Node modules issues:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Logs

**API Logs:**
```bash
# Docker
docker compose logs api

# Manual installation
# Check uvicorn output or application logs
```

**Frontend Logs:**
```bash
# Development
npm run dev  # Check console output

# Production
docker compose logs client
```

### Hardware Debugging

**Check GPIO pins:**
```bash
# List GPIO status
gpio readall
```

**Test I2C devices:**
```bash
# Scan I2C bus
i2cdetect -y 1
```

## Next Steps

1. **Configure Sensors**: Update `.env` with your actual sensor configurations
2. **Set Up Deployment**: Follow the [deployment guide](deployment.md) for production setup
3. **Customize UI**: Modify the React components in `client/src/`
4. **Add Features**: Extend the API with new endpoints in `api/app/routers/`

For more advanced configuration and deployment options, see the [deployment guide](deployment.md).
