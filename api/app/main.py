from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables, async_session
from .routers import sensors, readings
from .config import settings
import asyncio
import logging
from .hardware import temperature, air_quality
from .services.sensor_service import SensorService
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
    await create_tables()
    # Start background sensor reading task
    asyncio.create_task(sensor_reading_task())

async def sensor_reading_task():
    """Background task to periodically read sensors and store data"""
    logger = logging.getLogger(__name__)

    # Wait a bit for everything to initialize
    await asyncio.sleep(5)

    logger.info("Starting sensor reading background task")

    while True:
        try:
            # Create a new database session for this reading cycle
            async with async_session() as db:
                sensor_service = SensorService(db)

                # Collect sensor readings
                readings = await sensor_service.poll_sensors()

                # Log successful collection
                logger.info(f"Collected {len(readings)} sensor readings")

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
