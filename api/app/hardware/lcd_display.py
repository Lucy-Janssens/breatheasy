"""
LCD Display Interface
This module provides functions to control a 20x4 I2C LCD display.
"""

from typing import Optional
import time
import logging

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
    logger.info("RPLCD library available for LCD display")
except ImportError as e:
    LCD_AVAILABLE = False
    logger.warning(f"RPLCD library not available: {e}. Using mock display.")


class LCD_Display:
    """
    Interface for 20x4 I2C LCD display
    """
    def __init__(self, i2c_address: int = 0x27, i2c_port: int = 1):
        self.i2c_address = i2c_address
        self.i2c_port = i2c_port
        self.display = None
        
        # Display properties
        self.cols = 20
        self.rows = 4
        
        self.initialized = self._initialize()
    
    def _initialize(self) -> bool:
        """Initialize the LCD display"""
        if not LCD_AVAILABLE:
            logger.warning("RPLCD library not available - using mock display")
            return False
        
        try:
            # Initialize LCD with I2C address
            logger.info(f"Trying to initialize LCD at address 0x{self.i2c_address:02X}")
            
            self.display = CharLCD(
                i2c_expander='PCF8574',
                address=self.i2c_address,
                port=self.i2c_port,
                cols=self.cols,
                rows=self.rows,
                dotsize=8,
                charmap='A00',
                auto_linebreaks=True
            )
            
            # Test the display
            self.display.clear()
            self.display.write_string("BreatheEasy")
            logger.info(f"Successfully initialized LCD at address 0x{self.i2c_address:02X}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing LCD display at 0x{self.i2c_address:02X}: {e}")
            logger.info("Using mock display mode")
            return False
    
    def clear(self):
        """Clear the display"""
        if self.initialized and self.display:
            try:
                self.display.clear()
            except Exception as e:
                logger.error(f"Error clearing LCD: {e}")
        else:
            logger.debug("Mock LCD: clear()")
    
    def write_line(self, line: int, text: str, center: bool = False):
        """
        Write text to a specific line
        
        Args:
            line: Line number (0-3)
            text: Text to display (will be truncated to 20 chars)
            center: Center the text on the line
        """
        if line < 0 or line >= self.rows:
            logger.warning(f"Invalid line number: {line}")
            return
        
        # Truncate or pad text
        text = str(text)[:self.cols]
        
        if center:
            text = text.center(self.cols)
        else:
            text = text.ljust(self.cols)  # Pad with spaces to clear previous text
        
        if self.initialized and self.display:
            try:
                self.display.cursor_pos = (line, 0)
                self.display.write_string(text)
            except Exception as e:
                logger.error(f"Error writing to LCD line {line}: {e}")
        else:
            logger.debug(f"Mock LCD Line {line}: {text}")
    
    def display_sensor_data(
        self,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        pm25: Optional[float] = None,
        co2: Optional[float] = None
    ):
        """
        Display sensor data on LCD
        
        Layout:
        Line 0: "  BreatheEasy       "
        Line 1: "Temp: 22.5°C        "
        Line 2: "Hum: 45%  PM:12     "
        Line 3: "CO2: 450 ppm        "
        """
        if not self.initialized:
            logger.debug(f"Mock LCD Display: T={temperature}°C, H={humidity}%, PM2.5={pm25}, CO2={co2}")
            return
        
        try:
            # Line 0: Title
            self.write_line(0, "  BreatheEasy", center=False)
            
            # Line 1: Temperature
            if temperature is not None:
                temp_text = f"Temp: {temperature:.1f}\xdfC"  # \xdf is degree symbol
            else:
                temp_text = "Temp: --.-\xdfC"
            self.write_line(1, temp_text)
            
            # Line 2: Humidity and PM2.5
            if humidity is not None and pm25 is not None:
                line2_text = f"Hum:{humidity:.0f}% PM:{pm25:.0f}"
            elif humidity is not None:
                line2_text = f"Hum: {humidity:.0f}%"
            elif pm25 is not None:
                line2_text = f"PM2.5: {pm25:.0f}"
            else:
                line2_text = "Hum: --% PM: --"
            self.write_line(2, line2_text)
            
            # Line 3: CO2
            if co2 is not None:
                co2_text = f"CO2: {co2:.0f} ppm"
            else:
                co2_text = "CO2: --- ppm"
            self.write_line(3, co2_text)
            
            logger.debug(f"Updated LCD: T={temperature}, H={humidity}, PM={pm25}, CO2={co2}")
            
        except Exception as e:
            logger.error(f"Error displaying sensor data: {e}")
    
    def display_message(self, message: str, line: int = 1, center: bool = True):
        """
        Display a simple message on the LCD
        
        Args:
            message: Message to display
            line: Line number (0-3)
            center: Center the text
        """
        self.write_line(line, message, center=center)
    
    def close(self):
        """Clean up and close the display"""
        if self.initialized and self.display:
            try:
                self.display.clear()
                self.display.close()
                logger.info("LCD display closed")
            except Exception as e:
                logger.error(f"Error closing LCD: {e}")


# Global display instance
_lcd_display: Optional[LCD_Display] = None


def get_lcd_display() -> LCD_Display:
    """Get or create the global LCD display instance"""
    global _lcd_display
    if _lcd_display is None:
        _lcd_display = LCD_Display()
    return _lcd_display


def update_display(
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    pm25: Optional[float] = None,
    co2: Optional[float] = None
):
    """
    Update the LCD display with sensor data
    """
    lcd = get_lcd_display()
    lcd.display_sensor_data(temperature, humidity, pm25, co2)


def display_message(message: str, line: int = 1):
    """Display a message on the LCD"""
    lcd = get_lcd_display()
    lcd.display_message(message, line=line)

