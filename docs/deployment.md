# Breatheasy Deployment Guide

This guide covers the complete CI/CD setup for deploying Breatheasy to a Raspberry Pi with automated updates.

## Architecture Overview

```
GitHub Push → GitHub Actions → Docker Images → Raspberry Pi → Auto-Update
     ↓              ↓                ↓              ↓          ↓
  Code Changes   ARM Builds      GHCR Push     Webhook      Services
```

## Prerequisites

### GitHub Repository Setup

1. **Create GitHub Repository Secrets** (Settings → Secrets and variables → Actions):
   - `WEBHOOK_URL`: Your Raspberry Pi's webhook endpoint (e.g., `https://your-pi-host:9000/update`)
   - `WEBHOOK_SECRET`: Random secret for webhook authentication

2. **Enable GitHub Container Registry**:
   - Go to repository Settings → Packages
   - Ensure packages are public or your Pi can authenticate

### Raspberry Pi Setup

- Raspberry Pi 3B+ or newer (ARM64 recommended)
- Raspbian OS or Ubuntu
- Docker and Docker Compose installed
- Git installed
- Internet connection

## Quick Start Deployment

### 1. Initial Raspberry Pi Setup

```bash
# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/breatheasy.git
cd breatheasy

# Run installation script
chmod +x pi-updater/install.sh
sudo ./pi-updater/install.sh
```

The installation script will:
- Update system packages
- Install Docker and required dependencies
- Enable I2C for sensors
- Set up Python virtual environment
- Configure systemd services
- Start Breatheasy services

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
nano .env
```

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/breatheasy.db

# Sensor Configuration
TEMPERATURE_SENSOR_PIN=4
AIR_QUALITY_SENSOR_PIN=17
MOTION_SENSOR_PIN=27
OLED_RESET_PIN=24

# Polling intervals (seconds)
SENSOR_POLL_INTERVAL=30
DISPLAY_TIMEOUT=60

# GitHub Container Registry (for polling updates)
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token

# Webhook Secret (for webhook updates)
WEBHOOK_SECRET=your_webhook_secret
```

### 3. Start Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## Update Mechanisms

Choose one of the three update methods:

### Option 1: Webhook-based Updates (Recommended)

**Setup:**
```bash
# Edit webhook service
sudo nano /etc/systemd/system/breatheasy-webhook.service
# Set your WEBHOOK_SECRET

# Start webhook service
sudo systemctl daemon-reload
sudo systemctl enable breatheasy-webhook
sudo systemctl start breatheasy-webhook
```

**How it works:**
- GitHub Actions triggers webhook after successful build
- Webhook server receives update notification
- Services are pulled and restarted automatically

### Option 2: Polling-based Updates

**Setup:**
```bash
# Add to crontab (runs every 10 minutes)
(crontab -l ; echo "*/10 * * * * /home/pi/breatheasy/pi-updater/auto-update.sh >> /home/pi/breatheasy/update.log 2>&1") | crontab -

# Or run manually
/home/pi/breatheasy/pi-updater/auto-update.sh
```

**How it works:**
- Cron job runs update script periodically
- Script checks for new images and updates if available

### Option 3: Watchtower (Automatic)

Watchtower is included in `docker-compose.yml` and will automatically update containers when new images are available.

**Enable/Disable:**
- Uncomment the `watchtower` service in `docker-compose.yml`
- Restart with `docker compose up -d`

## GitHub Actions Workflow

The workflow (`.github/workflows/deploy.yml`) automatically:

1. **Triggers** on pushes to `main` branch
2. **Builds** multi-architecture Docker images (ARM64/ARMv7)
3. **Pushes** images to GitHub Container Registry
4. **Triggers** Raspberry Pi update via webhook

### Customizing the Workflow

Edit `.github/workflows/deploy.yml` to:
- Change trigger branches
- Add testing steps
- Modify image tags
- Add notifications

## Docker Configuration

### Service Architecture

```
breatheasy-client (Port 3000) → Nginx serving React app
breatheasy-api (Port 8000) → FastAPI backend with GPIO access
watchtower → Automatic updates (optional)
```

### Building Locally

```bash
# Build API image
docker build -t breatheasy-api:latest ./api

# Build client image
docker build -t breatheasy-client:latest ./client

# Run locally
docker compose up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/breatheasy.db` |
| `DEBUG` | Enable debug mode | `false` |
| `GITHUB_USERNAME` | GitHub username for GHCR | - |
| `GITHUB_TOKEN` | GitHub token for GHCR | - |
| `WEBHOOK_SECRET` | Secret for webhook auth | - |

## Hardware Setup

### GPIO Pin Configuration

The application expects these GPIO pins (BCM numbering):

- **Temperature Sensor**: Pin 4 (GPIO 4)
- **Air Quality Sensor**: Pin 17 (GPIO 17)
- **Motion Sensor**: Pin 27 (GPIO 27)
- **OLED Display**: Reset pin 24 (GPIO 24)

### I2C Setup

For sensors using I2C:
```bash
# Enable I2C
sudo raspi-config nonint do_i2c 0

# Check I2C devices
i2cdetect -y 1
```

## Monitoring & Troubleshooting

### Service Health Checks

```bash
# Check all services
docker compose ps

# View service logs
docker compose logs api
docker compose logs client

# Check webhook logs
sudo journalctl -u breatheasy-webhook -f

# Check auto-update logs
tail -f /home/pi/breatheasy/update.log
```

### Common Issues

**Services won't start:**
```bash
# Check Docker system
docker system df
docker system prune

# Check permissions
ls -la /dev/gpiomem
groups pi
```

**GPIO access denied:**
```bash
# Add to docker group
sudo usermod -aG docker pi

# Or run with privileged mode
docker compose up -d --privileged
```

**Webhook not receiving updates:**
```bash
# Check webhook service
sudo systemctl status breatheasy-webhook

# Test webhook manually
curl -X POST http://localhost:9000/update \
  -H "Authorization: Bearer YOUR_SECRET"
```

### Performance Optimization

**For Raspberry Pi 3:**
- Use ARMv7 images instead of ARM64
- Reduce sensor polling frequency
- Disable debug mode

**Memory usage:**
```bash
# Monitor memory
docker stats

# Limit container memory
docker compose up -d --scale api=1 --memory 256m
```

## Security Considerations

1. **Change default webhook secret**
2. **Use HTTPS for webhook endpoint** (with Tailscale or nginx)
3. **Regularly update GitHub tokens**
4. **Monitor access logs**
5. **Keep system updated**

## Backup & Recovery

### Database Backup

```bash
# Backup database
cp data/breatheasy.db data/breatheasy.db.backup

# Automated backup script
0 2 * * * cp /home/pi/breatheasy/data/breatheasy.db /home/pi/breatheasy/backups/breatheasy-$(date +\%Y\%m\%d).db
```

### Rollback Deployment

```bash
# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/breatheasy-api:v1.2.3
docker pull ghcr.io/YOUR_USERNAME/breatheasy-client:v1.2.3

# Update docker-compose.yml with specific tags
# Then restart
docker compose up -d
```

## Development Workflow

1. **Local Development**: Use `docker compose up` for testing
2. **Push Changes**: Commit and push to `main` branch
3. **Automated Build**: GitHub Actions builds and pushes images
4. **Auto-Update**: Raspberry Pi pulls new images automatically
5. **Monitor**: Check logs and service health

## Support

- **Logs**: `docker compose logs -f`
- **Health**: `curl http://localhost:8000/api/health`
- **Status**: `docker compose ps`
- **Updates**: Check `/home/pi/breatheasy/update.log`

For issues, check the [troubleshooting section](#monitoring--troubleshooting) or create an issue in the repository.
