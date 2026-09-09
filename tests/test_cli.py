import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def invoke(self, arguments, cwd):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run([sys.executable, "-m", "ultradevice", *arguments], cwd=cwd, env=env,
                              text=True, capture_output=True, timeout=20)

    def test_module_help_includes_every_late_command(self):
        result = self.invoke(["--help"], ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("simulate-physics", "randomize", "validate-scenario", "size-battery", "device", "demo"):
            self.assertIn(command, result.stdout)

    def test_all_documented_budget_commands(self):
        cases = [
            ["runtime", "--battery-wh", "12", "--avg-load-w", "2.8", "--solar-w", "0.6"],
            ["boost", "--battery-wh", "12", "--burst-w", "10", "--burst-sec", "60"],
            ["duty", "--battery-wh", "12", "--target-hours", "8", "--avg-load-w", "3"],
            ["size_battery", "--target-hours", "8", "--avg-load-w", "3"],
            ["doctor"],
        ]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.invoke(arguments, ROOT)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_file_commands_work_outside_repo_and_without_parent_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            cases = [
                ["profile", "--out", "scenario.json"],
                ["validate_scenario", "--scenario", "scenario.json"],
                ["simulate", "--scenario", "scenario.json", "--out", "simple.csv"],
                ["simulate_physics", "--scenario", "scenario.json", "--out", "physics.csv"],
                ["report", "--csv", "physics.csv", "--out", "report.md"],
                ["randomize", "--seed", "42", "--out", "random.json"],
                ["validate-scenario", "--scenario", "random.json"],
                ["optimize", "--battery-wh", "12", "--target-hours", "8", "--out", "optimized.json"],
                ["demo", "--seconds", "2", "--out", "demo.jsonl"],
                ["check-log", "--input", "demo.jsonl"],
                ["schema", "--kind", "reading", "--out", "reading.json"],
            ]
            for arguments in cases:
                with self.subTest(arguments=arguments):
                    result = self.invoke(arguments, directory)
                    self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((Path(directory) / "reading.json").read_text())["title"], "Reading")

    def test_invalid_scenario_and_infeasible_target_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "bad.json").write_text('{"battery_wh":1,"base_load_w":1,"dt_minutes":0}')
            for arguments in (["simulate", "--scenario", "bad.json"],
                              ["optimize", "--battery-wh", "1", "--target-hours", "24"],
                              ["demo", "--seconds", "nan"]):
                with self.subTest(arguments=arguments):
                    result = self.invoke(arguments, folder)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("Error:", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Optional plot dependency")
    def test_plot_creates_three_different_files(self):
        with tempfile.TemporaryDirectory() as folder:
            for arguments in (["profile", "--out", "scenario.json"],
                              ["simulate", "--scenario", "scenario.json", "--out", "data.csv"],
                              ["plot", "--csv", "data.csv", "--out", "chart.png"]):
                result = self.invoke(arguments, folder)
                self.assertEqual(result.returncode, 0, result.stderr)
            for suffix in ("soc", "load", "harvest"):
                path = Path(folder) / ("chart_" + suffix + ".png")
                self.assertGreater(path.stat().st_size, 1000)
