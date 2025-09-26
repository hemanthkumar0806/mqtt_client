#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
import RPi.GPIO as GPIO
import time

DE_RE_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(DE_RE_PIN, GPIO.OUT)
GPIO.output(DE_RE_PIN, 0)  # Receive mode

def set_tx():
    GPIO.output(DE_RE_PIN, 1)

def set_rx():
    GPIO.output(DE_RE_PIN, 0)

client = ModbusSerialClient(
    method="rtu",
    port="/dev/serial0",
    baudrate=9600,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1
)

if client.connect():
    print("✅ Connected to inverter")
    set_tx()
    time.sleep(0.05)  # Give time for DE/RE switching
    result = client.read_holding_registers(0, 2, unit=1)  # Test register address
    time.sleep(0.05)
    set_rx()

    if result.isError():
        print("❌ Modbus error:", result)
    else:
        print("📟 Registers:", result.registers)

    client.close()
else:
    print("❌ Connection failed")

GPIO.cleanup()