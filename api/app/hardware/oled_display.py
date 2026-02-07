"""
OLED Display Driver
Controls an SSD1306 128x64 OLED display over I2C using raw smbus2 commands.
Whadda WPI438 requires direct I2C writes (luma driver does not work).
Supports auto-sleep after a configurable timeout and wake-on-motion.
"""

from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

try:
    from smbus2 import SMBus, i2c_msg
    from PIL import Image, ImageDraw, ImageFont
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False
    logger.warning("smbus2/Pillow not available - mock display enabled")


class OLEDDisplay:
    """Driver for an SSD1306 OLED (128x64) via raw I2C."""

    WIDTH = 128
    HEIGHT = 64
    PAGES = HEIGHT // 8  # 8 pages of 8 pixels each

    # SSD1306 control bytes
    _CMD = 0x00   # Co=0, D/C#=0 -> command
    _DATA = 0x40  # Co=0, D/C#=1 -> data (GDDRAM)

    _INIT_SEQUENCE = [
        0xAE,        # Display OFF
        0xD5, 0x80,  # Clock divide ratio
        0xA8, 0x3F,  # Multiplex ratio (64-1)
        0xD3, 0x00,  # Display offset = 0
        0x40,        # Start line = 0
        0x8D, 0x14,  # Charge pump ON
        0x20, 0x00,  # Horizontal addressing mode
        0xA1,        # Segment remap (column 127 -> SEG0)
        0xC8,        # COM scan descending
        0xDA, 0x12,  # COM pins config
        0x81, 0xFF,  # Contrast max
        0xD9, 0xF1,  # Pre-charge period
        0xDB, 0x40,  # VCOM deselect level
        0xA4,        # Display from RAM
        0xA6,        # Normal display (not inverted)
        0xAF,        # Display ON
    ]

    def __init__(self, i2c_address: int = 0x3C, timeout: int = 60) -> None:
        self._address = i2c_address
        self._timeout = timeout
        self._bus: Optional[SMBus] = None
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
        if not SMBUS_AVAILABLE:
            logger.info("OLED display running in mock mode")
            return

        try:
            self._bus = SMBus(1)

            # Send full init sequence one command at a time
            for cmd in self._INIT_SEQUENCE:
                self._bus.write_byte_data(self._address, self._CMD, cmd)
                time.sleep(0.002)

            # Wait for display controller to stabilise
            time.sleep(0.1)

            self._load_fonts()
            self._initialized = True
            self._is_on = True
            self._last_activity = time.time()
            logger.info(f"SSD1306 OLED initialised at 0x{self._address:02X}")

            # Show startup test pattern (all-white) to verify I2C data path
            self._show_test_pattern()

        except Exception as exc:
            logger.error(f"OLED init failed: {exc}", exc_info=True)

    def _show_test_pattern(self) -> None:
        """Fill entire screen white to verify init + data writes work."""
        try:
            buf = bytes([0xFF] * (self.WIDTH * self.PAGES))
            self._send_framebuffer(buf)
            logger.info("OLED startup test pattern (all-white) sent successfully")
            time.sleep(1.0)
            # Clear screen
            buf = bytes([0x00] * (self.WIDTH * self.PAGES))
            self._send_framebuffer(buf)
            logger.info("OLED screen cleared after test pattern")
        except Exception as exc:
            logger.error(f"OLED test pattern failed: {exc}", exc_info=True)

    def _load_fonts(self) -> None:
        try:
            self._font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11
            )
            self._font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9
            )
            logger.info("Loaded DejaVu fonts for OLED")
        except Exception:
            self._font = ImageFont.load_default()
            self._font_small = self._font
            logger.warning("DejaVu fonts not found, using default bitmap font")

    # ------------------------------------------------------------------
    # Low-level I2C write
    # ------------------------------------------------------------------

    def _send_command(self, cmd: int) -> None:
        """Send a single command byte to the SSD1306."""
        if self._bus:
            self._bus.write_byte_data(self._address, self._CMD, cmd)

    def _send_data_chunk(self, data: list) -> None:
        """Send a chunk of data bytes using raw I2C write (i2c_rdwr).

        Uses i2c_msg for reliability instead of SMBus block write.
        The data control byte 0x40 is prepended automatically.
        """
        if not self._bus:
            return
        payload = [self._DATA] + data
        msg = i2c_msg.write(self._address, payload)
        self._bus.i2c_rdwr(msg)

    def _send_framebuffer(self, buf: bytes) -> None:
        """Write pixel buffer to the SSD1306 GDDRAM."""
        if not self._bus:
            logger.warning("_send_framebuffer called but no I2C bus")
            return

        try:
            # Set column address range: 0 -> 127
            self._send_command(0x21)
            self._send_command(0)
            self._send_command(self.WIDTH - 1)
            # Set page address range: 0 -> 7
            self._send_command(0x22)
            self._send_command(0)
            self._send_command(self.PAGES - 1)

            # Write data in 16-byte chunks using raw I2C
            chunk_size = 16
            for i in range(0, len(buf), chunk_size):
                chunk = list(buf[i:i + chunk_size])
                self._send_data_chunk(chunk)

            logger.debug(f"Framebuffer sent: {len(buf)} bytes, "
                         f"non-zero: {sum(1 for b in buf if b)}")
        except Exception as exc:
            logger.error(f"Framebuffer write failed: {exc}", exc_info=True)

    # ------------------------------------------------------------------
    # Render helpers
    # ------------------------------------------------------------------

    def _image_to_buffer(self, img: Image.Image) -> bytes:
        """Convert a PIL image to SSD1306 page-format buffer.

        Uses 'L' (grayscale) mode to avoid PIL '1' mode quirks,
        then thresholds at 128 to produce the 1-bit buffer.
        """
        # Convert to grayscale to avoid PIL "1" mode dithering/pixel issues
        grey = img.convert("L")
        pixels = grey.load()

        buf = bytearray(self.WIDTH * self.PAGES)
        for page in range(self.PAGES):
            for x in range(self.WIDTH):
                byte_val = 0
                for bit in range(8):
                    y = page * 8 + bit
                    if y < self.HEIGHT and pixels[x, y] > 128:
                        byte_val |= (1 << bit)
                buf[page * self.WIDTH + x] = byte_val
        return bytes(buf)

    def _render(self, img: Image.Image) -> None:
        """Render a PIL image to the physical display."""
        buf = self._image_to_buffer(img)
        nonzero = sum(1 for b in buf if b)
        logger.info(f"Rendering buffer: {len(buf)} bytes, {nonzero} non-zero")
        if nonzero == 0:
            logger.warning("Buffer is all zeros - nothing to display!")
        self._send_framebuffer(buf)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def wake(self) -> None:
        """Turn the display on and reset the activity timer."""
        if self._initialized and not self._is_on:
            self._send_command(0xAF)  # Display ON
        self._is_on = True
        self._last_activity = time.time()
        logger.debug("OLED display woken")

    def sleep(self) -> None:
        """Turn the display off."""
        if self._initialized and self._is_on:
            self._send_command(0xAE)  # Display OFF
        self._is_on = False
        logger.debug("OLED display sleeping")

    def should_sleep(self) -> bool:
        """Return True when the display has been idle longer than the timeout."""
        return (time.time() - self._last_activity) >= self._timeout

    def display_sensor_data(self, data: Dict) -> None:
        """Render sensor data on the OLED."""
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
                f"Mock OLED | T:{temp_s}C  H:{hum_s}%  P:{pres_s}hPa  AQ:{aq_s}"
            )
            return

        try:
            img = Image.new("L", (self.WIDTH, self.HEIGHT), 0)
            draw = ImageDraw.Draw(img)

            # Title
            draw.text((2, 0), "BreatheEasy", font=self._font, fill=255)
            draw.line([(0, 14), (self.WIDTH, 14)], fill=255)

            # Temp & Humidity
            draw.text((2, 18), f"T:{temp_s}C  H:{hum_s}%",
                       font=self._font_small, fill=255)

            # Pressure
            draw.text((2, 32), f"P:{pres_s} hPa",
                       font=self._font_small, fill=255)

            # Air Quality
            draw.text((2, 46), f"AQ: {aq_s}",
                       font=self._font_small, fill=255)

            self._render(img)
        except Exception as exc:
            logger.error(f"OLED render error: {exc}", exc_info=True)

    def display_message(self, msg: str) -> None:
        """Show a single text message centred on the display."""
        self._last_activity = time.time()

        if not self._initialized:
            logger.debug(f"Mock OLED message: {msg}")
            return

        try:
            img = Image.new("L", (self.WIDTH, self.HEIGHT), 0)
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), msg, font=self._font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (self.WIDTH - w) // 2
            y = (self.HEIGHT - h) // 2
            draw.text((x, y), msg, font=self._font, fill=255)
            self._render(img)
        except Exception as exc:
            logger.error(f"OLED message error: {exc}", exc_info=True)

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
