"""Lumped energy/current model; not a cell chemistry or protection circuit model."""
from dataclasses import dataclass

from .validation import efficiency, number


@dataclass
class Battery:
    capacity_wh: float
    v_nom: float = 3.7
    r_int: float = 0.15
    coulombic_eff: float = 0.98  # historical name; treated as energy efficiency here
    max_c_rate: float = 2.0
    peukert_k: float = 0.05

    def __post_init__(self):
        for name in ("capacity_wh", "v_nom", "max_c_rate"):
            number(name, getattr(self, name), positive=True)
        number("r_int", self.r_int)
        number("peukert_k", self.peukert_k)
        efficiency("coulombic_eff", self.coulombic_eff)

    @property
    def max_power_w(self):
        return self.capacity_wh * self.max_c_rate

    def clamp_current(self, p_w):
        number("p_w", p_w)
        return min(p_w, self.max_power_w) / self.v_nom

    def effective_capacity_wh(self, i_a):
        number("i_a", i_a)
        ratio = max(1.0, i_a / (self.capacity_wh / self.v_nom))
        return self.capacity_wh * ratio ** -self.peukert_k

    def discharge_factor(self, p_w):
        current = self.clamp_current(p_w)
        return (self.capacity_wh / self.effective_capacity_wh(current) / self.coulombic_eff
                + min(p_w, self.max_power_w) * self.r_int / self.v_nom ** 2)

    def step_discharge(self, soc_wh, net_p_w, dt_h):
        number("soc_wh", soc_wh)
        number("net_p_w", net_p_w)
        number("dt_h", dt_h)
        # Rate limits constrain delivered power, not just a computed current value.
        draw = min(net_p_w, self.max_power_w)
        return max(0.0, min(soc_wh, self.capacity_wh) - draw * dt_h * self.discharge_factor(draw))

    def step_charge(self, soc_wh, p_charge_w, dt_h):
        number("soc_wh", soc_wh)
        number("p_charge_w", p_charge_w)
        number("dt_h", dt_h)
        return min(self.capacity_wh, soc_wh + min(p_charge_w, self.max_power_w) * dt_h * self.coulombic_eff)
