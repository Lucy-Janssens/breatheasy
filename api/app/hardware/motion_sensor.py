"""
Motion Sensor Interface
This module provides functions to read from motion sensors like PIR sensors.
For now, it provides mock implementations that can be replaced with real sensor libraries.
"""

from typing import Optional
import random
import time


def read_motion(pin: int = 27) -> bool:
    """
    Read motion sensor state
    Returns: True if motion detected, False otherwise
    """
    try:
        # Mock implementation - replace with real sensor reading
        # Simulate random motion detection with low probability
        motion_detected = random.random() < 0.1  # 10% chance of detecting motion
        return motion_detected

    except Exception as e:
        print(f"Error reading motion sensor: {e}")
        return False


def initialize_sensor(pin: int = 27) -> bool:
    """Initialize the motion sensor"""
    try:
        # Mock initialization - replace with real sensor initialization
        print(f"Initializing motion sensor on pin {pin}")
        time.sleep(0.1)  # Mock initialization time
        return True
    except Exception as e:
        print(f"Error initializing motion sensor: {e}")
        return False


class MotionSensor:
    """Motion sensor class for continuous monitoring"""

    def __init__(self, pin: int = 27):
        self.pin = pin
        self.initialized = initialize_sensor(pin)

    def detect_motion(self) -> bool:
        """Detect if motion is currently present"""
        if not self.initialized:
            return False
        return read_motion(self.pin)

    def wait_for_motion(self, timeout: Optional[float] = None) -> bool:
        """Wait for motion to be detected"""
        if not self.initialized:
            return False

        start_time = time.time()
        while timeout is None or (time.time() - start_time) < timeout:
            if self.detect_motion():
                return True
            time.sleep(0.1)  # Check every 100ms
        return False
