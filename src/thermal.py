from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ThermalModel:
    r_th_c_per_w: float = 4.0   # thermal resistance body->ambient (C/W)
    c_th_j_per_c: float = 200.0 # thermal capacitance (J/C), placeholder
    t_ambient_c: float = 25.0
    t_limit_c: float = 42.0
    derate_start_c: float = 39.0

    def derate_factor(self, t_c: float) -> float:
        # 1.0 below derate_start, 0 at limit
        if t_c <= self.derate_start_c:
            return 1.0
        if t_c >= self.t_limit_c:
            return 0.0
        span = self.t_limit_c - self.derate_start_c
        return max(0.0, 1.0 - (t_c - self.derate_start_c) / max(span, 1e-6))

    def step(self, t_prev_c: float, p_w: float, dt_h: float) -> float:
        # simple RC heating: deltaT ≈ p*Rth*(1 - exp(-dt/RC)) (approximate discrete step)
        # Use a crude Euler step for simplicity.
        # Convert C_th to Wh/C for unit consistency: J = W*s; 1 Wh = 3600 J
        c_wh_per_c = self.c_th_j_per_c / 3600.0
        dT = (p_w * self.r_th_c_per_w - (t_prev_c - self.t_ambient_c)) * (dt_h / max(c_wh_per_c,1e-6))
        return t_prev_c + dT
