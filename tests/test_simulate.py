import tempfile
import unittest
from pathlib import Path

from ultradevice.battery import Battery
from ultradevice.config import Boost, Feature, HarvestCfg, Scenario
from ultradevice.report import summarize
from ultradevice.simulate import simulate, simulate_physics
from ultradevice.telemetry import write_csv


class SimulationTests(unittest.TestCase):
    def scenario(self, **values):
        return Scenario(**({"battery_wh": 100, "base_load_w": 1, "duration_minutes": 60} | values))

    def test_original_scenario(self):
        rows = simulate(self.scenario(battery_wh=5, duration_minutes=1440, dt_minutes=15,
                                      features={"ui": Feature(w=0.2)}))
        self.assertEqual(len(rows), 96)
        self.assertTrue(all(a["soc"] >= b["soc"] for a, b in zip(rows, rows[1:])))

    def test_boost_once_and_exact_fractional_duration(self):
        for dt in (1, 5, 7, 60):
            rows = simulate(self.scenario(dt_minutes=dt, boosts=[Boost(hour=0, burst_w=10, burst_sec=3.5)]))
            with self.subTest(dt=dt):
                self.assertEqual(sum(r["boosts_accepted"] for r in rows), 1)
                self.assertAlmostEqual(rows[-1]["soc_wh"], 99 - 35 / 3600, places=8)
                self.assertAlmostEqual(sum(r["boost_w"] * r["dt_min"] / 60 for r in rows), 35 / 3600)

    def test_boost_blocked_once_at_low_soc(self):
        rows = simulate(self.scenario(initial_soc=0.05, boosts=[Boost(hour=0, burst_w=10, burst_sec=30)]))
        self.assertEqual(sum(r["boosts_blocked"] for r in rows), 1)
        self.assertEqual(sum(r["boost_w"] for r in rows), 0)

    def test_disabled_radio_never_subtracted(self):
        rows = simulate(self.scenario(initial_soc=0.1, features={"radio": Feature(on=False, w=50)}))
        self.assertTrue(all(abs(r["load_w"] - 1) < 1e-9 for r in rows))

    def test_surplus_recharges(self):
        for function in (simulate, simulate_physics):
            rows = function(self.scenario(battery_wh=1, initial_soc=0.2, base_load_w=0.1,
                                          harvest=HarvestCfg(external_w=1)))
            with self.subTest(function=function.__name__):
                self.assertGreater(rows[-1]["soc_wh"], 0.2)
                self.assertLessEqual(rows[-1]["soc"], 1)
                self.assertGreater(sum(r["battery_charge_wh"] for r in rows), 0)

    def test_empty_battery_cannot_deliver_free_power(self):
        rows = simulate(self.scenario(battery_wh=0.1))
        self.assertEqual(rows[-1]["load_w"], 0)
        self.assertAlmostEqual(sum(r["load_w"] * r["dt_min"] / 60 for r in rows), 0.1)
        self.assertAlmostEqual(sum(r["unserved_w"] * r["dt_min"] / 60 for r in rows), 0.9)

    def test_partial_intervals_and_report_include_first_step(self):
        rows = simulate(self.scenario(duration_minutes=61, dt_minutes=7))
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[-1]["dt_min"], 5)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.csv"
            write_csv(path, rows)
            report = summarize(path)
            self.assertAlmostEqual(report["hours"], 61 / 60)
            self.assertAlmostEqual(report["energy_load_Wh"], 61 / 60)

    def test_physics_keeps_boost_energy(self):
        scenario = self.scenario(boosts=[Boost(hour=0, burst_w=10, burst_sec=30)], eff_out=1, eff_harv=1)
        battery = Battery(100, r_int=0, peukert_k=0, coulombic_eff=1)
        rows = simulate_physics(scenario, battery=battery)
        self.assertAlmostEqual(rows[-1]["soc_wh"], 99 - 300 / 3600, places=8)

    def test_current_limit_records_unserved_power(self):
        rows = simulate_physics(self.scenario(battery_wh=10, base_load_w=10, duration_minutes=1),
                                battery=Battery(10, max_c_rate=0.01))
        self.assertLessEqual(rows[0]["load_w"], 0.091)
        self.assertGreater(rows[0]["unserved_w"], 9)

    def test_energy_accounting(self):
        rows = simulate_physics(self.scenario(battery_wh=1, initial_soc=0.5,
                                harvest=HarvestCfg(external_w=2)))
        balance = rows[0]["initial_soc_wh"] + sum(r["battery_charge_wh"] - r["battery_draw_wh"] for r in rows)
        self.assertAlmostEqual(balance, rows[-1]["soc_wh"])

    def test_hot_ambient_does_not_claim_safe_cooling(self):
        rows = simulate_physics(self.scenario(ambient_c=45))
        self.assertEqual(rows[-1]["load_w"], 0)
        self.assertGreaterEqual(rows[-1]["temp_c"], 45)

    def test_one_interval_report_and_empty_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "out.csv"
            write_csv(path, simulate(self.scenario(duration_minutes=1)))
            self.assertAlmostEqual(summarize(path)["hours"], 1 / 60)
            with self.assertRaises(ValueError):
                write_csv(path, [])
