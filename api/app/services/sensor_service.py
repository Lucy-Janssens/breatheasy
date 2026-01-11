from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Sensor, SensorReading
from ..schemas import SensorCreate, SensorUpdate, SensorReadingCreate
from ..hardware import air_quality, temperature
from ..integrations.mqtt_publisher import get_mqtt_publisher


class SensorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mqtt_publisher = get_mqtt_publisher()

    async def get_all_sensors(self) -> List[Sensor]:
        """Get all sensors"""
        result = await self.db.execute(select(Sensor))
        return result.scalars().all()

    async def get_sensor_by_id(self, sensor_id: str) -> Optional[Sensor]:
        """Get a sensor by ID"""
        result = await self.db.execute(select(Sensor).where(Sensor.id == sensor_id))
        return result.scalar_one_or_none()

    async def create_sensor(self, sensor_data: SensorCreate) -> Sensor:
        """Create a new sensor"""
        sensor = Sensor(**sensor_data.dict())
        self.db.add(sensor)
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def update_sensor(self, sensor_id: str, sensor_data: SensorUpdate) -> Optional[Sensor]:
        """Update a sensor"""
        sensor = await self.get_sensor_by_id(sensor_id)
        if not sensor:
            return None

        update_data = sensor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sensor, field, value)

        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def delete_sensor(self, sensor_id: str) -> bool:
        """Delete a sensor"""
        sensor = await self.get_sensor_by_id(sensor_id)
        if not sensor:
            return False

        await self.db.delete(sensor)
        await self.db.commit()
        return True

    async def record_reading(self, reading_data: SensorReadingCreate) -> SensorReading:
        """Record a new sensor reading"""
        reading = SensorReading(**reading_data.dict())
        self.db.add(reading)
        await self.db.commit()
        await self.db.refresh(reading)
        return reading

    async def poll_sensors(self) -> List[SensorReading]:
        """Poll all sensors and record readings"""
        readings = []

        try:
            # Poll temperature/humidity sensor
            temp, humidity = temperature.read_temperature_humidity()
            if temp is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="temp_sensor",
                    sensor_type="temperature",
                    value=temp,
                    unit="°C"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("temperature", temp)

            if humidity is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="humidity_sensor",
                    sensor_type="humidity",
                    value=humidity,
                    unit="%"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("humidity", humidity)

            # Poll air quality sensor
            pm25, pm10, co2, voc = air_quality.read_air_quality()
            if pm25 is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="air_quality_sensor",
                    sensor_type="pm25",
                    value=pm25,
                    unit="µg/m³"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("pm25", pm25)

            if pm10 is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="air_quality_sensor",
                    sensor_type="pm10",
                    value=pm10,
                    unit="µg/m³"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("pm10", pm10)

            if co2 is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="air_quality_sensor",
                    sensor_type="co2",
                    value=co2,
                    unit="ppm"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("co2", co2)

            if voc is not None:
                reading = await self.record_reading(SensorReadingCreate(
                    sensor_id="air_quality_sensor",
                    sensor_type="voc",
                    value=voc,
                    unit="ppb"
                ))
                readings.append(reading)
                # Publish to MQTT
                self.mqtt_publisher.publish_sensor_reading("voc", voc)

        except Exception as e:
            print(f"Error polling sensors: {e}")

        return readings
