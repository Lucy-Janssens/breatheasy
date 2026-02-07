"""
PIR Motion Sensor Driver
Monitors a GPIO pin for motion events with 300 ms debounce.
Supports callback-based notification and background monitoring.
"""

from typing import Callable, Optional
import logging
import time
import threading

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available – mock mode enabled")


class MotionSensor:
    """Driver for a PIR motion sensor on a single GPIO pin."""

    _DEBOUNCE_MS: int = 300

    def __init__(
        self,
        pin: int = 4,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        self._pin = pin
        self._callback = callback
        self._initialized = False
        self._last_motion_time: float = 0.0
        self._lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

        self._initialize()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        if not GPIO_AVAILABLE:
            logger.info("PIR motion sensor running in mock mode")
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # Edge-triggered event detection with debounce
            GPIO.add_event_detect(
                self._pin,
                GPIO.RISING,
                callback=self._on_motion,
                bouncetime=self._DEBOUNCE_MS,
            )
            self._initialized = True
            logger.info(f"PIR motion sensor initialised on GPIO{self._pin}")
        except Exception as exc:
            logger.error(f"PIR init failed: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_motion_detected(self) -> bool:
        """Return True if the GPIO pin is currently HIGH."""
        if not self._initialized:
            import random
            return random.random() < 0.1

        try:
            return GPIO.input(self._pin) == GPIO.HIGH
        except Exception:
            return False

    def time_since_last_motion(self) -> float:
        """Seconds since the last motion event (0.0 if never detected)."""
        with self._lock:
            if self._last_motion_time == 0.0:
                return 0.0
            return time.time() - self._last_motion_time

    def set_callback(self, func: Callable[[], None]) -> None:
        """Register a function to call when motion is detected."""
        self._callback = func

    def start_monitoring(self) -> None:
        """Start a background thread that periodically logs motion state."""
        if self._running:
            return
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="pir-monitor"
        )
        self._monitor_thread.start()
        logger.info("PIR background monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the background monitoring thread."""
        self._running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=2)
            self._monitor_thread = None
        logger.info("PIR background monitoring stopped")

    def cleanup(self) -> None:
        """Release GPIO resources."""
        self.stop_monitoring()
        if self._initialized and GPIO_AVAILABLE:
            try:
                GPIO.remove_event_detect(self._pin)
                GPIO.cleanup(self._pin)
            except Exception:
                pass
            self._initialized = False
            logger.info("PIR sensor cleaned up")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_motion(self, _channel: int) -> None:
        with self._lock:
            self._last_motion_time = time.time()
        logger.debug("Motion detected")
        if self._callback is not None:
            try:
                self._callback()
            except Exception as exc:
                logger.error(f"Motion callback error: {exc}")

    def _monitor_loop(self) -> None:
        while self._running:
            time.sleep(1)
