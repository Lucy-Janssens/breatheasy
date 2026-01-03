#!/usr/bin/env python3
"""
Temperature Display Script
Displays current temperature on the SSD1322 OLED display
"""

import sys
import os
import time
import signal
import logging

# Add the API directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from app.hardware import temperature, oled_display, motion_sensor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    logger.info("Shutdown signal received")
    running = False

def display_temperature_loop():
    """Main loop to display temperature on OLED"""
    global running

    logger.info("Starting temperature display...")

    # Initialize sensors and display
    display = oled_display.OLED_Display()
    motion = motion_sensor.MotionSensor(pin=4)  # GPIO 4 (physical pin 7)

    if not temperature.initialize_sensor():
        logger.error("Failed to initialize temperature sensor")
        return 1

    if not display.initialized:
        logger.error("Failed to initialize OLED display")
        return 1

    logger.info("Sensors and display initialized successfully")
    logger.info("Press Ctrl+C to exit")

    # Clear display initially
    display.clear()
    display.display_message("Breatheasy Active", 0)
    time.sleep(2)

    last_temp = None
    last_humidity = None
    update_count = 0

    try:
        while running:
            # Check if we should display (motion sensor or always on)
            if motion.should_display_be_active():
                # Read temperature and humidity
                temp_hum = temperature.read_temperature_humidity()

                if temp_hum and temp_hum[0] is not None:
                    current_temp, current_humidity = temp_hum

                    # Only update display if values changed significantly
                    temp_changed = (last_temp is None or
                                  abs(current_temp - last_temp) >= 0.5)
                    hum_changed = (last_humidity is None or
                                 abs(current_humidity - last_humidity) >= 2.0)

                    if temp_changed or hum_changed or update_count % 30 == 0:  # Force update every 30 seconds
                        # Display temperature
                        display.display_reading("TEMPERATURE", current_temp, "C")

                        # Display humidity on second line after 2 seconds
                        time.sleep(2)
                        display.display_reading("HUMIDITY", current_humidity, "%")

                        # Update last values
                        last_temp = current_temp
                        last_humidity = current_humidity

                        logger.info(f"Updated display - Temp: {current_temp:.1f}°C, Humidity: {current_humidity:.1f}%")

                    update_count += 1
                else:
                    # Display error message
                    display.display_message("Sensor Error", 0)
                    display.display_message("Check Connections", 1)
                    logger.warning("Failed to read temperature sensor")
                    time.sleep(5)
            else:
                # Motion timeout - clear display to save power
                display.clear()
                logger.debug("Display cleared due to motion timeout")

            # Wait before next reading
            time.sleep(3)  # Update every 3 seconds

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Error in display loop: {e}")
        return 1
    finally:
        # Cleanup
        display.clear()
        logger.info("Temperature display stopped")

    return 0

def display_status():
    """Display current sensor status"""
    print("🔍 Checking sensor status...")

    # Check temperature sensor
    temp_status = temperature.get_sensor_details()
    print(f"Temperature Sensor: {'✅ Active' if temp_status.get('available') else '❌ Not Available'}")
    if temp_status.get('available'):
        temp = temp_status.get('temperature')
        if temp is not None:
            print(f"  Temperature: {temp:.1f}°C")
    # Check OLED display
    display = oled_display.OLED_Display()
    display_status = display.get_display_info()
    print(f"OLED Display: {'✅ Active' if display_status.get('initialized') else '❌ Not Available'}")
    if display_status.get('address'):
        print(f"  Address: 0x{display_status['address']:02X}")

    # Check motion sensor
    motion = motion_sensor.MotionSensor(pin=4)
    motion_status = motion.get_status()
    print(f"Motion Sensor: {'✅ Active' if motion_status.get('initialized') else '❌ Not Available'}")
    if motion_status.get('initialized'):
        print(f"  GPIO Pin: {motion_status['pin']}")
        print(f"  Current Motion: {motion_status['current_motion']}")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        display_status()
        return 0

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🌡️ Breatheasy Temperature Display")
    print("=================================")
    print("This script displays temperature and humidity on the OLED display.")
    print("Use --status to check sensor status")
    print("Press Ctrl+C to exit")
    print()

    return display_temperature_loop()

if __name__ == "__main__":
    sys.exit(main())
