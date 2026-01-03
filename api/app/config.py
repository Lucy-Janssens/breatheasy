from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./breatheasy.db"

    # Sensor Configuration
    temperature_sensor_pin: int = 4
    air_quality_sensor_pin: int = 17
    motion_sensor_pin: int = 27
    oled_reset_pin: int = 24

    # Polling intervals (seconds)
    sensor_poll_interval: int = 30
    display_timeout: int = 60

    # Tailscale (optional)
    tailscale_hostname: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
