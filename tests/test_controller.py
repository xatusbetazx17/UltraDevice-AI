import unittest

from pydantic import ValidationError

from ultradevice.controller import ControllerConfig, DeviceController, Reading


def reading(index, **changes):
    fields = dict(seq=index, uptime_ms=index * 1000, temp_c=25.0, temp_source="simulated",
                  battery_soc=0.8, load_w=0.2, harvest_w=0.01, device_mode="normal", sensor_ok=True)
    fields.update(changes)
    return Reading(**fields)


class ControllerTests(unittest.TestCase):
    def test_invalid_limits(self):
        for values in ({"shutdown_c": 38}, {"cooldown_s": 0}, {"boost_max_s": 11},
                       {"recover_soc": 0.1}, {"reserve_soc": 0.01}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                ControllerConfig(**values)

    def test_wire_schema_is_strict(self):
        for changes in ({"seq": "2"}, {"battery_soc": float("nan")}, {"sensor_ok": "true"},
                        {"temp_source": "skin"}, {"uptime_ms": True}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                reading(1, **changes)

    def test_unknown_battery_is_not_fabricated(self):
        controller = DeviceController()
        result = controller.step(reading(0, battery_soc=None), 0, "boost")
        self.assertEqual(result.mode, "conserve")
        self.assertIn("unknown", result.reason)

    def test_reserve_hysteresis(self):
        controller = DeviceController()
        for index, (soc, expected) in enumerate(((0.19, "reserve"), (0.24, "reserve"), (0.25, "normal"))):
            self.assertEqual(controller.step(reading(index, battery_soc=soc), index).mode, expected)

    def test_shutdown_empty_battery(self):
        result = DeviceController().step(reading(0, battery_soc=0.01), 0)
        self.assertEqual(result.mode, "shutdown")

    def test_thermal_hysteresis(self):
        controller = DeviceController()
        for index, (temp, expected) in enumerate(((42, "shutdown"), (40, "shutdown"), (38, "normal"), (39, "conserve"))):
            self.assertEqual(controller.step(reading(index, temp_c=temp), index).mode, expected)

    def test_missing_sensor_fault_latches(self):
        controller = DeviceController()
        self.assertEqual(controller.step(reading(0, temp_c=None, sensor_ok=False), 0).mode, "fault")
        self.assertEqual(controller.step(reading(1), 1).mode, "fault")
        self.assertEqual(controller.step(reading(2), 2, reset_fault=True).mode, "normal")

    def test_stale_and_replayed_samples(self):
        for stale in (False, True):
            controller = DeviceController()
            controller.step(reading(0), 0)
            result = controller.step(reading(1 if stale else 0), 4 if stale else 1)
            self.assertEqual(result.mode, "fault")

    def test_future_receipt_rejected(self):
        self.assertEqual(DeviceController().step(reading(0), 0, received_s=1).mode, "fault")

    def test_boost_does_not_extend_and_cooldown_survives_requests(self):
        controller = DeviceController()
        results = []
        for t in range(132):
            results.append(controller.step(reading(t), t, "boost"))
        self.assertTrue(all(r.mode == "conserve" for r in results[:60]))
        self.assertTrue(all(r.mode == "boost" for r in results[60:70]))
        self.assertTrue(all(r.mode == "conserve" for r in results[70:130]))
        self.assertEqual(results[130].mode, "boost")
        self.assertEqual(results[69].boost_remaining_s, 1)

    def test_stealth_disables_advisory_radio_and_ui(self):
        result = DeviceController().step(reading(0), 0, "stealth")
        self.assertEqual((result.radio_duty, result.ui_duty), (0, 0))
