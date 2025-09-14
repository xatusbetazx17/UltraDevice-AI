from __future__ import annotations
import random
from typing import Dict, Any

def random_scenario(seed: int = 0) -> Dict[str, Any]:
    random.seed(seed)
    base = {
      "name": "random_day",
      "battery_wh": random.uniform(10.0, 20.0),
      "base_load_w": random.uniform(0.8, 1.5),
      "features": {
        "sensors": {"on": True, "w": round(random.uniform(0.5, 1.0), 2)},
        "ui": {"on": True, "w": round(random.uniform(0.2, 0.6), 2)},
        "radio": {"on": True, "w": round(random.uniform(0.3, 0.7), 2)},
      },
      "harvest": {
        "solar": {"scale": 0.001 + random.random()*0.002, "irradiance_csv": "data/sky_irradiance_clear.csv"},
        "kinetic": {"scale": 0.2 + random.random()*0.3, "motion_csv": "data/motion_profile_commute.csv"}
      },
      "boosts": [{"hour": 17, "burst_w": 8.0 + random.random()*6.0, "burst_sec": 30 + int(random.random()*60)}],
      "dt_minutes": random.choice([5, 10, 15])
    }
    return base
