import json
import tempfile
import unittest
from pathlib import Path

from ultradevice.ai import PolicyLearner
from ultradevice.audit import verify_log
from ultradevice.device import SimulatedDevice, run_demo, run_session


class DeviceTests(unittest.TestCase):
    def test_full_virtual_demo_and_shutdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "demo.jsonl"
            result = run_demo(95, path)
            self.assertEqual(result["modes"], ["boost", "conserve", "normal", "stealth"])
            self.assertEqual(result["source"], "simulated")
            self.assertEqual(verify_log(path)["records"], result["samples"] + 3)
            last = json.loads(path.read_text().splitlines()[-1])
            self.assertEqual(last["data"]["acknowledged_mode"], "shutdown")

    def test_edit_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "demo.jsonl"
            run_demo(1, path)
            path.write_text(path.read_text().replace('"source": "simulated"', '"source": "usb"'))
            with self.assertRaises(ValueError):
                verify_log(path)

    def test_failure_stops_and_closes_device(self):
        class BrokenDevice(SimulatedDevice):
            def sample(self):
                raise OSError("disconnected")
        device = BrokenDevice()
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(OSError):
            run_session(device, 1, Path(folder) / "error.jsonl", realtime=False)
        self.assertEqual(device.mode, "shutdown")
        self.assertTrue(device.closed)

    def test_validation_error_also_closes_device(self):
        device = SimulatedDevice()
        with self.assertRaises(ValueError):
            run_session(device, -1, "unused.jsonl", realtime=False)
        self.assertTrue(device.closed)
        self.assertEqual(device.mode, "shutdown")

    def test_predictor_is_bounded_and_explicit(self):
        learner = PolicyLearner()
        self.assertIsNone(learner.forecast(1))
        for _ in range(200):
            learner.update(1, 0.5)
        self.assertEqual(len(learner.history), 100)
        self.assertEqual(learner.forecast(1), 2)
        with self.assertRaises(ValueError):
            learner.update(-1, 0)

    def test_prediction_can_conserve_when_target_infeasible(self):
        with tempfile.TemporaryDirectory() as folder:
            result = run_session(SimulatedDevice(), 2, Path(folder) / "log.jsonl", realtime=False,
                                 target_hours=100, capacity_wh=2)
            self.assertEqual(result["modes"], ["conserve"])
