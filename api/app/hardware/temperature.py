"""
Temperature and Humidity Sensor Interface
This module provides functions to read from temperature/humidity sensors like DHT22.
For now, it provides mock implementations that can be replaced with real sensor libraries.
"""

from typing import Tuple, Optional
import random
import time


def read_temperature_humidity() -> Tuple[Optional[float], Optional[float]]:
    """
    Read temperature and humidity from sensor
    Returns: (temperature, humidity) in °C and % or None if reading fails
    """
    try:
        # Mock implementation - replace with real sensor readings
        temperature = random.uniform(15, 30)  # °C
        humidity = random.uniform(30, 80)  # %

        # Simulate occasional sensor failures
        if random.random() < 0.03:  # 3% chance of failure
            return None, None

        return temperature, humidity

    except Exception as e:
        print(f"Error reading temperature/humidity sensor: {e}")
        return None, None


def initialize_sensor(pin: int = 4) -> bool:
    """Initialize the temperature/humidity sensor"""
    try:
        # Mock initialization - replace with real sensor initialization
        print(f"Initializing DHT sensor on pin {pin}")
        time.sleep(0.1)  # Mock initialization time
        return True
    except Exception as e:
        print(f"Error initializing temperature/humidity sensor: {e}")
        return False


def read_temperature() -> Optional[float]:
    """Read only temperature"""
    temp, _ = read_temperature_humidity()
    return temp


def read_humidity() -> Optional[float]:
    """Read only humidity"""
    _, humidity = read_temperature_humidity()
    return humidity
