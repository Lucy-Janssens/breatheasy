from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from ..database import get_db
from ..models import SensorReading
from ..schemas import SensorReading as SensorReadingSchema

router = APIRouter()


@router.get("/latest", response_model=list[SensorReadingSchema])
async def get_latest_readings(db: AsyncSession = Depends(get_db)):
    """Get the latest reading for each sensor type"""
    # This is a simplified implementation - in production you'd want to get the latest per sensor
    result = await db.execute(
        select(SensorReading)
        .order_by(desc(SensorReading.timestamp))
        .limit(100)  # Get recent readings and filter in memory
    )
    readings = result.scalars().all()

    # Group by sensor_type and get the most recent for each
    latest_by_type = {}
    for reading in readings:
        if reading.sensor_type not in latest_by_type:
            latest_by_type[reading.sensor_type] = reading
        elif reading.timestamp > latest_by_type[reading.sensor_type].timestamp:
            latest_by_type[reading.sensor_type] = reading

    return list(latest_by_type.values())


@router.get("/sensor/{sensor_id}", response_model=list[SensorReadingSchema])
async def get_sensor_readings(
    sensor_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get readings for a specific sensor"""
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    readings = result.scalars().all()
    return readings


@router.get("/history", response_model=list[SensorReadingSchema])
async def get_readings_history(
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: AsyncSession = Depends(get_db)
):
    """Get readings from the last N hours"""
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.timestamp >= since)
        .order_by(desc(SensorReading.timestamp))
    )
    readings = result.scalars().all()
    return readings
