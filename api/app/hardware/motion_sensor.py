"""
Motion Sensor Interface
This module provides functions to read from PIR motion sensors.
"""

from typing import Optional
import time
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO library not available. Using mock motion sensor.")

# Configure logging
logger = logging.getLogger(__name__)

# Global GPIO state
_gpio_initialized = False

def _initialize_gpio():
    """Initialize GPIO if not already done"""
    global _gpio_initialized
    if _gpio_initialized:
        return True

    if not GPIO_AVAILABLE:
        logger.warning("GPIO not available - using mock motion sensor")
        return False

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        _gpio_initialized = True
        logger.info("GPIO initialized for motion sensor")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize GPIO: {e}")
        return False

def read_motion(pin: int = 4) -> bool:
    """
    Read motion sensor state
    Returns: True if motion detected, False otherwise

    Note: pin should be BCM GPIO number (4 for physical pin 7)
    """
    try:
        if not _initialize_gpio():
            # Mock implementation when GPIO not available
            import random
            return random.random() < 0.1  # 10% chance of detecting motion

        # Set up pin as input
        GPIO.setup(pin, GPIO.IN)

        # Read the pin state
        motion_detected = GPIO.input(pin) == GPIO.HIGH

        return motion_detected

    except Exception as e:
        logger.error(f"Error reading motion sensor: {e}")
        return False


def initialize_sensor(pin: int = 4) -> bool:
    """
    Initialize the motion sensor
    Note: pin should be BCM GPIO number (4 for physical pin 7)
    """
    try:
        if not _initialize_gpio():
            logger.warning("Motion sensor initialization skipped - GPIO not available")
            return False

        # Set up pin as input with pull-down resistor
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        logger.info(f"Motion sensor initialized on GPIO pin {pin}")
        return True
    except Exception as e:
        logger.error(f"Error initializing motion sensor: {e}")
        return False


class MotionSensor:
    """Motion sensor class for continuous monitoring"""

    def __init__(self, pin: int = 4):
        """
        Initialize motion sensor
        pin: BCM GPIO pin number (default 4 = physical pin 7)
        """
        self.pin = pin
        self.initialized = initialize_sensor(pin)

        # Motion detection state
        self.last_motion_time = 0
        self.motion_timeout = 30  # seconds to keep display active after motion

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
                self.last_motion_time = time.time()
                return True
            time.sleep(0.1)  # Check every 100ms
        return False

    def should_display_be_active(self) -> bool:
        """Check if display should be active based on recent motion"""
        if not self.initialized:
            return True  # Always active if no motion sensor

        time_since_motion = time.time() - self.last_motion_time
        return time_since_motion < self.motion_timeout

    def get_status(self) -> dict:
        """Get motion sensor status"""
        return {
            "initialized": self.initialized,
            "gpio_available": GPIO_AVAILABLE,
            "pin": self.pin,
            "current_motion": self.detect_motion() if self.initialized else False,
            "last_motion_seconds": time.time() - self.last_motion_time,
            "display_active": self.should_display_be_active()
        }
