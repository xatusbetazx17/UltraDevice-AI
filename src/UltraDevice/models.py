from pydantic import BaseModel, Field

class PowerProfile(BaseModel):
    battery_wh: float = Field(..., gt=0, description="Battery capacity in Watt-hours")
    avg_load_w: float = Field(..., ge=0, description="Average device load in Watts")
    solar_w: float = Field(0.0, ge=0)
    kinetic_w: float = Field(0.0, ge=0)
    thermal_w: float = Field(0.0, ge=0)

    @property
    def harvest_w(self) -> float:
        return self.solar_w + self.kinetic_w + self.thermal_w
