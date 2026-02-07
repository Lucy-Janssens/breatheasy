"""
SQLAlchemy ORM models for BreatheEasy.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Text
from sqlalchemy.sql import func
from .database import Base


class SensorReading(Base):
    """Individual sensor metric stored every poll cycle."""

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sensor_type = Column(String, nullable=False)   # bme680, dht22, motion
    metric = Column(String, nullable=False)         # temperature, humidity, pressure, air_quality
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)           # celsius, percent, hPa, score

    __table_args__ = (
        Index("ix_sensor_metric_ts", "sensor_type", "metric", "timestamp"),
    )


class SystemEvent(Base):
    """Structured log / event table."""

    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String, nullable=False)     # info, warning, error
    source = Column(String, nullable=False)         # sensor_manager, display_manager, api
    message = Column(String, nullable=False)
    metadata_ = Column("metadata", Text, nullable=True)  # JSON string
