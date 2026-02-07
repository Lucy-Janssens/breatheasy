"""
Unit tests for hardware drivers (run in mock mode without actual hardware).
"""

import pytest


class TestBME680Sensor:
    def test_mock_read_returns_all_keys(self):
        from app.hardware.bme680_sensor import BME680Sensor
        sensor = BME680Sensor(i2c_address=0x76)
        data = sensor.read()
        assert "temperature" in data
        assert "humidity" in data
        assert "pressure" in data
        assert "air_quality_score" in data

    def test_mock_read_values_in_range(self):
        from app.hardware.bme680_sensor import BME680Sensor
        sensor = BME680Sensor()
        data = sensor.read()
        assert 10 <= data["temperature"] <= 40
        assert 0 <= data["humidity"] <= 100
        assert 900 <= data["pressure"] <= 1100
        assert 0 <= data["air_quality_score"] <= 100

    def test_health_check_false_without_hardware(self):
        from app.hardware.bme680_sensor import BME680Sensor
        sensor = BME680Sensor()
        assert sensor.health_check() is False


class TestDHTSensor:
    def test_mock_read_returns_temp_and_humidity(self):
        from app.hardware.dht_sensor import DHTSensor
        sensor = DHTSensor(pin=17)
        data = sensor.read()
        assert "temperature" in data
        assert "humidity" in data

    def test_health_check_false_without_hardware(self):
        from app.hardware.dht_sensor import DHTSensor
        sensor = DHTSensor(pin=17)
        assert sensor.health_check() is False

    def test_cleanup_no_error(self):
        from app.hardware.dht_sensor import DHTSensor
        sensor = DHTSensor(pin=17)
        sensor.cleanup()  # should not raise


class TestMotionSensor:
    def test_is_motion_detected_returns_bool(self):
        from app.hardware.motion_sensor import MotionSensor
        sensor = MotionSensor(pin=4)
        result = sensor.is_motion_detected()
        assert isinstance(result, bool)

    def test_time_since_last_motion(self):
        from app.hardware.motion_sensor import MotionSensor
        sensor = MotionSensor(pin=4)
        t = sensor.time_since_last_motion()
        assert isinstance(t, float)
        assert t >= 0.0

    def test_cleanup_no_error(self):
        from app.hardware.motion_sensor import MotionSensor
        sensor = MotionSensor(pin=4)
        sensor.cleanup()


class TestOLEDDisplay:
    def test_mock_display_message_no_error(self):
        from app.hardware.oled_display import OLEDDisplay
        display = OLEDDisplay(i2c_address=0x3C, timeout=60)
        display.display_message("Hello")  # should not raise

    def test_mock_display_sensor_data_no_error(self):
        from app.hardware.oled_display import OLEDDisplay
        display = OLEDDisplay()
        display.display_sensor_data({
            "sensors": {
                "bme680": {
                    "temperature": 22.0,
                    "humidity": 50.0,
                    "pressure": 1013.0,
                    "air_quality_score": 80.0,
                }
            }
        })

    def test_should_sleep_respects_timeout(self):
        from app.hardware.oled_display import OLEDDisplay
        display = OLEDDisplay(timeout=0)  # immediate timeout
        assert display.should_sleep() is True

    def test_wake_and_sleep(self):
        from app.hardware.oled_display import OLEDDisplay
        display = OLEDDisplay(timeout=60)
        display.wake()
        assert display._is_on is True
        display.sleep()
        assert display._is_on is False
