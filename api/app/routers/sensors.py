from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Sensor
from ..schemas import Sensor as SensorSchema, SensorCreate, SensorUpdate

router = APIRouter()


@router.get("/", response_model=list[SensorSchema])
async def get_sensors(db: AsyncSession = Depends(get_db)):
    """Get all sensors"""
    result = await db.execute(select(Sensor))
    sensors = result.scalars().all()
    return sensors


@router.get("/{sensor_id}", response_model=SensorSchema)
async def get_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific sensor by ID"""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.post("/", response_model=SensorSchema)
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_db)):
    """Create a new sensor"""
    # Check if sensor already exists
    result = await db.execute(select(Sensor).where(Sensor.id == sensor.id))
    existing_sensor = result.scalar_one_or_none()
    if existing_sensor:
        raise HTTPException(status_code=400, detail="Sensor with this ID already exists")

    db_sensor = Sensor(**sensor.dict())
    db.add(db_sensor)
    await db.commit()
    await db.refresh(db_sensor)
    return db_sensor


@router.put("/{sensor_id}", response_model=SensorSchema)
async def update_sensor(
    sensor_id: str,
    sensor_update: SensorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a sensor"""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    update_data = sensor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sensor, field, value)

    await db.commit()
    await db.refresh(sensor)
    return sensor


@router.delete("/{sensor_id}")
async def delete_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a sensor"""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    await db.delete(sensor)
    await db.commit()
    return {"message": "Sensor deleted successfully"}
