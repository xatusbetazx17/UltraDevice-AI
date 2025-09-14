from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Feature(BaseModel):
    on: bool = True
    w: float = 0.0

class SolarCfg(BaseModel):
    scale: float = 0.0
    irradiance_csv: str

class KineticCfg(BaseModel):
    scale: float = 0.0
    motion_csv: str

class HarvestCfg(BaseModel):
    solar: Optional[SolarCfg] = None
    kinetic: Optional[KineticCfg] = None

class Boost(BaseModel):
    hour: int
    burst_w: float
    burst_sec: float

class Scenario(BaseModel):
    name: str = "scenario"
    battery_wh: float = Field(..., gt=0)
    base_load_w: float = Field(..., ge=0)
    features: Dict[str, Feature] = {}
    harvest: HarvestCfg = HarvestCfg()
    boosts: List[Boost] = []
    dt_minutes: int = 5
