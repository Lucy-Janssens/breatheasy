"""
BME680 Sensor Driver
Reads temperature, humidity, pressure, and gas resistance from BME680 via I2C.
Calculates an air quality score (0-100) based on gas resistance.
"""

from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

try:
    import board
    import busio
    import adafruit_bme680
    BME680_AVAILABLE = True
except ImportError:
    BME680_AVAILABLE = False
    logger.warning("adafruit-circuitpython-bme680 not available – mock mode enabled")


class BME680Sensor:
    """Driver for the BME680 environmental sensor over I2C."""

    # Gas resistance baseline for air quality calculation (Ohms).
    # A well-ventilated room typically reads 50 kΩ–200 kΩ.
    _GAS_BASELINE: float = 150_000.0
    _HUM_BASELINE: float = 40.0  # optimal humidity for air quality
    _HUM_WEIGHT: float = 0.25    # humidity contributes 25 %
    _GAS_WEIGHT: float = 0.75    # gas resistance contributes 75 %

    def __init__(self, i2c_address: int = 0x76) -> None:
        self._address = i2c_address
        self._sensor: Optional[object] = None
        self._initialized = False
        self._gas_readings: list[float] = []
        self._gas_baseline: float = self._GAS_BASELINE

        self._initialize()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        if not BME680_AVAILABLE:
            logger.info("BME680 running in mock mode (library unavailable)")
            return

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self._sensor = adafruit_bme680.Adafruit_BME680_I2C(
                i2c, address=self._address
            )
            # Configure oversampling & heater for gas readings
            self._sensor.sea_level_pressure = 1013.25
            self._sensor.temperature_oversample = 8
            self._sensor.humidity_oversample = 2
            self._sensor.pressure_oversample = 4
            self._sensor.filter_size = 3
            self._sensor.gas_heater_temp = 320
            self._sensor.gas_heater_duration = 150
            self._initialized = True
            logger.info(
                f"BME680 initialised at 0x{self._address:02X}"
            )
        except Exception as exc:
            logger.error(f"BME680 init failed: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(self) -> Dict[str, float]:
        """Return a dict with temperature, humidity, pressure, and air_quality_score."""
        if not self._initialized:
            return self._mock_read()

        try:
            temperature: float = self._sensor.temperature
            humidity: float = self._sensor.humidity
            pressure: float = self._sensor.pressure
            gas: float = self._sensor.gas

            # Accumulate gas readings for a running baseline
            self._gas_readings.append(gas)
            if len(self._gas_readings) > 50:
                self._gas_readings = self._gas_readings[-50:]
                self._gas_baseline = sum(self._gas_readings) / len(self._gas_readings)

            air_quality_score = self._calculate_air_quality(gas, humidity)

            return {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
                "air_quality_score": round(air_quality_score, 1),
            }
        except Exception as exc:
            logger.error(f"BME680 read error: {exc}")
            return self._mock_read()

    def health_check(self) -> bool:
        """Return True when the sensor can be read successfully."""
        if not self._initialized:
            return False
        try:
            _ = self._sensor.temperature
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _calculate_air_quality(self, gas: float, humidity: float) -> float:
        """Compute a 0-100 air quality score from gas resistance & humidity."""
        # Gas contribution (higher resistance → cleaner air)
        gas_offset = self._gas_baseline - gas
        if gas_offset > 0:
            gas_score = (gas / self._gas_baseline) * (self._GAS_WEIGHT * 100)
        else:
            gas_score = self._GAS_WEIGHT * 100

        # Humidity contribution (closer to 40 % → better score)
        hum_offset = humidity - self._HUM_BASELINE
        if hum_offset > 0:
            hum_score = (
                (100 - self._HUM_BASELINE - hum_offset)
                / (100 - self._HUM_BASELINE)
                * (self._HUM_WEIGHT * 100)
            )
        else:
            hum_score = (
                (self._HUM_BASELINE + hum_offset)
                / self._HUM_BASELINE
                * (self._HUM_WEIGHT * 100)
            )

        return max(0.0, min(100.0, gas_score + hum_score))

    @staticmethod
    def _mock_read() -> Dict[str, float]:
        import random

        return {
            "temperature": round(random.uniform(18.0, 28.0), 2),
            "humidity": round(random.uniform(30.0, 65.0), 2),
            "pressure": round(random.uniform(1005.0, 1025.0), 2),
            "air_quality_score": round(random.uniform(40.0, 95.0), 1),
        }
