"""
Temperature and Humidity Sensor Interface
This module provides functions to read temperature and humidity from BME680 sensor.
"""

from typing import Tuple, Optional
import logging
from .air_quality import _bme680_sensor

# Configure logging
logger = logging.getLogger(__name__)

def read_temperature_humidity() -> Tuple[Optional[float], Optional[float]]:
    """
    Read temperature and humidity from BME680 sensor
    Returns: (temperature, humidity) in °C and % or None if reading fails
    """
    global _bme680_sensor

    if not _bme680_sensor:
        from . import air_quality
        if not air_quality.initialize_sensor():
            logger.warning("BME680 sensor not available - using mock data")
            return _get_mock_readings()

    try:
        temperature = _bme680_sensor.temperature
        humidity = _bme680_sensor.humidity

        if temperature is None or humidity is None:
            logger.warning("BME680 returned None values for temperature/humidity")
            return None, None

        logger.debug(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
        return temperature, humidity

    except Exception as e:
        logger.error(f"Error reading temperature/humidity from BME680: {e}")
        return None, None


def _get_mock_readings() -> Tuple[Optional[float], Optional[float]]:
    """Provide mock readings when sensor is not available"""
    import random

    temperature = random.uniform(15, 30)  # °C
    humidity = random.uniform(30, 80)  # %

    # Simulate occasional sensor failures
    if random.random() < 0.03:  # 3% chance of failure
        return None, None

    return temperature, humidity


def initialize_sensor() -> bool:
    """Initialize the temperature/humidity sensor (BME680)"""
    # BME680 is initialized through the air_quality module
    from . import air_quality
    return air_quality.initialize_sensor()


def read_temperature() -> Optional[float]:
    """Read only temperature"""
    temp, _ = read_temperature_humidity()
    return temp


def read_humidity() -> Optional[float]:
    """Read only humidity"""
    _, humidity = read_temperature_humidity()
    return humidity


def get_sensor_details() -> dict:
    """Get detailed sensor information"""
    global _bme680_sensor

    if not _bme680_sensor:
        return {"status": "not_initialized", "available": False}

    try:
        return {
            "status": "active",
            "available": True,
            "sensor_type": "BME680",
            "temperature": _bme680_sensor.temperature,
            "humidity": _bme680_sensor.humidity,
            "pressure": _bme680_sensor.pressure,
            "altitude": _bme680_sensor.altitude
        }
    except Exception as e:
        logger.error(f"Error getting sensor details: {e}")
        return {"status": "error", "available": False, "error": str(e)}
