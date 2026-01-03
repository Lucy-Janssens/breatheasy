from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SensorBase(BaseModel):
    name: str
    type: str
    location: str
    is_active: bool = True


class SensorCreate(SensorBase):
    id: str


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class Sensor(SensorBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SensorReadingBase(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReading(SensorReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AirQualityData(BaseModel):
    pm25: float
    pm10: float
    co2: float
    voc: float
    temperature: float
    humidity: float
    timestamp: datetime


class SystemStatusBase(BaseModel):
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float


class SystemStatus(SystemStatusBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SystemStatusResponse(SystemStatusBase):
    timestamp: datetime
