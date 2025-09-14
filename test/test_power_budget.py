from ultradevice.models import PowerProfile
from ultradevice.power import ideal_runtime_hours, net_power_w

def test_runtime_basic():
    p = PowerProfile(battery_wh=10, avg_load_w=2.0, solar_w=0.5)
    assert round(net_power_w(p), 2) == 1.5
    t = ideal_runtime_hours(p)
    assert 6.5 < t < 7.0  # 10Wh / 1.5W ≈ 6.67h
