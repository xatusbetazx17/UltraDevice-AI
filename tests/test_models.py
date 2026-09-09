import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from ultradevice.config import Boost, Scenario, load_scenario
from ultradevice.models import PowerProfile
from ultradevice.profiles import load_hourly_csv
from ultradevice.randomize import random_scenario


class ValidationTests(unittest.TestCase):
    def test_profile_validation(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                PowerProfile(battery_wh=value, avg_load_w=1)

    def test_invalid_scenarios(self):
        for field, value in (("dt_minutes", 0), ("dt_minutes", 61), ("base_load_w", -1),
                             ("initial_soc", 2), ("battery_wh", float("nan")),
                             ("features", {"radio": {"w": -2}}), ("wrong_name", 1)):
            data = {"battery_wh": 1, "base_load_w": 1, field: value}
            with self.subTest(field=field), self.assertRaises(ValidationError):
                Scenario.model_validate(data)

    def test_boost_horizon_and_cooldown(self):
        with self.assertRaises(ValidationError):
            Scenario(battery_wh=1, base_load_w=1, duration_minutes=1,
                     boosts=[Boost(hour=1, burst_w=1, burst_sec=1)])
        with self.assertRaises(ValidationError):
            Scenario(battery_wh=1, base_load_w=1,
                     boosts=[Boost(hour=0, burst_w=1, burst_sec=30), Boost(hour=0, minute=1, burst_w=1, burst_sec=30)])

    def test_complete_profile_required(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            for contents in ("hour,value\n0,1\n", "hour,value\n0,nan\n", "value\n1\n"):
                path.write_text(contents)
                with self.subTest(contents=contents), self.assertRaises(ValueError):
                    load_hourly_csv(path)

    def test_scenario_relative_profiles(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "sun.csv").write_text("hour,value\n" + "".join(f"{h},1\n" for h in range(24)))
            (path / "scenario.json").write_text('{"battery_wh":1,"base_load_w":1,"harvest":{"solar":{"scale":1,"irradiance_csv":"sun.csv"}}}')
            scenario = load_scenario(path / "scenario.json")
            self.assertEqual(Path(scenario.harvest.solar.irradiance_csv), (path / "sun.csv").resolve())

    def test_seeded_generator_is_valid_and_reproducible(self):
        self.assertEqual(random_scenario(5), random_scenario(5))
        for seed in range(50):
            Scenario.model_validate(random_scenario(seed))
