"""Host policy. Firmware independently limits its LED demo outputs."""
from dataclasses import asdict, dataclass
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from .config import StrictModel
from .validation import number

Mode = Literal["normal", "conserve", "stealth", "boost", "reserve", "shutdown", "fault"]
MODES = ("normal", "conserve", "stealth", "boost", "reserve", "shutdown", "fault")


class Reading(StrictModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)
    seq: int = Field(ge=0)
    uptime_ms: int = Field(ge=0)
    temp_c: float | None = Field(default=None, ge=-40, le=125)
    temp_source: Literal["die", "tmp117", "simulated"]
    battery_soc: float | None = Field(default=None, ge=0, le=1)
    load_w: float | None = Field(default=None, ge=0)
    harvest_w: float | None = Field(default=None, ge=0)
    device_mode: Mode
    sensor_ok: bool


class ControllerConfig(StrictModel):
    reserve_soc: float = Field(0.2, ge=0, lt=1)
    recover_soc: float = Field(0.25, gt=0, le=1)
    shutdown_soc: float = Field(0.05, ge=0, lt=1)
    derate_c: float = Field(39.0, gt=-40, lt=85)
    shutdown_c: float = Field(42.0, gt=-40, le=85)
    boost_max_s: float = Field(10, gt=0, le=10)
    cooldown_s: float = Field(60, ge=60)
    stale_after_s: float = Field(3, gt=0, le=3)

    @model_validator(mode="after")
    def thresholds(self):
        if not self.shutdown_soc < self.reserve_soc < self.recover_soc:
            raise ValueError("Require shutdown_soc < reserve_soc < recover_soc")
        if self.derate_c >= self.shutdown_c:
            raise ValueError("derate_c must be below shutdown_c")
        return self


@dataclass(frozen=True)
class Decision:
    mode: str
    reason: str
    sample_period_s: float
    radio_duty: float
    ui_duty: float
    boost_remaining_s: float

    def to_dict(self):
        return asdict(self)


class DeviceController:
    def __init__(self, config=None):
        self.config = config or ControllerConfig()
        self.mode = "conserve"
        self.last_seq = -1
        self.last_uptime_ms = -1
        self.last_time = None
        self.boost_until = None
        # A new host cannot erase a board's previous cooldown: wait one cooldown on startup.
        self.next_boost = None
        self.fault_latched = False
        self.hot_latched = False
        self.reserve_latched = False

    def _decision(self, mode, reason, now):
        self.mode = mode
        duties = {"normal": (1, 1, 1), "boost": (0.25, 1, 1), "conserve": (2, 0.25, 0.4),
                  "stealth": (2, 0, 0), "reserve": (2, 0, 0.1),
                  "shutdown": (1, 0, 0), "fault": (1, 0, 0)}
        period, radio, ui = duties[mode]
        return Decision(mode, reason, period, radio, ui, max(0, (self.boost_until or now) - now))

    def _cancel_boost(self, now):
        if self.boost_until is not None:
            self.next_boost = max(self.next_boost or 0, min(now, self.boost_until) + self.config.cooldown_s)
            self.boost_until = None

    def step(self, reading, now_s, requested="normal", *, received_s=None, reset_fault=False):
        number("now_s", now_s)
        if requested not in MODES:
            raise ValueError("Unknown mode")
        cfg = self.config
        if self.next_boost is None:
            self.next_boost = now_s + cfg.cooldown_s
        age = now_s - (now_s if received_s is None else received_s)
        invalid_time = self.last_time is not None and (now_s < self.last_time or now_s - self.last_time > cfg.stale_after_s)
        valid = (isinstance(reading, Reading) and reading.sensor_ok and reading.temp_c is not None
                 and reading.seq > self.last_seq and reading.uptime_ms > self.last_uptime_ms
                 and 0 <= age <= cfg.stale_after_s and not invalid_time)
        if not valid:
            self.fault_latched = True
            self._cancel_boost(now_s)
            self.last_time = now_s
            return self._decision("fault", "Invalid, stale, missing or replayed sensor sample", now_s)
        self.last_seq, self.last_uptime_ms, self.last_time = reading.seq, reading.uptime_ms, now_s
        if reset_fault and reading.temp_c < cfg.derate_c:
            self.fault_latched = False
        if self.fault_latched:
            return self._decision("fault", "Fault is latched; explicit reset with fresh cool sensors required", now_s)
        if reading.temp_c >= cfg.shutdown_c:
            self.hot_latched = True
        elif reading.temp_c < cfg.derate_c:
            self.hot_latched = False
        if requested in ("shutdown", "fault") or self.hot_latched:
            self._cancel_boost(now_s)
            return self._decision("shutdown", "Temperature shutdown" if self.hot_latched else "Operator stop", now_s)
        soc = reading.battery_soc
        if soc is not None:
            if soc <= cfg.shutdown_soc:
                self._cancel_boost(now_s)
                self.reserve_latched = True
                return self._decision("shutdown", "Battery depleted", now_s)
            if soc <= cfg.reserve_soc:
                self.reserve_latched = True
            elif soc >= cfg.recover_soc:
                self.reserve_latched = False
        if self.reserve_latched:
            self._cancel_boost(now_s)
            return self._decision("reserve", "Preserving battery reserve", now_s)
        if reading.temp_c >= cfg.derate_c:
            self._cancel_boost(now_s)
            return self._decision("conserve", "Temperature derating", now_s)
        if soc is None:
            self._cancel_boost(now_s)
            return self._decision("stealth" if requested == "stealth" else "conserve", "Battery state unknown; boost unavailable", now_s)
        if self.boost_until is not None and now_s >= self.boost_until:
            self._cancel_boost(now_s)
        if requested != "boost":
            self._cancel_boost(now_s)
        if requested == "boost":
            if self.boost_until is None:
                if now_s < self.next_boost:
                    return self._decision("conserve", "Boost cooldown", now_s)
                self.boost_until = now_s + cfg.boost_max_s
            return self._decision("boost", "Bounded boost", now_s)
        return self._decision(requested, "Requested mode", now_s)
