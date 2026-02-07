#!/usr/bin/env python3
"""
Minimal OLED test to run INSIDE the Docker container.
Usage: docker exec breatheasy-api python test_oled_docker.py
"""
import time

ADDR = 0x3C
CMD = 0x00
DATA = 0x40

INIT_SEQ = [
    0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
    0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
    0x81, 0xFF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF,
]


def test_with_smbus():
    """Test using smbus2.write_byte_data (same as app uses)."""
    from smbus2 import SMBus, i2c_msg
    print("=== Testing with smbus2 ===")

    bus = SMBus(1)

    # Init
    for cmd in INIT_SEQ:
        bus.write_byte_data(ADDR, CMD, cmd)
        time.sleep(0.002)
    time.sleep(0.1)
    print("Init done")

    # Fill screen white using i2c_msg (same as app)
    # Set address window
    bus.write_byte_data(ADDR, CMD, 0x21)  # Col
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 127)
    bus.write_byte_data(ADDR, CMD, 0x22)  # Page
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 7)

    buf = [0xFF] * 1024
    for i in range(0, 1024, 16):
        chunk = buf[i:i+16]
        payload = [DATA] + chunk
        msg = i2c_msg.write(ADDR, payload)
        bus.i2c_rdwr(msg)

    print("All-white pattern sent via i2c_msg. Screen should be white now.")
    time.sleep(3)

    # Try alternative: write_i2c_block_data
    bus.write_byte_data(ADDR, CMD, 0x21)
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 127)
    bus.write_byte_data(ADDR, CMD, 0x22)
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 7)

    for i in range(0, 1024, 32):
        chunk = buf[i:i+32]
        bus.write_i2c_block_data(ADDR, DATA, chunk)

    print("All-white pattern sent via write_i2c_block_data. Screen should be white now.")
    time.sleep(3)

    # Clear
    bus.write_byte_data(ADDR, CMD, 0x21)
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 127)
    bus.write_byte_data(ADDR, CMD, 0x22)
    bus.write_byte_data(ADDR, CMD, 0)
    bus.write_byte_data(ADDR, CMD, 7)

    clear = [0x00] * 1024
    for i in range(0, 1024, 32):
        bus.write_i2c_block_data(ADDR, DATA, clear[i:i+32])
    print("Screen cleared.")
    bus.close()


def test_with_ioctl():
    """Test using raw ioctl (bypasses smbus entirely)."""
    import struct
    import fcntl

    print("\n=== Testing with raw ioctl ===")

    I2C_SLAVE = 0x0703
    fd = open("/dev/i2c-1", "rb+", buffering=0)
    fcntl.ioctl(fd, I2C_SLAVE, ADDR)

    # Init
    for cmd in INIT_SEQ:
        fd.write(bytes([CMD, cmd]))
        time.sleep(0.002)
    time.sleep(0.1)
    print("Init done (ioctl)")

    # Set address window
    for c in [0x21, 0, 127, 0x22, 0, 7]:
        fd.write(bytes([CMD, c]))

    # Fill white
    for i in range(0, 1024, 16):
        fd.write(bytes([DATA] + [0xFF] * 16))

    print("All-white pattern sent via raw ioctl. Screen should be white now.")
    time.sleep(3)

    # Clear
    for c in [0x21, 0, 127, 0x22, 0, 7]:
        fd.write(bytes([CMD, c]))
    for i in range(0, 1024, 16):
        fd.write(bytes([DATA] + [0x00] * 16))

    print("Screen cleared (ioctl).")
    fd.close()


if __name__ == "__main__":
    test_with_smbus()
    test_with_ioctl()
    print("\nDone. If you didn't see anything on the screen, the I2C bus")
    print("inside Docker cannot reach the physical display.")
