from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Battery:
    capacity_wh: float
    v_nom: float = 3.7
    r_int: float = 0.15  # ohms (aggregate pack)
    coulombic_eff: float = 0.98
    max_c_rate: float = 2.0  # x capacity per hour
    peukert_k: float = 0.05  # small for Li-ion

    def clamp_current(self, p_w: float) -> float:
        # approximate current draw from power and nominal voltage
        i = max(p_w, 0.0) / max(self.v_nom, 1e-6)
        max_i = self.max_c_rate * (self.capacity_wh / self.v_nom)
        return min(i, max_i)

    def effective_capacity_wh(self, i_a: float) -> float:
        # Peukert-like adjustment (weak for Li-ion)
        if i_a <= 0:
            return self.capacity_wh
        ref_i = (self.capacity_wh / self.v_nom)  # 1C reference
        ratio = max(i_a / max(ref_i, 1e-6), 1e-6)
        return self.capacity_wh * (ratio ** (-self.peukert_k))

    def step_discharge(self, soc_wh: float, net_p_w: float, dt_h: float) -> float:
        # net_p_w is the net *draw* (>=0)
        i_a = self.clamp_current(net_p_w)
        eff_cap = self.effective_capacity_wh(i_a)
        # energy out (account for coulombic efficiency on discharge path)
        e_wh = (net_p_w * dt_h) / max(self.coulombic_eff, 1e-6)
        new_soc = max(0.0, soc_wh - e_wh)
        # clamp by effective capacity (softly)
        return min(new_soc, eff_cap)

    def step_charge(self, soc_wh: float, p_charge_w: float, dt_h: float) -> float:
        if p_charge_w <= 0:
            return soc_wh
        e_wh = p_charge_w * dt_h * self.coulombic_eff
        return min(self.capacity_wh, soc_wh + e_wh)
