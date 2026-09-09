"""Stable exact step for a first-order thermal RC model."""
import math
from dataclasses import dataclass

from .validation import number


@dataclass
class ThermalModel:
    r_th_c_per_w: float = 4.0
    c_th_j_per_c: float = 200.0
    t_ambient_c: float = 25.0
    t_limit_c: float = 42.0
    derate_start_c: float = 39.0

    def __post_init__(self):
        number("r_th_c_per_w", self.r_th_c_per_w, positive=True)
        number("c_th_j_per_c", self.c_th_j_per_c, positive=True)
        for name in ("t_ambient_c", "t_limit_c", "derate_start_c"):
            number(name, getattr(self, name), minimum=-273.15, positive=True)
        if self.derate_start_c >= self.t_limit_c:
            raise ValueError("derate_start_c must be below t_limit_c")

    def derate_factor(self, t_c):
        number("t_c", t_c, minimum=-273.15, positive=True)
        return min(1.0, max(0.0, (self.t_limit_c - t_c) / (self.t_limit_c - self.derate_start_c)))

    def step(self, t_prev_c, p_w, dt_h, ambient_c=None):
        number("t_prev_c", t_prev_c, minimum=-273.15, positive=True)
        number("p_w", p_w)
        number("dt_h", dt_h)
        ambient = self.t_ambient_c if ambient_c is None else ambient_c
        number("ambient_c", ambient, minimum=-273.15, positive=True)
        equilibrium = ambient + p_w * self.r_th_c_per_w
        decay = math.exp(-dt_h * 3600 / (self.r_th_c_per_w * self.c_th_j_per_c))
        return equilibrium + (t_prev_c - equilibrium) * decay
