"""Validated scenario schema. Power is watts, energy Wh, time minutes/seconds."""
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, validate_assignment=True, strict=True)


class Feature(StrictModel):
    on: bool = True
    w: float = Field(0.0, ge=0)


class SolarCfg(StrictModel):
    scale: float = Field(0.0, ge=0)
    irradiance_csv: str


class KineticCfg(StrictModel):
    scale: float = Field(0.0, ge=0)
    motion_csv: str


class HarvestCfg(StrictModel):
    solar: SolarCfg | None = None
    kinetic: KineticCfg | None = None
    thermal_w: float = Field(0.0, ge=0)
    external_w: float = Field(0.0, ge=0)


class Boost(StrictModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    burst_w: float = Field(gt=0)
    burst_sec: float = Field(gt=0, le=60)

    @property
    def start_s(self):
        return self.hour * 3600 + self.minute * 60


class Scenario(StrictModel):
    name: str = "scenario"
    battery_wh: float = Field(gt=0)
    initial_soc: float = Field(1.0, ge=0, le=1)
    base_load_w: float = Field(ge=0)
    features: dict[str, Feature] = Field(default_factory=dict)
    harvest: HarvestCfg = Field(default_factory=HarvestCfg)
    boosts: list[Boost] = Field(default_factory=list)
    dt_minutes: int = Field(5, ge=1, le=60)
    duration_minutes: int = Field(1440, ge=1, le=1440)
    boost_cooldown_s: float = Field(300.0, ge=0)
    reserve_soc: float = Field(0.1, ge=0, le=1)
    ambient_c: float = Field(25.0, ge=-40, le=85)
    ambient_csv: str | None = None
    cloudiness_csv: str | None = None
    eff_out: float = Field(0.9, gt=0, le=1)
    eff_harv: float = Field(0.8, gt=0, le=1)

    @model_validator(mode="after")
    def check_boosts(self):
        previous_end = None
        for boost in sorted(self.boosts, key=lambda b: b.start_s):
            if boost.start_s + boost.burst_sec > self.duration_minutes * 60:
                raise ValueError("boost must finish within the scenario duration")
            if previous_end is not None and boost.start_s < previous_end + self.boost_cooldown_s:
                raise ValueError("boosts overlap or violate boost_cooldown_s")
            previous_end = boost.start_s + boost.burst_sec
        return self


def load_scenario(path):
    """Resolve relative CSV paths beside the scenario; bundled data/... also works."""
    from .profiles import resolve_profile

    source = Path(path).resolve()
    scn = Scenario.model_validate_json(source.read_text(encoding="utf-8"))
    if scn.harvest.solar:
        scn.harvest.solar.irradiance_csv = str(resolve_profile(
            scn.harvest.solar.irradiance_csv, source.parent))
    if scn.harvest.kinetic:
        scn.harvest.kinetic.motion_csv = str(resolve_profile(
            scn.harvest.kinetic.motion_csv, source.parent))
    for field in ("ambient_csv", "cloudiness_csv"):
        if getattr(scn, field):
            setattr(scn, field, str(resolve_profile(getattr(scn, field), source.parent)))
    return scn
