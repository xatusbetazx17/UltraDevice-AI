from __future__ import annotations

import random
from typing import Any, Dict


def random_scenario(seed: int = 0) -> Dict[str, Any]:
    rng = random.Random(seed)
    base = {
      "name": "random_day",
      "battery_wh": rng.uniform(10.0, 20.0),
      "base_load_w": rng.uniform(0.8, 1.5),
      "features": {
        "sensors": {"on": True, "w": round(rng.uniform(0.5, 1.0), 2)},
        "ui": {"on": True, "w": round(rng.uniform(0.2, 0.6), 2)},
        "radio": {"on": True, "w": round(rng.uniform(0.3, 0.7), 2)},
      },
      "harvest": {
        "solar": {"scale": 0.001 + rng.random()*0.002, "irradiance_csv": "data/sky_irradiance_clear.csv"},
        "kinetic": {"scale": 0.2 + rng.random()*0.3, "motion_csv": "data/motion_profile_commute.csv"}
      },
      "boosts": [{"hour": 17, "burst_w": 8.0 + rng.random()*6.0, "burst_sec": 30 + int(rng.random()*30)}],
      "dt_minutes": rng.choice([5, 10, 15])
    }
    return base
