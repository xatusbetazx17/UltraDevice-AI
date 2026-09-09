"""Configurable sensor POWER BUDGET, not a physical sensor driver.

Measured readings come from protocol.SerialDevice and firmware/pico/sensors.py.
"""
from .validation import number


class Sensors:
    def __init__(self, active_w=1.0, stealth_w=0.5):
        self.active_w = number("active_w", active_w)
        self.stealth_w = number("stealth_w", stealth_w)
        self.stealth = False

    def set_stealth(self, on):
        if not isinstance(on, bool):
            raise ValueError("on must be bool")
        self.stealth = on

    def power_draw_w(self):
        return self.stealth_w if self.stealth else self.active_w
