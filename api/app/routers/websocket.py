"""
WebSocket endpoint for real-time sensor updates.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

logger = logging.getLogger(__name__)

# Set from main.py at startup
_sensor_manager = None


def set_sensor_manager(manager) -> None:
    global _sensor_manager
    _sensor_manager = manager


@router.websocket("/ws/sensors")
async def sensor_websocket(ws: WebSocket):
    """
    Real-time sensor feed.

    On connect:
      1. Accept the connection
      2. Register with SensorManager
      3. Send latest readings immediately
      4. Keep alive until client disconnects
    """
    await ws.accept()

    if _sensor_manager is None:
        await ws.send_text(json.dumps({"error": "SensorManager not ready"}))
        await ws.close()
        return

    _sensor_manager.add_websocket_client(ws)
    logger.info("WebSocket client connected")

    # Push current state right away (with error handling)
    try:
        latest = _sensor_manager.get_latest_readings()
        if latest:
            await ws.send_text(json.dumps(latest))
    except Exception as exc:
        logger.warning(f"Failed to send initial data: {exc}")

    try:
        # Keep the connection open — the SensorManager broadcasts on poll
        while True:
            # Wait for any incoming message (e.g. ping / keep-alive)
            try:
                await ws.receive_text()
            except Exception:
                break
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as exc:
        logger.warning(f"WebSocket error: {exc}")
    finally:
        _sensor_manager.remove_websocket_client(ws)
