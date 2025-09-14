from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BatteryAging:
    capacity_wh_nom: float
    throughput_wh: float = 0.0
    calendar_days: float = 0.0
    # simple parameters
    fade_per_kwh: float = 0.02  # 2% per kWh throughput
    calendar_fade_per_year: float = 0.03  # 3%/year

    def record_throughput(self, wh: float):
        self.throughput_wh += max(wh, 0.0)

    @property
    def capacity_wh(self) -> float:
        cycle_fade = (self.throughput_wh / 1000.0) * self.fade_per_kwh
        cal_fade = (self.calendar_days / 365.0) * self.calendar_fade_per_year
        fade = min(0.4, max(0.0, cycle_fade + cal_fade))  # cap 40% loss
        return self.capacity_wh_nom * (1.0 - fade)
