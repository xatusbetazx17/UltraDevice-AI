import math
import unittest

from ultradevice.battery import Battery
from ultradevice.thermal import ThermalModel


class BatteryThermalTests(unittest.TestCase):
    def test_battery_basic(self):
        after = Battery(10).step_discharge(10, 3.7, 1)
        self.assertTrue(5 < after < 10)

    def test_invalid_parameters(self):
        for kwargs in ({"capacity_wh": -1}, {"capacity_wh": 1, "v_nom": 0},
                       {"capacity_wh": 1, "coulombic_eff": 1.1}, {"capacity_wh": float("nan")}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Battery(**kwargs)

    def test_current_limit_applies_to_energy(self):
        battery = Battery(10, max_c_rate=0.1, r_int=0, peukert_k=0, coulombic_eff=1)
        self.assertAlmostEqual(battery.step_discharge(10, 100, 1), 9)
        self.assertAlmostEqual(battery.step_charge(0, 100, 1), 1)

    def test_zero_time_and_empty_energy(self):
        battery = Battery(10)
        self.assertEqual(battery.step_discharge(7, 100, 0), 7)
        self.assertEqual(battery.step_discharge(0, 1, 1), 0)
        self.assertEqual(battery.step_charge(10, 10, 1), 10)
        self.assertLessEqual(battery.effective_capacity_wh(0.01), 10)

    def test_no_negative_energy_inputs(self):
        with self.assertRaises(ValueError):
            Battery(1).step_discharge(1, 1, -1)

    def test_thermal_exact_rc(self):
        thermal = ThermalModel(r_th_c_per_w=4, c_th_j_per_c=200)
        self.assertAlmostEqual(thermal.step(25, 1, 800 / 3600), 25 + 4 * (1 - math.exp(-1)))
        self.assertEqual(thermal.step(31, 100, 0), 31)

    def test_long_thermal_step_stable(self):
        thermal = ThermalModel()
        self.assertAlmostEqual(thermal.step(25, 1, 24), 29)
        self.assertAlmostEqual(thermal.step(40, 0, 24), 25)
        self.assertEqual(thermal.derate_factor(39), 1)
        self.assertEqual(thermal.derate_factor(42), 0)
        self.assertTrue(0 < thermal.derate_factor(41) < 1)

    def test_invalid_thermal_model(self):
        for kwargs in ({"r_th_c_per_w": 0}, {"derate_start_c": 43}, {"c_th_j_per_c": float("inf")}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ThermalModel(**kwargs)
