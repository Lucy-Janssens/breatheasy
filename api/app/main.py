from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables, async_session
from .routers import sensors, readings
from .config import settings
import asyncio
import logging
import os
from .hardware import temperature, air_quality, lcd_display
from .services.sensor_service import SensorService
from .integrations.mqtt_publisher import initialize_mqtt, shutdown_mqtt
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="Breatheasy API",
    description="Air Quality Monitoring System API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(readings.router, prefix="/api/readings", tags=["readings"])


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger(__name__)
    await create_tables()
    
    # Initialize MQTT connection
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "mqtt")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    
    logger.info(f"Initializing MQTT connection to {mqtt_host}:{mqtt_port}")
    mqtt_success = initialize_mqtt(mqtt_host, mqtt_port)
    
    if mqtt_success:
        logger.info("MQTT connection initialized successfully")
    else:
        logger.warning("Failed to initialize MQTT connection - continuing without MQTT")
    
    # Start background sensor reading task
    asyncio.create_task(sensor_reading_task())


@app.on_event("shutdown")
async def shutdown_event():
    logger = logging.getLogger(__name__)
    logger.info("Shutting down MQTT connection")
    shutdown_mqtt()

async def sensor_reading_task():
    """Background task to periodically read sensors and store data"""
    logger = logging.getLogger(__name__)

    # Wait a bit for everything to initialize
    await asyncio.sleep(5)

    logger.info("Starting sensor reading background task")
    
    # Initialize LCD display
    lcd = lcd_display.get_lcd_display()

    while True:
        try:
            # Create a new database session for this reading cycle
            async with async_session() as db:
                sensor_service = SensorService(db)

                # Collect sensor readings
                readings = await sensor_service.poll_sensors()

                # Log successful collection
                logger.info(f"Collected {len(readings)} sensor readings")
                
                # Update LCD display with latest readings
                temp_val = None
                humidity_val = None
                pm25_val = None
                co2_val = None
                
                for reading in readings:
                    if reading.sensor_type == "temperature":
                        temp_val = reading.value
                    elif reading.sensor_type == "humidity":
                        humidity_val = reading.value
                    elif reading.sensor_type == "pm25":
                        pm25_val = reading.value
                    elif reading.sensor_type == "co2":
                        co2_val = reading.value
                
                # Update LCD with current values
                lcd_display.update_display(
                    temperature=temp_val,
                    humidity=humidity_val,
                    pm25=pm25_val,
                    co2=co2_val
                )

        except Exception as e:
            logger.error(f"Error in sensor reading task: {e}")

        # Wait before next reading (configured interval)
        await asyncio.sleep(settings.sensor_poll_interval)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Breatheasy API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
