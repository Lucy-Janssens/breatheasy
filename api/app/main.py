"""
FastAPI application entry-point for BreatheEasy.

Startup sequence:
  1. Create database tables
  2. Initialise SensorManager (BME680, DHT22, PIR)
  3. Initialise DisplayManager (OLED + PIR)
  4. Start SensorManager polling
  5. Start DisplayManager monitoring
  6. Initialise MQTT connection
"""

from __future__ import annotations

import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import create_tables
from .hardware.oled_display import OLEDDisplay
from .integrations.mqtt_publisher import initialize_mqtt, shutdown_mqtt
from .routers import sensors as sensors_router
from .routers import readings as readings_router
from .routers import websocket as ws_router
from .services.sensor_manager import SensorManager
from .services.display_manager import DisplayManager

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="BreatheEasy API",
    description="Raspberry Pi Air Quality Monitoring System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sensors_router.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(readings_router.router, prefix="/api/readings", tags=["readings"])
app.include_router(ws_router.router, tags=["websocket"])

# ---------------------------------------------------------------------------
# Singletons (set during startup)
# ---------------------------------------------------------------------------
_sensor_manager: SensorManager | None = None
_display_manager: DisplayManager | None = None


# ---------------------------------------------------------------------------
# Lifecycle hooks
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event() -> None:
    global _sensor_manager, _display_manager

    # 1. Database
    await create_tables()
    logger.info("Database tables created")

    # 2. SensorManager
    _sensor_manager = SensorManager()
    sensors_router.set_sensor_manager(_sensor_manager)
    ws_router.set_sensor_manager(_sensor_manager)

    # 3. DisplayManager
    oled = OLEDDisplay(
        i2c_address=settings.oled_address,
        timeout=settings.display_timeout,
    )
    _display_manager = DisplayManager(
        display=oled,
        motion_sensor=_sensor_manager.pir,
    )

    # 4 & 5. Start managers
    await _sensor_manager.start()
    await _display_manager.start()

    # 6. MQTT
    mqtt_host = settings.mqtt_broker_host
    mqtt_port = settings.mqtt_broker_port
    mqtt_ok = initialize_mqtt(mqtt_host, mqtt_port)
    if mqtt_ok:
        logger.info(f"MQTT connected to {mqtt_host}:{mqtt_port}")
    else:
        logger.warning("MQTT connection failed – continuing without MQTT")

    # Feed display with sensor data whenever a new poll completes
    asyncio.create_task(_display_feed_loop())

    logger.info("BreatheEasy API startup complete")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if _sensor_manager is not None:
        await _sensor_manager.stop()
    if _display_manager is not None:
        await _display_manager.stop()
    shutdown_mqtt()
    logger.info("BreatheEasy API shutdown complete")


async def _display_feed_loop() -> None:
    """Push sensor data to the display every poll cycle."""
    await asyncio.sleep(5)
    logger.info("Display feed loop started")
    while True:
        try:
            if _sensor_manager and _display_manager:
                data = _sensor_manager.get_latest_readings()
                if data:
                    logger.debug(f"Updating display with data: {data}")
                    await _display_manager.update_sensor_data(data)
                else:
                    logger.warning("No sensor data available for display")
        except Exception as exc:
            logger.error(f"Display feed error: {exc}", exc_info=True)
        await asyncio.sleep(settings.sensor_poll_interval)


# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "BreatheEasy API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    health = _sensor_manager.health_check() if _sensor_manager else {}
    return {"status": "healthy", "sensors": health}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
