from ultradevice.powertrain import effective_net_draw
from ultradevice.sizing import size_pack

def test_powertrain_draw():
    # 3W load, 0.5W harvest → battery sees about 3/0.9 - 0.5*0.8 = 3.333.. - 0.4 = 2.933.. W
    p = effective_net_draw(3.0, 0.5, eff_out=0.9, eff_harv=0.8)
    assert 2.8 < p < 3.1

def test_size_pack():
    res = size_pack(8, 3.0, 0.5)
    assert res["battery_wh"] > 0 and res["approx_mass_kg"] > 0
