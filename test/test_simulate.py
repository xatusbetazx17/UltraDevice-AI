from ultradevice.config import Scenario, Feature, HarvestCfg
from ultradevice.simulate import simulate

def test_simulate_basic():
    scn = Scenario(
        name="t",
        battery_wh=5.0,
        base_load_w=1.0,
        features={"ui": Feature(on=True, w=0.2)},
        harvest=HarvestCfg(),
        boosts=[],
        dt_minutes=15,
    )
    rows = simulate(scn)
    assert len(rows) == (24*60)//15
    socs = [r["soc"] for r in rows]
    assert all(socs[i] >= socs[i+1] - 1e-6 for i in range(len(socs)-1))
