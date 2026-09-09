import unittest

from ultradevice.powertrain import effective_net_draw, signed_net_draw
from ultradevice.sizing import battery_mass_kg, size_pack


class SizingTests(unittest.TestCase):
    def test_powertrain(self):
        self.assertAlmostEqual(effective_net_draw(3, 0.5), 3 / 0.9 - 0.5 * 0.8)
        self.assertLess(signed_net_draw(0, 1), 0)

    def test_sizing(self):
        result = size_pack(8, 3, 0.5)
        self.assertAlmostEqual(result["battery_wh"], 23.47)
        self.assertGreater(result["approx_mass_kg"], 0)

    def test_invalid_efficiency(self):
        for value in (0, -1, 1.1, float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                effective_net_draw(1, 0, eff_out=value)
        with self.assertRaises(ValueError):
            battery_mass_kg(1, 0)
