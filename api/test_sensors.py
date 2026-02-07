#!/usr/bin/env python3
"""
Standalone hardware test script – run directly on the Raspberry Pi.

Usage:
    python3 test_sensors.py           # test all
    python3 test_sensors.py bme680    # test BME680 only
    python3 test_sensors.py dht22     # test DHT22 only
    python3 test_sensors.py pir       # test PIR only
    python3 test_sensors.py oled      # test OLED only
    python3 test_sensors.py i2c       # scan I2C bus
"""

import sys
import time


def test_i2c() -> bool:
    """Scan the I2C bus and print detected devices."""
    print("\n=== I2C Bus Scan ===")
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        found = []
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                found.append(addr)
            except OSError:
                pass
        if found:
            print(f"  Devices found: {', '.join(f'0x{a:02X}' for a in found)}")
            return True
        else:
            print("  No I2C devices found!")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_bme680() -> bool:
    """Test the BME680 sensor."""
    print("\n=== BME680 Sensor Test ===")
    try:
        from app.hardware.bme680_sensor import BME680Sensor
        sensor = BME680Sensor(i2c_address=0x76)
        data = sensor.read()
        print(f"  Temperature:  {data['temperature']:.1f} \u00b0C")
        print(f"  Humidity:     {data['humidity']:.1f} %")
        print(f"  Pressure:     {data['pressure']:.1f} hPa")
        print(f"  Air Quality:  {data['air_quality_score']:.1f} / 100")
        healthy = sensor.health_check()
        print(f"  Health check: {'PASS' if healthy else 'FAIL (mock mode)'}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_dht22() -> bool:
    """Test the DHT22 sensor."""
    print("\n=== DHT22 Sensor Test ===")
    try:
        from app.hardware.dht_sensor import DHTSensor
        sensor = DHTSensor(pin=17)
        data = sensor.read()
        print(f"  Temperature: {data['temperature']:.1f} \u00b0C")
        print(f"  Humidity:    {data['humidity']:.1f} %")
        healthy = sensor.health_check()
        print(f"  Health check: {'PASS' if healthy else 'FAIL (mock mode)'}")
        sensor.cleanup()
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_pir() -> bool:
    """Test the PIR motion sensor for 10 seconds."""
    print("\n=== PIR Motion Sensor Test ===")
    print("  Monitoring for motion for 10 seconds...")
    try:
        from app.hardware.motion_sensor import MotionSensor
        detected_count = 0

        def on_motion():
            nonlocal detected_count
            detected_count += 1
            print(f"  >> Motion detected! (count: {detected_count})")

        sensor = MotionSensor(pin=4, callback=on_motion)
        end = time.time() + 10
        while time.time() < end:
            state = sensor.is_motion_detected()
            sys.stdout.write(f"\r  Current state: {'MOTION' if state else 'clear '}  ")
            sys.stdout.flush()
            time.sleep(0.5)

        print(f"\n  Total detections: {detected_count}")
        sensor.cleanup()
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_oled() -> bool:
    """Test the OLED display."""
    print("\n=== OLED Display Test ===")
    try:
        from app.hardware.oled_display import OLEDDisplay
        display = OLEDDisplay(i2c_address=0x3C, timeout=60)
        print("  Displaying test message...")
        display.wake()
        display.display_message("BreatheEasy Test")
        time.sleep(2)

        print("  Displaying sensor data layout...")
        display.display_sensor_data({
            "sensors": {
                "bme680": {
                    "temperature": 22.5,
                    "humidity": 45.0,
                    "pressure": 1013.0,
                    "air_quality_score": 75.0,
                }
            }
        })
        time.sleep(3)
        display.sleep()
        print("  OLED test complete")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    tests = {
        "i2c": test_i2c,
        "bme680": test_bme680,
        "dht22": test_dht22,
        "pir": test_pir,
        "oled": test_oled,
    }

    requested = sys.argv[1:] if len(sys.argv) > 1 else list(tests.keys())
    results = {}

    print("BreatheEasy Hardware Test Runner")
    print("=" * 40)

    for name in requested:
        if name not in tests:
            print(f"\nUnknown test: {name}")
            continue
        results[name] = tests[name]()

    print("\n" + "=" * 40)
    print("Results:")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:10s} {status}")
    print()

    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
