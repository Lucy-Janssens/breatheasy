"""
DHT22 Sensor Driver
Backup temperature / humidity sensor on a single-wire GPIO pin.
Enforces a minimum 2-second interval between reads (DHT22 hardware limit).
"""

from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

try:
    import board
    import adafruit_dht
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False
    logger.warning("adafruit-circuitpython-dht not available – mock mode enabled")

# Map from integer pin numbers to board pin objects
_PIN_MAP = {
    4: getattr(board, "D4", None) if DHT_AVAILABLE else None,
    17: getattr(board, "D17", None) if DHT_AVAILABLE else None,
    18: getattr(board, "D18", None) if DHT_AVAILABLE else None,
    27: getattr(board, "D27", None) if DHT_AVAILABLE else None,
}


class DHTSensor:
    """Driver for the DHT22 temperature/humidity sensor."""

    _MIN_READ_INTERVAL: float = 2.0  # seconds

    def __init__(self, pin: int = 17, sensor_type: str = "DHT22") -> None:
        self._pin = pin
        self._sensor_type = sensor_type
        self._sensor: Optional[object] = None
        self._initialized = False
        self._last_read_time: float = 0.0

        self._initialize()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        if not DHT_AVAILABLE:
            logger.info("DHT22 running in mock mode (library unavailable)")
            return

        board_pin = _PIN_MAP.get(self._pin)
        if board_pin is None:
            logger.error(f"Unsupported GPIO pin {self._pin} for DHT sensor")
            return

        try:
            if self._sensor_type == "DHT22":
                self._sensor = adafruit_dht.DHT22(board_pin, use_pulseio=False)
            else:
                self._sensor = adafruit_dht.DHT11(board_pin, use_pulseio=False)
            self._initialized = True
            logger.info(f"{self._sensor_type} initialised on GPIO{self._pin}")
        except Exception as exc:
            logger.error(f"DHT init failed: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(self) -> Dict[str, float]:
        """Return temperature and humidity.  Respects 2 s minimum interval."""
        if not self._initialized:
            return self._mock_read()

        # Enforce minimum interval
        elapsed = time.time() - self._last_read_time
        if elapsed < self._MIN_READ_INTERVAL:
            time.sleep(self._MIN_READ_INTERVAL - elapsed)

        # DHT sensors can throw checksum errors — retry up to 3 times
        for attempt in range(3):
            try:
                temperature = self._sensor.temperature
                humidity = self._sensor.humidity
                self._last_read_time = time.time()

                if temperature is not None and humidity is not None:
                    return {
                        "temperature": round(temperature, 2),
                        "humidity": round(humidity, 2),
                    }
            except RuntimeError as exc:
                logger.warning(
                    f"DHT read attempt {attempt + 1}/3 failed: {exc}"
                )
                time.sleep(self._MIN_READ_INTERVAL)
            except Exception as exc:
                logger.error(f"DHT unexpected error: {exc}")
                break

        logger.error("DHT22: all read attempts exhausted")
        return self._mock_read()

    def health_check(self) -> bool:
        """Try up to 3 reads; return True if any succeeds."""
        if not self._initialized:
            return False
        for _ in range(3):
            try:
                t = self._sensor.temperature
                if t is not None:
                    return True
            except Exception:
                time.sleep(self._MIN_READ_INTERVAL)
        return False

    def cleanup(self) -> None:
        """Release the GPIO pin."""
        if self._sensor is not None:
            try:
                self._sensor.exit()
            except Exception:
                pass
            self._sensor = None
            self._initialized = False
            logger.info("DHT sensor cleaned up")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_read() -> Dict[str, float]:
        import random

        return {
            "temperature": round(random.uniform(18.0, 28.0), 2),
            "humidity": round(random.uniform(30.0, 65.0), 2),
        }
