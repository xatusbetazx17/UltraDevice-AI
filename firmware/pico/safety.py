"""Dependency-free firmware policy, also tested under CPython.

Only drives the reference board LED. Limits are example engineering settings.
"""
import math

MODES = ("normal", "conserve", "stealth", "boost", "reserve", "shutdown", "fault")


class SafetyController:
    def __init__(self):
        self.mode = "conserve"
        self.last_host_ms = None
        self.boost_end_ms = None
        self.cooldown_until_ms = 60000
        self.fault_latched = False
        self.hot = False

    def cancel_boost(self, now_ms):
        if self.boost_end_ms is not None:
            self.cooldown_until_ms = max(self.cooldown_until_ms, min(now_ms, self.boost_end_ms) + 60000)
            self.boost_end_ms = None

    def tick(self, now_ms, temp_c, sensor_ok, stop_pressed=False):
        good = (sensor_ok and isinstance(temp_c, (int, float)) and not isinstance(temp_c, bool)
                and math.isfinite(temp_c) and -40 <= temp_c <= 125)
        if not good:
            self.fault_latched = True
        if good and temp_c >= 42:
            self.hot = True
        elif good and temp_c < 39:
            self.hot = False
        if self.fault_latched:
            self.mode = "fault"
        elif stop_pressed or self.hot:
            self.mode = "shutdown"
        elif self.last_host_ms is not None and now_ms - self.last_host_ms > 3000:
            self.mode = "shutdown"
        elif good and temp_c >= 39:
            self.mode = "conserve"
        elif self.boost_end_ms is not None and now_ms >= self.boost_end_ms:
            self.mode = "conserve"
        if self.mode != "boost":
            self.cancel_boost(now_ms)
        return self.mode

    def command(self, mode, now_ms, temp_c, sensor_ok, stop_pressed=False):
        if mode not in MODES:
            raise ValueError("Unknown mode")
        self.last_host_ms = now_ms
        if mode == "boost":
            if self.boost_end_ms is None:
                if now_ms < self.cooldown_until_ms:
                    mode = "conserve"
                else:
                    self.boost_end_ms = now_ms + 10000
        else:
            self.cancel_boost(now_ms)
        self.mode = mode
        return self.tick(now_ms, temp_c, sensor_ok, stop_pressed)

    def reset(self, temp_c, sensor_ok):
        if sensor_ok and temp_c is not None and math.isfinite(temp_c) and -40 <= temp_c < 39:
            self.fault_latched = False
            return True
        return False
