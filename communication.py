#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
from pymodbus.client import ModbusSerialClient

# --- 1. GPIO Pin Definitions for DE and RE Control ---
# These now match your wiring: DE to GPIO 5, RE to GPIO 6.
DE_PIN = 5
RE_PIN = 6

def setup_gpio():
    """Sets up the GPIO pins."""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DE_PIN, GPIO.OUT)
    GPIO.setup(RE_PIN, GPIO.OUT)

def set_tx_mode():
    """Sets the MAX485 to transmit mode."""
    GPIO.output(DE_PIN, GPIO.HIGH)
    GPIO.output(RE_PIN, GPIO.HIGH)

def set_rx_mode():
    """Sets the MAX485 to receive mode (default)."""
    GPIO.output(DE_PIN, GPIO.LOW)
    GPIO.output(RE_PIN, GPIO.LOW)

# --- 2. Main Modbus Communication Logic ---
def main():
    """Connects to the inverter and reads data."""
    setup_gpio()
    set_rx_mode()  # Start in receive mode

    # This is the standard serial port for GPIO on a Raspberry Pi 4.
    # Ensure it's enabled in sudo raspi-config -> Interface Options -> Serial Port.
    port = "/dev/serial0" 

    # --- IMPORTANT: These settings MUST match your inverter's configuration ---
    client = ModbusSerialClient(
        method="rtu",
        port=port,
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    try:
        if not client.connect():
            print(f"❌ Connection Failed to Modbus device on {port}")
            return

        print("✅ Connected to inverter successfully!")
        
        # This command reads 2 registers, starting at address 1, from slave device 1.
        # Adjust (address, count, slave) as needed for the data you want.
        slave_id = 1
        register_address = 1
        register_count = 2

        # Switch to transmit, send command, then switch back to receive.
        set_tx_mode()
        time.sleep(0.05)  # Short delay for the driver to switch
        
        print(f"Reading {register_count} registers from address {register_address}...")
        result = client.read_holding_registers(register_address, register_count, slave=slave_id)
        
        time.sleep(0.05)  # Allow transmission to complete
        set_rx_mode()

        if result.isError():
            print(f"❌ Modbus Error: {result}")
        else:
            print(f"✅ Registers: {result.registers}")

    finally:
        print("Cleaning up GPIO and closing connection.")
        client.close()
        GPIO.cleanup()

if _name_ == "_main_":
    main()