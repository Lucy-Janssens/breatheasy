"""
/api/readings – historical data and statistical aggregations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func as sqlfunc
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import SensorReading

router = APIRouter()


@router.get("/history")
async def get_readings_history(
    sensor_type: Optional[str] = Query(None, description="e.g. bme680, dht22, motion"),
    metric: Optional[str] = Query(None, description="e.g. temperature, humidity"),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Return historical sensor readings with optional filters."""
    query = select(SensorReading).order_by(desc(SensorReading.timestamp))

    if sensor_type:
        query = query.where(SensorReading.sensor_type == sensor_type)
    if metric:
        query = query.where(SensorReading.metric == metric)
    if start_time:
        query = query.where(SensorReading.timestamp >= start_time)
    if end_time:
        query = query.where(SensorReading.timestamp <= end_time)

    query = query.limit(limit)
    result = await db.execute(query)
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "sensor_type": r.sensor_type,
            "metric": r.metric,
            "value": r.value,
            "unit": r.unit,
        }
        for r in rows
    ]


@router.get("/stats")
async def get_readings_stats(
    metric: str = Query(..., description="e.g. temperature, humidity, air_quality_score"),
    timeframe: str = Query("24h", description="1h, 24h, or 7d"),
    db: AsyncSession = Depends(get_db),
):
    """Return min / max / avg for a given metric over a timeframe."""
    now = datetime.now(timezone.utc)
    delta_map = {"1h": timedelta(hours=1), "24h": timedelta(hours=24), "7d": timedelta(days=7)}
    delta = delta_map.get(timeframe, timedelta(hours=24))
    since = now - delta

    query = (
        select(
            sqlfunc.min(SensorReading.value).label("min"),
            sqlfunc.max(SensorReading.value).label("max"),
            sqlfunc.avg(SensorReading.value).label("avg"),
            sqlfunc.count(SensorReading.id).label("count"),
        )
        .where(SensorReading.metric == metric)
        .where(SensorReading.timestamp >= since)
    )

    result = await db.execute(query)
    row = result.one_or_none()

    if row is None or row.count == 0:
        return {"min": None, "max": None, "avg": None, "count": 0, "timeframe": timeframe}

    return {
        "min": round(row.min, 2) if row.min is not None else None,
        "max": round(row.max, 2) if row.max is not None else None,
        "avg": round(row.avg, 2) if row.avg is not None else None,
        "count": row.count,
        "timeframe": timeframe,
    }
