"""
/api/sensors – current sensor readings and health status.
"""

from fastapi import APIRouter

router = APIRouter()

# The sensor_manager is set at app startup from main.py
_sensor_manager = None


def set_sensor_manager(manager) -> None:
    global _sensor_manager
    _sensor_manager = manager


@router.get("/current")
async def get_current_readings():
    """Return the latest sensor readings from memory."""
    if _sensor_manager is None:
        return {"error": "SensorManager not initialised"}
    return _sensor_manager.get_latest_readings()


@router.get("/health")
async def get_sensor_health():
    """Return the health / connectivity status of every sensor."""
    if _sensor_manager is None:
        return {"error": "SensorManager not initialised"}
    return _sensor_manager.health_check()
