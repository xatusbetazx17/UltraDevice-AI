from __future__ import annotations

class PolicyEngine:
    """Rule-based policy:
    - Reduce radio/UI duty at low battery SOC.
    - Disallow boost when SOC is very low.
    """
    def decide(self, soc: float) -> dict:
        return {
            "radio_duty": 0.5 if soc < 0.2 else 1.0,
            "ui_duty": 0.6 if soc < 0.15 else 1.0,
            "allow_boost": soc > 0.1,
        }
