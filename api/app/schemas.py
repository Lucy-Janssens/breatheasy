"""
Pydantic schemas for request/response serialisation.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SensorReadingOut(BaseModel):
    """A single persisted sensor reading."""
    id: int
    timestamp: datetime
    sensor_type: str
    metric: str
    value: float
    unit: str

    class Config:
        from_attributes = True


class SensorDataResponse(BaseModel):
    """Aggregated current sensor data returned by /api/sensors/current."""
    timestamp: str
    sensors: Dict[str, Any]


class SensorHealthResponse(BaseModel):
    bme680: bool
    dht22: bool
    motion: bool
    manager_running: bool


class ReadingStatsResponse(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    count: int = 0
    timeframe: str


class SystemEventOut(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    source: str
    message: str
    metadata_: Optional[str] = None

    class Config:
        from_attributes = True
