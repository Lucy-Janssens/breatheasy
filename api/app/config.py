"""
Application configuration loaded from environment variables via Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./data/breatheasy.db"

    # GPIO Pins
    motion_sensor_pin: int = 4
    dht_sensor_pin: int = 17

    # I2C addresses
    bme680_address: int = 0x76
    oled_address: int = 0x3C

    # Intervals (seconds)
    sensor_poll_interval: int = 30
    display_timeout: int = 60

    # MQTT
    mqtt_broker_host: str = "mqtt"
    mqtt_broker_port: int = 1883

    # Tailscale (optional)
    tailscale_hostname: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
