import unittest

from ultradevice.models import PowerProfile
from ultradevice.power import (
    duty_fraction_for_target,
    ideal_runtime_hours,
    net_power_w,
    reserve_boost,
)


class BudgetTests(unittest.TestCase):
    def test_original_runtime(self):
        profile = PowerProfile(battery_wh=10, avg_load_w=2, solar_w=0.5)
        self.assertEqual(net_power_w(profile), 1.5)
        self.assertAlmostEqual(ideal_runtime_hours(profile), 10 / 1.5)

    def test_harvest_can_exceed_low_load(self):
        self.assertAlmostEqual(duty_fraction_for_target(1, 4, 1, 2, 1), 2 / 3)

    def test_infeasible_target(self):
        with self.assertRaises(ValueError):
            duty_fraction_for_target(1, 4, 2, 0, 10)

    def test_invalid_budget(self):
        for values in ((1, 1, 2, 0, 1), (1, 4, 1, 0, 0), (1, 4, 1, -1, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                duty_fraction_for_target(*values)
        with self.assertRaises(ValueError):
            reserve_boost(10, -1, 10)

    def test_equal_power_modes(self):
        self.assertEqual(duty_fraction_for_target(10, 1, 1, 0, 1), 1)
