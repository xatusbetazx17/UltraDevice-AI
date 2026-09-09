"""Raspberry Pi Pico (RP2040, non-W) MicroPython reference application.

USB request/response service; onboard LED is the ONLY controlled load.
Copy safety.py, sensors.py and service.py alongside this file. No network or cloud API.
"""
import json
import math
import select
import sys
import time

from machine import ADC, I2C, PWM, WDT, Pin
from safety import SafetyController
from sensors import TMP117
from service import DeviceService

USE_TMP117 = False  # Set True ONLY after wiring the external sensor in hardware/README.md.
MAX_FRAME = 4096


def run():
    led = PWM(Pin(25))
    led.freq(1000)
    led.duty_u16(0)
    stop = Pin(2, Pin.IN, Pin.PULL_UP)
    sensor = ADC(4)
    external = None
    initialization_failed = False
    if USE_TMP117:
        try:
            bus = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
            external = TMP117(bus)
            time.sleep_ms(1100)  # Allow the first default conversion to finish.
        except (OSError, ValueError):
            initialization_failed = True
    policy = SafetyController()
    service = DeviceService(policy, "tmp117" if USE_TMP117 else "die")
    watchdog = WDT(timeout=5000)
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)
    buffer = ""
    discard = False
    now_ms = 0
    last_tick = time.ticks_ms()
    temp = None
    sensor_ok = False
    next_sample_ms = 0
    try:
        while True:
            tick = time.ticks_ms()
            now_ms += time.ticks_diff(tick, last_tick)
            last_tick = tick
            if now_ms >= next_sample_ms:
                try:
                    if initialization_failed:
                        raise ValueError("Configured sensor unavailable")
                    if external:
                        temp = external.temperature_c()
                    else:
                        volts = sensor.read_u16() * 3.3 / 65535
                        temp = 27 - (volts - 0.706) / 0.001721
                    sensor_ok = math.isfinite(temp) and -40 <= temp <= 125
                except (OSError, ValueError):
                    sensor_ok = False
                    temp = None
                next_sample_ms = now_ms + 250
            mode = policy.tick(now_ms, temp, sensor_ok, not stop.value())
            duties = {"normal": 12000, "conserve": 3000, "stealth": 0,
                      "reserve": 1000, "boost": 24000, "shutdown": 0, "fault": 0}
            led.duty_u16(duties[mode])
            # Bounded input work keeps sensor checks and watchdog alive under malformed traffic.
            for _ in range(128):
                if not poller.poll(0):
                    break
                char = sys.stdin.read(1)
                if not char:
                    break
                if char != "\n":
                    if not discard:
                        buffer += char
                        if len(buffer) >= MAX_FRAME:
                            buffer = ""
                            discard = True
                    continue
                if discard:
                    discard = False
                    buffer = ""
                    continue
                try:
                    request = json.loads(buffer)
                    response = service.handle(request, now_ms, temp, sensor_ok, not stop.value())
                    led.duty_u16(duties[policy.mode])
                except (ValueError, TypeError) as error:
                    response = {"v": 1, "id": 0, "ok": False, "error": str(error)}
                buffer = ""
                print(json.dumps(response))
            watchdog.feed()
            time.sleep_ms(10)
    finally:
        led.duty_u16(0)
        led.deinit()


if __name__ == "__main__":
    # Hold the optional stop button during boot to retain REPL access without a watchdog.
    if Pin(2, Pin.IN, Pin.PULL_UP).value():
        run()
