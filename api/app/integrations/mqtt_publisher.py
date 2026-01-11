"""
MQTT Publisher for Home Assistant Integration
This module handles MQTT publishing with Home Assistant MQTT Discovery protocol.
"""

import json
import logging
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTPublisher:
    """
    MQTT Publisher with Home Assistant Discovery support
    """
    
    # Device information for Home Assistant
    DEVICE_INFO = {
        "identifiers": ["breatheasy_001"],
        "name": "BreatheEasy Monitor",
        "model": "BME680 + LCD20x4",
        "manufacturer": "Custom",
        "sw_version": "1.0.0"
    }
    
    # Sensor configurations with Home Assistant device classes
    SENSOR_CONFIGS = {
        "temperature": {
            "name": "BreatheEasy Temperature",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "state_class": "measurement",
            "icon": "mdi:thermometer"
        },
        "humidity": {
            "name": "BreatheEasy Humidity",
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "state_class": "measurement",
            "icon": "mdi:water-percent"
        },
        "pm25": {
            "name": "BreatheEasy PM2.5",
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
            "state_class": "measurement",
            "icon": "mdi:air-filter"
        },
        "pm10": {
            "name": "BreatheEasy PM10",
            "device_class": "pm10",
            "unit_of_measurement": "µg/m³",
            "state_class": "measurement",
            "icon": "mdi:air-filter"
        },
        "co2": {
            "name": "BreatheEasy CO2",
            "device_class": "carbon_dioxide",
            "unit_of_measurement": "ppm",
            "state_class": "measurement",
            "icon": "mdi:molecule-co2"
        },
        "voc": {
            "name": "BreatheEasy VOC",
            "device_class": "volatile_organic_compounds",
            "unit_of_measurement": "ppb",
            "state_class": "measurement",
            "icon": "mdi:chemical-weapon"
        }
    }
    
    def __init__(
        self,
        broker_host: str = "mqtt",
        broker_port: int = 1883,
        client_id: str = "breatheasy-api"
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.discovery_sent = set()  # Track which sensors have been discovered
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            
            # Start network loop in background
            self.client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info("Successfully connected to MQTT broker")
            # Send discovery messages for all sensors
            self._send_all_discovery_messages()
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnect from MQTT broker: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback when message is published"""
        logger.debug(f"Message published: {mid}")
    
    def _send_all_discovery_messages(self):
        """Send discovery messages for all configured sensors"""
        for sensor_type in self.SENSOR_CONFIGS.keys():
            self._send_discovery_message(sensor_type)
    
    def _send_discovery_message(self, sensor_type: str):
        """
        Send Home Assistant MQTT Discovery message for a sensor
        
        Args:
            sensor_type: Type of sensor (temperature, humidity, pm25, etc.)
        """
        if sensor_type not in self.SENSOR_CONFIGS:
            logger.warning(f"Unknown sensor type: {sensor_type}")
            return
        
        if sensor_type in self.discovery_sent:
            logger.debug(f"Discovery already sent for {sensor_type}")
            return
        
        config = self.SENSOR_CONFIGS[sensor_type]
        unique_id = f"breatheasy_{sensor_type}"
        
        # Home Assistant MQTT Discovery topic
        discovery_topic = f"homeassistant/sensor/{unique_id}/config"
        
        # State topic where sensor values will be published
        state_topic = f"breatheasy/sensor/{sensor_type}"
        
        # Discovery payload
        payload = {
            "name": config["name"],
            "unique_id": unique_id,
            "state_topic": state_topic,
            "unit_of_measurement": config["unit_of_measurement"],
            "device_class": config.get("device_class"),
            "state_class": config.get("state_class"),
            "icon": config.get("icon"),
            "device": self.DEVICE_INFO,
            "availability_topic": "breatheasy/status",
            "payload_available": "online",
            "payload_not_available": "offline"
        }
        
        try:
            result = self.client.publish(
                discovery_topic,
                json.dumps(payload),
                qos=1,
                retain=True
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.discovery_sent.add(sensor_type)
                logger.info(f"Sent discovery message for {sensor_type}")
            else:
                logger.error(f"Failed to send discovery message for {sensor_type}")
                
        except Exception as e:
            logger.error(f"Error sending discovery message for {sensor_type}: {e}")
    
    def publish_sensor_reading(
        self,
        sensor_type: str,
        value: float
    ) -> bool:
        """
        Publish a sensor reading to MQTT
        
        Args:
            sensor_type: Type of sensor (temperature, humidity, pm25, etc.)
            value: Sensor value
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        if sensor_type not in self.SENSOR_CONFIGS:
            logger.warning(f"Unknown sensor type: {sensor_type}")
            return False
        
        # Ensure discovery message has been sent
        if sensor_type not in self.discovery_sent:
            self._send_discovery_message(sensor_type)
        
        # State topic
        state_topic = f"breatheasy/sensor/{sensor_type}"
        
        # Round value to 2 decimal places
        value_rounded = round(value, 2)
        
        try:
            result = self.client.publish(
                state_topic,
                str(value_rounded),
                qos=0,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published {sensor_type}: {value_rounded}")
                return True
            else:
                logger.error(f"Failed to publish {sensor_type}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing {sensor_type}: {e}")
            return False
    
    def publish_availability(self, status: str = "online"):
        """
        Publish availability status
        
        Args:
            status: 'online' or 'offline'
        """
        if self.client:
            try:
                self.client.publish(
                    "breatheasy/status",
                    status,
                    qos=1,
                    retain=True
                )
                logger.info(f"Published availability: {status}")
            except Exception as e:
                logger.error(f"Error publishing availability: {e}")


# Global MQTT publisher instance
_mqtt_publisher: Optional[MQTTPublisher] = None


def get_mqtt_publisher(
    broker_host: str = "mqtt",
    broker_port: int = 1883,
    client_id: str = "breatheasy-api"
) -> MQTTPublisher:
    """Get or create the global MQTT publisher instance"""
    global _mqtt_publisher
    if _mqtt_publisher is None:
        _mqtt_publisher = MQTTPublisher(
            broker_host=broker_host,
            broker_port=broker_port,
            client_id=client_id
        )
    return _mqtt_publisher


def initialize_mqtt(
    broker_host: str = "mqtt",
    broker_port: int = 1883
) -> bool:
    """Initialize MQTT connection"""
    publisher = get_mqtt_publisher(broker_host, broker_port)
    success = publisher.connect()
    if success:
        publisher.publish_availability("online")
    return success


def shutdown_mqtt():
    """Shutdown MQTT connection"""
    global _mqtt_publisher
    if _mqtt_publisher:
        _mqtt_publisher.publish_availability("offline")
        _mqtt_publisher.disconnect()
        _mqtt_publisher = None

