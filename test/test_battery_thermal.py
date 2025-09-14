from ultradevice.battery import Battery
from ultradevice.thermal import ThermalModel

def test_battery_basic():
    bat = Battery(capacity_wh=10.0, v_nom=3.7)
    soc = 10.0
    # draw 3.7W for 1 hour ~ 1C -> about 1Ah -> ~3.7Wh
    soc2 = bat.step_discharge(soc, net_p_w=3.7, dt_h=1.0)
    assert soc2 < soc and soc2 > 5.0

def test_thermal_derate():
    th = ThermalModel(r_th_c_per_w=4.0, t_ambient_c=25.0, t_limit_c=42.0, derate_start_c=39.0)
    df_low = th.derate_factor(35.0)
    df_hi = th.derate_factor(41.0)
    assert df_low == 1.0 and 0.0 < df_hi < 1.0
