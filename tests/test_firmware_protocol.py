import importlib.util
import json
import os
import threading
import unittest
from pathlib import Path

from ultradevice.protocol import MAX_FRAME, SerialDevice, decode_frame, encode_frame

ROOT = Path(__file__).resolve().parents[1]


def load_firmware(name):
    spec = importlib.util.spec_from_file_location("firmware_" + name, ROOT / "firmware" / "pico" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SafetyController = load_firmware("safety").SafetyController
DeviceService = load_firmware("service").DeviceService
TMP117 = load_firmware("sensors").TMP117


class FirmwareTests(unittest.TestCase):
    def test_boost_timeout_and_cooldown(self):
        guard = SafetyController()
        self.assertEqual(guard.command("boost", 0, 25, True), "conserve")
        for t in range(60000, 70000, 1000):
            self.assertEqual(guard.command("boost", t, 25, True), "boost")
        self.assertEqual(guard.command("boost", 70000, 25, True), "conserve")
        self.assertEqual(guard.command("boost", 71000, 25, True), "conserve")

    def test_temperature_and_hardware_stop_override_host(self):
        guard = SafetyController()
        self.assertEqual(guard.command("boost", 60000, 42, True), "shutdown")
        self.assertEqual(guard.command("normal", 61000, 41, True), "shutdown")
        self.assertEqual(guard.command("normal", 62000, 25, True, stop_pressed=True), "shutdown")

    def test_heartbeat_loss(self):
        guard = SafetyController()
        guard.command("normal", 0, 25, True)
        self.assertEqual(guard.tick(3001, 25, True), "shutdown")

    def test_invalid_temp_is_latched(self):
        guard = SafetyController()
        self.assertEqual(guard.tick(0, None, False), "fault")
        self.assertEqual(guard.command("normal", 1, 25, True), "fault")
        self.assertTrue(guard.reset(25, True))
        self.assertEqual(guard.command("normal", 2, 25, True), "normal")

    def test_protocol_rejects_unknown_fields_and_commands(self):
        service = DeviceService(SafetyController())
        for value in ([], {"v": 2, "id": 1}, {"v": 1, "id": True},
                      {"v": 1, "id": 1, "op": "set_mode", "mode": "boost", "override": True},
                      {"v": 1, "id": 1, "op": "exec"}):
            with self.subTest(value=value):
                self.assertFalse(service.handle(value, 0, 25, True)["ok"])

    def test_tmp117_register_decoding(self):
        class I2C:
            raw = b"\x0c\x80"
            def readfrom_mem(self, address, register, count):
                self_address = address
                if self_address != 0x48 or count != 2:
                    raise AssertionError("wrong bus request")
                return b"\x01\x17" if register == 0x0F else self.raw
        bus = I2C()
        sensor = TMP117(bus)
        self.assertEqual(sensor.temperature_c(), 25)
        bus.raw = b"\xf3\x80"
        self.assertEqual(sensor.temperature_c(), -25)
        bus.raw = b"\x80\x00"
        with self.assertRaises(ValueError):
            sensor.temperature_c()

    def test_tmp117_identity_required(self):
        class I2C:
            def readfrom_mem(self, *args):
                return b"\x00\x00"
        with self.assertRaises(ValueError):
            TMP117(I2C())


class ProtocolTests(unittest.TestCase):
    def test_frames_are_bounded_and_finite(self):
        for raw in (b"{}", b"[]\n", b'{"v":1,"id":0,"value":NaN}\n',
                    b'{"v":true,"id":0}\n', b'{"v":1,"id":true}\n', b"x" * (MAX_FRAME + 1) + b"\n"):
            with self.subTest(raw=raw[:50]), self.assertRaises(ValueError):
                decode_frame(raw)

    def test_actual_firmware_service_matches_host(self):
        class Transport:
            service = DeviceService(SafetyController())
            def write(self, data, timeout):
                self.response = self.service.handle(json.loads(data), 10, 25.0, True)
            def readline(self, timeout):
                return encode_frame(self.response)
            def close(self):
                pass
        device = SerialDevice(transport=Transport())
        sample = device.sample()
        self.assertIsNone(sample.battery_soc)
        self.assertEqual(sample.temp_c, 25)
        self.assertEqual(device.set_mode("stealth"), "stealth")
        self.assertEqual(device.set_mode("shutdown"), "shutdown")

    @unittest.skipUnless(os.name == "posix", "POSIX USB TTY integration")
    def test_real_tty_with_fragmented_firmware_responses(self):
        import pty
        master, slave = pty.openpty()
        path = os.ttyname(slave)
        failure = []
        def board():
            service = DeviceService(SafetyController())
            buffer = b""
            try:
                for i in range(3):
                    while b"\n" not in buffer:
                        buffer += os.read(master, 1024)
                    line, _, buffer = buffer.partition(b"\n")
                    response = encode_frame(service.handle(json.loads(line), i * 1000, 25.0, True))
                    os.write(master, response[:5])
                    os.write(master, response[5:])
            except BaseException as error:
                failure.append(error)
        device = SerialDevice(path)
        worker = threading.Thread(target=board, daemon=True)
        worker.start()
        try:
            self.assertEqual(device.sample().temp_c, 25)
            self.assertEqual(device.set_mode("stealth"), "stealth")
            self.assertEqual(device.set_mode("shutdown"), "shutdown")
            worker.join(timeout=3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(failure, [])
        finally:
            device.close()
            os.close(master)
            os.close(slave)
