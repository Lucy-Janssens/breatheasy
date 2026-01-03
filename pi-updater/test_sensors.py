#!/usr/bin/env python3
"""
Sensor Test Script
Test the sensor detection and basic functionality on Raspberry Pi
"""

import sys
import os

# Add the API directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from app.hardware.sensor_detection import detect_sensors, SensorDetector
from app.hardware import air_quality, temperature, oled_display, motion_sensor

def test_sensor_detection():
    """Test sensor detection"""
    print("🔍 Testing sensor detection...")

    detector = SensorDetector()
    devices = detector.scan_bus()

    if not devices:
        print("❌ No I2C devices detected")
        return False

    print(f"✅ Found {len(devices)} I2C device(s):")
    for addr, device_type in devices.items():
        print(f"   0x{addr:02X}: {device_type}")

    config = detect_sensors()
    if config:
        print("✅ Sensor configuration:")
        for sensor, addr in config.items():
            print(f"   {sensor}: 0x{addr:02X}")
    else:
        print("❌ No known sensors detected")

    return bool(config)

def test_bme680():
    """Test BME680 sensor"""
    print("\n🌡️ Testing BME680 sensor...")

    if not air_quality.initialize_sensor():
        print("❌ BME680 initialization failed")
        return False

    # Test reading air quality data
    readings = air_quality.read_air_quality()
    if readings and all(r is not None for r in readings):
        pm25, pm10, co2, voc = readings
        print("✅ BME680 air quality readings:"        print(".1f"        print(".1f"        print(".1f"        print(".1f"        return True
    else:
        print("❌ Failed to read from BME680")
        return False

def test_temperature():
    """Test temperature and humidity"""
    print("\n🌡️ Testing temperature/humidity sensor...")

    if not temperature.initialize_sensor():
        print("❌ Temperature sensor initialization failed")
        return False

    # Test reading temperature and humidity
    temp_hum = temperature.read_temperature_humidity()
    if temp_hum and all(r is not None for r in temp_hum):
        temp, hum = temp_hum
        print("✅ Temperature/Humidity readings:"        print(".1f"        print(".1f"        return True
    else:
        print("❌ Failed to read temperature/humidity")
        return False

def test_oled_display():
    """Test OLED display"""
    print("\n📺 Testing OLED display...")

    display = oled_display.OLED_Display()
    if not display.initialized:
        print("❌ OLED display initialization failed")
        return False

    print("✅ OLED display initialized")

    # Test basic display functions
    try:
        display.clear()
        print("✅ Display clear function works")

        display.display_message("Sensor Test Active", 0)
        print("✅ Display message function works")

        return True
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        return False

def test_motion_sensor():
    """Test motion sensor"""
    print("\n🚶 Testing motion sensor...")

    motion = motion_sensor.MotionSensor(pin=4)  # GPIO 4 (physical pin 7)
    if not motion.initialized:
        print("❌ Motion sensor initialization failed")
        return False

    print("✅ Motion sensor initialized")

    # Test motion detection
    try:
        # Test reading
        motion_detected = motion.detect_motion()
        print(f"✅ Motion detection works - Current state: {motion_detected}")

        # Get status
        status = motion.get_status()
        print(f"✅ Status query works - GPIO pin: {status['pin']}")

        return True
    except Exception as e:
        print(f"❌ Motion sensor test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Breatheasy Sensor Test")
    print("=" * 40)

    tests = [
        ("Sensor Detection", test_sensor_detection),
        ("BME680 Sensor", test_bme680),
        ("Temperature/Humidity", test_temperature),
        ("OLED Display", test_oled_display),
        ("Motion Sensor", test_motion_sensor),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Your sensors are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
