"""
Legacy SensorService kept for backward compatibility.
The new SensorManager in sensor_manager.py is the primary service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import SensorReading


class SensorService:
    """Legacy service – thin wrapper around DB queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest_readings(self, limit: int = 10) -> List[SensorReading]:
        result = await self.db.execute(
            select(SensorReading)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
