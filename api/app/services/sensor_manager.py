"""
SensorManager – central coordinator for all hardware sensors.

Responsibilities:
  * Initialise BME680, DHT22, and PIR sensors
  * Run an async polling loop (default 30 s)
  * Persist readings to the database
  * Broadcast updates to registered WebSocket clients
  * Expose latest readings from memory
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import async_session
from ..hardware.bme680_sensor import BME680Sensor
from ..hardware.dht_sensor import DHTSensor
from ..hardware.motion_sensor import MotionSensor
from ..models import SensorReading
from ..integrations.mqtt_publisher import get_mqtt_publisher

logger = logging.getLogger(__name__)


class SensorManager:
    """Coordinates sensor polling, storage, and real-time distribution."""

    def __init__(self) -> None:
        # Hardware drivers
        self._bme680 = BME680Sensor(i2c_address=settings.bme680_address)
        self._dht22 = DHTSensor(pin=settings.dht_sensor_pin)
        self._pir = MotionSensor(pin=settings.motion_sensor_pin)

        # State
        self._latest: Dict[str, Any] = {}
        self._ws_clients: Set[WebSocket] = set()
        self._task: Optional[asyncio.Task] = None
        self._running = False

        # MQTT publisher (may be a no-op if broker unavailable)
        self._mqtt = get_mqtt_publisher()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the async polling loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            f"SensorManager started – polling every {settings.sensor_poll_interval}s"
        )

    async def stop(self) -> None:
        """Stop polling and clean up hardware resources."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._dht22.cleanup()
        self._pir.cleanup()
        logger.info("SensorManager stopped")

    # ------------------------------------------------------------------
    # Public read helpers
    # ------------------------------------------------------------------

    def get_latest_readings(self) -> Dict[str, Any]:
        """Return the most recent sensor data from memory."""
        return self._latest

    def health_check(self) -> Dict[str, bool]:
        """Return the health status of each sensor and the manager itself."""
        return {
            "bme680": self._bme680.health_check(),
            "dht22": self._dht22.health_check(),
            "motion": self._pir._initialized,
            "manager_running": self._running,
        }

    # ------------------------------------------------------------------
    # PIR accessor (needed by DisplayManager)
    # ------------------------------------------------------------------

    @property
    def pir(self) -> MotionSensor:
        return self._pir

    # ------------------------------------------------------------------
    # WebSocket management
    # ------------------------------------------------------------------

    def add_websocket_client(self, ws: WebSocket) -> None:
        self._ws_clients.add(ws)
        logger.debug(f"WS client added ({len(self._ws_clients)} total)")

    def remove_websocket_client(self, ws: WebSocket) -> None:
        self._ws_clients.discard(ws)
        logger.debug(f"WS client removed ({len(self._ws_clients)} total)")

    # ------------------------------------------------------------------
    # Internal polling
    # ------------------------------------------------------------------

    async def _poll_loop(self) -> None:
        # Small delay so the rest of startup finishes first
        await asyncio.sleep(3)

        while self._running:
            try:
                data = self._read_all_sensors()
                self._latest = data
                await self._persist(data)
                await self._broadcast(data)
                self._publish_mqtt(data)
            except Exception as exc:
                logger.error(f"Poll error: {exc}", exc_info=True)

            await asyncio.sleep(settings.sensor_poll_interval)

    def _read_all_sensors(self) -> Dict[str, Any]:
        """Collect data from every sensor; skip any that fail."""
        now = datetime.now(timezone.utc).isoformat()
        sensors: Dict[str, Any] = {}

        try:
            sensors["bme680"] = self._bme680.read()
        except Exception as exc:
            logger.warning(f"BME680 read failed: {exc}")

        try:
            sensors["dht22"] = self._dht22.read()
        except Exception as exc:
            logger.warning(f"DHT22 read failed: {exc}")

        try:
            sensors["motion"] = {
                "motion_detected": self._pir.is_motion_detected(),
                "time_since_motion": round(self._pir.time_since_last_motion(), 1),
            }
        except Exception as exc:
            logger.warning(f"PIR read failed: {exc}")

        return {"timestamp": now, "sensors": sensors}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    async def _persist(self, data: Dict[str, Any]) -> None:
        """Store individual metrics as rows in the sensor_readings table."""
        sensors = data.get("sensors", {})
        rows: List[SensorReading] = []

        bme = sensors.get("bme680", {})
        for metric, unit in [
            ("temperature", "celsius"),
            ("humidity", "percent"),
            ("pressure", "hPa"),
            ("air_quality_score", "score"),
        ]:
            val = bme.get(metric)
            if val is not None:
                rows.append(
                    SensorReading(
                        sensor_type="bme680", metric=metric, value=val, unit=unit
                    )
                )

        dht = sensors.get("dht22", {})
        for metric, unit in [("temperature", "celsius"), ("humidity", "percent")]:
            val = dht.get(metric)
            if val is not None:
                rows.append(
                    SensorReading(
                        sensor_type="dht22", metric=metric, value=val, unit=unit
                    )
                )

        motion = sensors.get("motion", {})
        if "motion_detected" in motion:
            rows.append(
                SensorReading(
                    sensor_type="motion",
                    metric="motion_detected",
                    value=1.0 if motion["motion_detected"] else 0.0,
                    unit="bool",
                )
            )

        if not rows:
            return

        try:
            async with async_session() as db:
                db.add_all(rows)
                await db.commit()
            logger.debug(f"Persisted {len(rows)} readings")
        except Exception as exc:
            logger.error(f"DB persist error: {exc}")

    # ------------------------------------------------------------------
    # WebSocket broadcast
    # ------------------------------------------------------------------

    async def _broadcast(self, data: Dict[str, Any]) -> None:
        if not self._ws_clients:
            return

        payload = json.dumps(data)
        stale: List[WebSocket] = []

        for ws in self._ws_clients:
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)

        for ws in stale:
            self._ws_clients.discard(ws)

    # ------------------------------------------------------------------
    # MQTT publish
    # ------------------------------------------------------------------

    def _publish_mqtt(self, data: Dict[str, Any]) -> None:
        sensors = data.get("sensors", {})
        bme = sensors.get("bme680", {})

        mapping = {
            "temperature": bme.get("temperature"),
            "humidity": bme.get("humidity"),
            "pm25": bme.get("air_quality_score"),  # map AQ score for HA
        }

        for key, val in mapping.items():
            if val is not None:
                try:
                    self._mqtt.publish_sensor_reading(key, val)
                except Exception:
                    pass
