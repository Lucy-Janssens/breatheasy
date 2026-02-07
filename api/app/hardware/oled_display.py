"""
OLED Display Driver
Controls an SSD1306 128×64 OLED display over I2C (Whadda WPI438).
Supports auto-sleep after a configurable timeout and wake-on-motion.
"""

from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

try:
    from luma.oled.device import ssd1306
    from luma.core.interface.serial import i2c as luma_i2c
    from luma.core.render import canvas
    from PIL import ImageFont
    LUMA_AVAILABLE = True
except ImportError:
    LUMA_AVAILABLE = False
    logger.warning("luma.oled not available – mock display enabled")


class OLEDDisplay:
    """Driver for an SSD1306 OLED (128×64) via I2C."""

    WIDTH = 128
    HEIGHT = 64

    def __init__(self, i2c_address: int = 0x3C, timeout: int = 60) -> None:
        self._address = i2c_address
        self._timeout = timeout  # seconds before auto-sleep
        self._device: Optional[object] = None
        self._initialized = False
        self._is_on = False
        self._last_activity: float = time.time()

        self._font = None
        self._font_small = None
        self._initialize()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        if not LUMA_AVAILABLE:
            logger.info("OLED display running in mock mode")
            return

        try:
            serial = luma_i2c(port=1, address=self._address)
            self._device = ssd1306(serial, width=self.WIDTH, height=self.HEIGHT)
            
            # Force display on with max contrast
            self._device.show()
            self._device.contrast(255)
            
            self._load_fonts()
            self._initialized = True
            self._is_on = True
            self._last_activity = time.time()
            logger.info(f"SSD1306 OLED initialised at 0x{self._address:02X}")
        except Exception as exc:
            logger.error(f"OLED init failed: {exc}")

    def _load_fonts(self) -> None:
        try:
            self._font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11
            )
            self._font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9
            )
        except Exception:
            self._font = ImageFont.load_default()
            self._font_small = self._font

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def wake(self) -> None:
        """Turn the display on and reset the activity timer."""
        if self._initialized and not self._is_on:
            try:
                self._device.show()
            except Exception as exc:
                logger.error(f"OLED wake error: {exc}")
        self._is_on = True
        self._last_activity = time.time()
        logger.debug("OLED display woken")

    def sleep(self) -> None:
        """Turn the display off."""
        if self._initialized and self._is_on:
            try:
                self._device.hide()
            except Exception as exc:
                logger.error(f"OLED sleep error: {exc}")
        self._is_on = False
        logger.debug("OLED display sleeping")

    def should_sleep(self) -> bool:
        """Return True when the display has been idle longer than the timeout."""
        return (time.time() - self._last_activity) >= self._timeout

    def display_sensor_data(self, data: Dict) -> None:
        """
        Render sensor data on the OLED.

        Expected *data* layout::

            {
                'sensors': {
                    'bme680': {'temperature': 22.5, 'humidity': 45, 'pressure': 1013, 'air_quality_score': 75},
                    ...
                }
            }

        Display layout::

            BreatheEasy
            ────────────────────────
            Temp: 22.5°C   Hum: 45%
            Pressure: 1013 hPa
            Air: Good (75)
        """
        if not self._is_on:
            logger.warning("display_sensor_data called but display is OFF")
            return

        self._last_activity = time.time()

        sensors = data.get("sensors", {})
        bme = sensors.get("bme680", {})

        temp = bme.get("temperature")
        hum = bme.get("humidity")
        pres = bme.get("pressure")
        aq = bme.get("air_quality_score")

        temp_s = f"{temp:.1f}" if temp is not None else "--.-"
        hum_s = f"{hum:.0f}" if hum is not None else "--"
        pres_s = f"{pres:.0f}" if pres is not None else "----"
        aq_label = self._aq_label(aq)
        aq_s = f"{aq_label} ({aq:.0f})" if aq is not None else "N/A"

        logger.info(f"Rendering to OLED: T={temp_s} H={hum_s} P={pres_s} AQ={aq_s}")

        if not self._initialized:
            logger.debug(
                f"Mock OLED | T:{temp_s}°C  H:{hum_s}%  P:{pres_s}hPa  AQ:{aq_s}"
            )
            return

        try:
            with canvas(self._device) as draw:
                # Title
                draw.text((2, 0), "BreatheEasy", font=self._font, fill="white")
                draw.line([(0, 14), (self.WIDTH, 14)], fill="white")
                
                # Line 1: Temp & Humidity
                draw.text(
                    (2, 18),
                    f"T:{temp_s}\u00b0C H:{hum_s}%",
                    font=self._font_small,
                    fill="white",
                )
                
                # Line 2: Pressure
                draw.text(
                    (2, 32),
                    f"P:{pres_s} hPa",
                    font=self._font_small,
                    fill="white",
                )
                
                # Line 3: Air Quality
                draw.text(
                    (2, 46),
                    f"AQ: {aq_s}",
                    font=self._font_small,
                    fill="white",
                )
        except Exception as exc:
            logger.error(f"OLED render error: {exc}")

    def display_message(self, msg: str) -> None:
        """Show a single text message centred on the display."""
        self._last_activity = time.time()

        if not self._initialized:
            logger.debug(f"Mock OLED message: {msg}")
            return

        try:
            with canvas(self._device) as draw:
                bbox = draw.textbbox((0, 0), msg, font=self._font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x = (self.WIDTH - w) // 2
                y = (self.HEIGHT - h) // 2
                draw.text((x, y), msg, font=self._font, fill="white")
        except Exception as exc:
            logger.error(f"OLED message error: {exc}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _aq_label(score: Optional[float]) -> str:
        if score is None:
            return "N/A"
        if score >= 80:
            return "Excellent"
        if score >= 60:
            return "Good"
        if score >= 40:
            return "Moderate"
        if score >= 20:
            return "Poor"
        return "Very Poor"
