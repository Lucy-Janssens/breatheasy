"""
OLED Display Interface
This module provides functions to control an SSD1322 OLED display.
"""

from typing import Optional
import time
import logging
from .sensor_detection import get_ssd1322_address

try:
    import adafruit_ssd1322
    import board
    import busio
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    SSD1322_AVAILABLE = True
except ImportError:
    SSD1322_AVAILABLE = False
    logging.warning("Adafruit SSD1322 library not available. Using mock display.")

# Configure logging
logger = logging.getLogger(__name__)

class OLED_Display:
    def __init__(self, reset_pin: int = 24):
        self.reset_pin = reset_pin
        self.display = None
        self.initialized = self._initialize()

        # Display properties
        self.width = 256
        self.height = 64

    def _initialize(self) -> bool:
        """Initialize the SSD1322 OLED display"""
        if not SSD1322_AVAILABLE:
            logger.warning("SSD1322 library not available - using mock display")
            return False

        try:
            # Auto-detect SSD1322 address
            ssd1322_addr = get_ssd1322_address()
            if ssd1322_addr is None:
                logger.error("SSD1322 display not detected on I2C bus")
                return False

            # Initialize I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Initialize reset pin
            reset = digitalio.DigitalInOut(getattr(board, f'D{self.reset_pin}'))
            reset.direction = digitalio.Direction.OUTPUT

            # Initialize SSD1322 display
            self.display = adafruit_ssd1322.SSD1322_I2C(
                self.width, self.height, i2c,
                addr=ssd1322_addr,
                reset=reset
            )

            # Clear display
            self.clear()

            logger.info(f"SSD1322 display initialized at address 0x{ssd1322_addr:02X}")
            return True

        except Exception as e:
            logger.error(f"Error initializing SSD1322 display: {e}")
            return False

    def display_reading(self, sensor_type: str, value: float, unit: str):
        """Display a sensor reading on the screen"""
        if not self.initialized:
            self._mock_display(f"{sensor_type.upper()}: {value:.1f} {unit}")
            return

        try:
            # Create image for drawing
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Use default font
            font = ImageFont.load_default()

            # Format reading
            text = f"{sensor_type.upper()}: {value:.1f} {unit}"

            # Draw text centered
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2

            draw.text((x, y), text, font=font, fill=255)

            # Display image
            self.display.image(image)
            self.display.show()

        except Exception as e:
            logger.error(f"Error displaying reading: {e}")

    def display_message(self, message: str, line: int = 0):
        """Display a custom message"""
        if not self.initialized:
            self._mock_display(f"Line {line}: {message}")
            return

        try:
            # Create image for drawing
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Use default font
            font = ImageFont.load_default()

            # Calculate line position
            line_height = 12
            y = line * line_height + 2

            # Draw text
            draw.text((2, y), message, font=font, fill=255)

            # Display image
            self.display.image(image)
            self.display.show()

        except Exception as e:
            logger.error(f"Error displaying message: {e}")

    def display_air_quality_status(self, pm25: Optional[float], co2: Optional[float]):
        """Display air quality status"""
        if not self.initialized:
            status = "Air Quality: "
            if pm25 is not None:
                if pm25 > 35:
                    status += "PM2.5 POOR "
                elif pm25 > 12:
                    status += "PM2.5 MODERATE "
                else:
                    status += "PM2.5 GOOD "
            if co2 is not None:
                if co2 > 1000:
                    status += "CO2 POOR"
                elif co2 > 800:
                    status += "CO2 MODERATE"
                else:
                    status += "CO2 GOOD"
            self._mock_display(status)
            return

        try:
            # Create image for drawing
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Use default font
            font = ImageFont.load_default()

            status = "Air Quality:"
            y = 2
            draw.text((2, y), status, font=font, fill=255)

            y += 15
            if pm25 is not None:
                pm25_status = "PM2.5: "
                if pm25 > 35:
                    pm25_status += "POOR"
                elif pm25 > 12:
                    pm25_status += "MODERATE"
                else:
                    pm25_status += "GOOD"
                draw.text((2, y), pm25_status, font=font, fill=255)
                y += 12

            if co2 is not None:
                co2_status = "CO2: "
                if co2 > 1000:
                    co2_status += "POOR"
                elif co2 > 800:
                    co2_status += "MODERATE"
                else:
                    co2_status += "GOOD"
                draw.text((2, y), co2_status, font=font, fill=255)

            # Display image
            self.display.image(image)
            self.display.show()

        except Exception as e:
            logger.error(f"Error displaying air quality status: {e}")

    def clear(self):
        """Clear the display"""
        if not self.initialized:
            self._mock_display("Display cleared")
            return

        try:
            # Create blank image
            image = Image.new("1", (self.width, self.height))
            self.display.image(image)
            self.display.show()
        except Exception as e:
            logger.error(f"Error clearing display: {e}")

    def set_brightness(self, level: int):
        """Set display brightness (0-255)"""
        if not self.initialized:
            self._mock_display(f"Brightness set to {level}")
            return

        try:
            # SSD1322 doesn't have direct brightness control
            # This could be implemented with contrast settings if supported
            logger.info(f"Brightness control not implemented for SSD1322 (requested: {level})")
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")

    def _mock_display(self, message: str):
        """Mock display output when hardware is not available"""
        print(f"OLED Display: {message}")

    def get_display_info(self) -> dict:
        """Get display information"""
        return {
            "initialized": self.initialized,
            "width": self.width,
            "height": self.height,
            "available": SSD1322_AVAILABLE,
            "address": get_ssd1322_address()
        }
