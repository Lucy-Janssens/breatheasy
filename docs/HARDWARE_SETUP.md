## Breadboard Layout

Using a breadboard for clean, organized connections:

**Power Rails:**
- Top Red (+): 3.3V for OLED, DHT, BME680
- Bottom Red (+): 5V for PIR sensor only
- Blue (-): Common ground for all components

**I2C Bus:**
- Row 10: Shared SDA line (OLED + BME680)
- Row 12: Shared SCL line (OLED + BME680)

**GPIO Signals:**
- Row 15: PIR motion sensor signal (GPIO4)
- Row 20: DHT temperature sensor signal (GPIO17)

See complete breadboard diagram in this file.