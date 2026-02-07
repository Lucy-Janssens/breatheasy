"""
DisplayManager – controls the OLED display based on motion sensor activity.

Responsibilities:
  * Wake display when PIR detects motion
  * Auto-sleep after configurable timeout
  * Refresh display content with latest sensor data
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from ..config import settings
from ..hardware.oled_display import OLEDDisplay
from ..hardware.motion_sensor import MotionSensor

logger = logging.getLogger(__name__)


class DisplayManager:
    """Manages OLED display lifecycle driven by motion events."""

    def __init__(self, display: OLEDDisplay, motion_sensor: MotionSensor) -> None:
        self._display = display
        self._motion = motion_sensor
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._latest_data: Dict[str, Any] = {}

        # Wire up motion callback to wake the display
        self._motion.set_callback(self._on_motion)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the display update / sleep-check loop."""
        if self._running:
            return
        self._running = True
        self._display.wake()
        self._display.display_message("BreatheEasy")
        self._task = asyncio.create_task(self._loop())
        logger.info("DisplayManager started")

    async def stop(self) -> None:
        """Stop the loop and put the display to sleep."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._display.sleep()
        logger.info("DisplayManager stopped")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def update_sensor_data(self, data: Dict[str, Any]) -> None:
        """Receive new sensor data and refresh the display if it's on."""
        self._latest_data = data
        if self._display._is_on:
            self._display.display_sensor_data(data)

    async def show_message(self, msg: str, duration: float = 3.0) -> None:
        """Display a temporary message, then revert to sensor data."""
        self._display.display_message(msg)
        await asyncio.sleep(duration)
        if self._latest_data and self._display._is_on:
            self._display.display_sensor_data(self._latest_data)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_motion(self) -> None:
        """Callback invoked by the PIR sensor when motion is detected."""
        self._display.wake()
        # Refresh with latest data immediately
        if self._latest_data:
            self._display.display_sensor_data(self._latest_data)

    async def _loop(self) -> None:
        while self._running:
            try:
                if self._display._is_on and self._display.should_sleep():
                    self._display.sleep()
            except Exception as exc:
                logger.error(f"DisplayManager loop error: {exc}")
            await asyncio.sleep(1)
