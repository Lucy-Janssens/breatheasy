"""
Legacy DisplayService – kept for backward compatibility.
The new DisplayManager in display_manager.py is the primary service.
"""

from ..hardware.oled_display import OLEDDisplay


class DisplayService:
    def __init__(self):
        self.display = OLEDDisplay()

    async def display_message(self, message: str):
        self.display.display_message(message)

    async def clear_display(self):
        self.display.sleep()
