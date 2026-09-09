"""Optional empirical capacity-fade estimate, not automatically applied in simulation."""
from dataclasses import dataclass

from .validation import number


@dataclass
class BatteryAging:
    capacity_wh_nom: float
    throughput_wh: float = 0.0
    calendar_days: float = 0.0
    fade_per_kwh: float = 0.02
    calendar_fade_per_year: float = 0.03

    def __post_init__(self):
        number("capacity_wh_nom", self.capacity_wh_nom, positive=True)
        for name in ("throughput_wh", "calendar_days", "fade_per_kwh", "calendar_fade_per_year"):
            number(name, getattr(self, name))

    def record_throughput(self, wh):
        self.throughput_wh += number("wh", wh)

    def advance_days(self, days):
        self.calendar_days += number("days", days)

    @property
    def capacity_wh(self):
        fade = min(0.4, self.throughput_wh / 1000 * self.fade_per_kwh
                   + self.calendar_days / 365 * self.calendar_fade_per_year)
        return self.capacity_wh_nom * (1 - fade)
