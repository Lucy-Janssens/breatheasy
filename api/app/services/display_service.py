from typing import Optional
from ..hardware import oled_display


class DisplayService:
    def __init__(self):
        self.display = oled_display.OLED_Display()

    async def display_reading(self, sensor_type: str, value: float, unit: str):
        """Display a sensor reading on the OLED screen"""
        try:
            self.display.display_reading(sensor_type, value, unit)
        except Exception as e:
            print(f"Error displaying reading: {e}")

    async def display_message(self, message: str, line: int = 0):
        """Display a custom message on the OLED screen"""
        try:
            self.display.display_message(message, line)
        except Exception as e:
            print(f"Error displaying message: {e}")

    async def clear_display(self):
        """Clear the OLED display"""
        try:
            self.display.clear()
        except Exception as e:
            print(f"Error clearing display: {e}")

    async def display_air_quality_status(self, pm25: Optional[float], co2: Optional[float]):
        """Display air quality status"""
        try:
            self.display.display_air_quality_status(pm25, co2)
        except Exception as e:
            print(f"Error displaying air quality status: {e}")
