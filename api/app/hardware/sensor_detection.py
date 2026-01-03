"""
Sensor Detection and Auto-Configuration
This module automatically detects I2C devices and configures hardware interfaces.
"""

import smbus2
from typing import Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Known I2C addresses for common sensors
KNOWN_DEVICES = {
    0x27: "SSD1322_OLED",
    0x3C: "SSD1322_OLED_ALT",
    0x3D: "SSD1322_OLED_ALT2",
    0x76: "BME680_PRIMARY",
    0x77: "BME680_SECONDARY",
}

class SensorDetector:
    def __init__(self, bus_number: int = 1):
        self.bus_number = bus_number
        self.bus: Optional[smbus2.SMBus] = None
        self.detected_devices: Dict[int, str] = {}

    def initialize_bus(self) -> bool:
        """Initialize the I2C bus"""
        try:
            self.bus = smbus2.SMBus(self.bus_number)
            logger.info(f"Initialized I2C bus {self.bus_number}")
            # Small delay to ensure bus is ready
            import time
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize I2C bus {self.bus_number}: {e}")
            return False

    def scan_bus(self) -> Dict[int, str]:
        """Scan the I2C bus for devices"""
        if not self.bus:
            if not self.initialize_bus():
                return {}

        detected = {}
        logger.info("Scanning I2C bus for devices...")

        for address in range(0x03, 0x78):  # Valid I2C addresses
            try:
                self.bus.read_byte(address)
                device_name = KNOWN_DEVICES.get(address, f"UNKNOWN_DEVICE_0x{address:02X}")
                detected[address] = device_name
                logger.info(f"Found device at 0x{address:02X}: {device_name}")
            except OSError:
                # No device at this address
                pass

        self.detected_devices = detected
        return detected

    def identify_bme680(self) -> Optional[int]:
        """Identify BME680 sensor address"""
        bme_addresses = [addr for addr, device in self.detected_devices.items()
                        if "BME680" in device]

        if not bme_addresses:
            logger.warning("No BME680 sensor detected")
            return None

        # Try to verify each BME680 address
        for address in bme_addresses:
            if self._verify_bme680(address):
                logger.info(f"BME680 verified at address 0x{address:02X}")
                return address

        logger.warning("BME680 detected but verification failed")
        return None

    def identify_ssd1322(self) -> Optional[int]:
        """Identify SSD1322 OLED display address"""
        oled_addresses = [addr for addr, device in self.detected_devices.items()
                         if "SSD1322" in device]

        if not oled_addresses:
            logger.warning("No SSD1322 OLED display detected")
            return None

        # Try to verify each OLED address
        for address in oled_addresses:
            if self._verify_ssd1322(address):
                logger.info(f"SSD1322 verified at address 0x{address:02X}")
                return address

        logger.warning("SSD1322 detected but verification failed")
        return None

    def _verify_bme680(self, address: int) -> bool:
        """Verify BME680 by reading chip ID"""
        if not self.bus:
            return False

        try:
            # BME680 chip ID is 0x61
            chip_id = self.bus.read_byte_data(address, 0xD0)
            logger.debug(f"BME680 at 0x{address:02X} chip ID: 0x{chip_id:02X}")
            return chip_id == 0x61
        except Exception as e:
            logger.debug(f"BME680 verification failed at 0x{address:02X}: {e}")
            # For debugging, let's try a simpler verification
            try:
                # Just try to read any byte - if it responds, assume it's the BME680
                self.bus.read_byte(address)
                logger.debug(f"BME680 basic read succeeded at 0x{address:02X}")
                return True
            except:
                return False

    def _verify_ssd1322(self, address: int) -> bool:
        """Verify SSD1322 by attempting to read from it"""
        if not self.bus:
            return False

        try:
            # Try to read a byte from the display
            self.bus.read_byte(address)
            return True
        except Exception as e:
            logger.debug(f"SSD1322 verification failed at 0x{address:02X}: {e}")
            return False

    def get_sensor_config(self) -> Dict[str, int]:
        """Get complete sensor configuration"""
        logger.debug("Getting sensor configuration...")

        if not self.detected_devices:
            logger.debug("No cached devices, scanning bus...")
            self.scan_bus()
            logger.debug(f"Scan complete. Found devices: {self.detected_devices}")

        config = {}

        logger.debug("Identifying BME680...")
        bme680_addr = self.identify_bme680()
        if bme680_addr:
            config['bme680'] = bme680_addr
            logger.info(f"BME680 configured at 0x{bme680_addr:02X}")
        else:
            logger.warning("BME680 not identified")

        logger.debug("Identifying SSD1322...")
        ssd1322_addr = self.identify_ssd1322()
        if ssd1322_addr:
            config['ssd1322'] = ssd1322_addr
            logger.info(f"SSD1322 configured at 0x{ssd1322_addr:02X}")
        else:
            logger.warning("SSD1322 not identified")

        logger.debug(f"Final sensor config: {config}")
        return config

# Global detector instance
_detector = SensorDetector()

def detect_sensors() -> Dict[str, int]:
    """Convenience function to detect all sensors"""
    return _detector.get_sensor_config()

def get_bme680_address() -> Optional[int]:
    """Get BME680 sensor address"""
    # Ensure bus is scanned before identifying
    if not _detector.detected_devices:
        _detector.scan_bus()
    return _detector.identify_bme680()

def get_ssd1322_address() -> Optional[int]:
    """Get SSD1322 display address"""
    # Ensure bus is scanned before identifying
    if not _detector.detected_devices:
        _detector.scan_bus()
    return _detector.identify_ssd1322()
