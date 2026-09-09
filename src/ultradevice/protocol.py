"""Bounded, versioned request/response JSON over a local USB serial port."""
import json
import os
import time

from .controller import MODES, Reading
from .validation import number

MAX_FRAME = 4096


def encode_frame(value):
    data = (json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n").encode()
    if len(data) > MAX_FRAME:
        raise ValueError("Frame too large")
    return data


def decode_frame(raw):
    if len(raw) > MAX_FRAME or not raw.endswith(b"\n"):
        raise ValueError("Oversize or incomplete frame")
    def reject(value):
        raise ValueError(f"Non-finite JSON constant: {value}")
    try:
        value = json.loads(raw.decode("utf-8"), parse_constant=reject)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid JSON frame") from error
    if not isinstance(value, dict) or type(value.get("v")) is not int or value["v"] != 1:
        raise ValueError("Unsupported protocol version")
    if type(value.get("id")) is not int or value["id"] < 0:
        raise ValueError("Invalid request id")
    return value


class PosixTransport:
    """POSIX TTY implementation; leaves terminal settings restored on close."""
    def __init__(self, port):
        import termios
        import tty
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        self.buffer = bytearray()
        self.original = None
        try:
            self.original = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
            settings = termios.tcgetattr(self.fd)
            settings[4] = settings[5] = termios.B115200
            termios.tcsetattr(self.fd, termios.TCSANOW, settings)
        except Exception:
            self.close()
            raise

    def write(self, data, timeout):
        import select
        deadline = time.monotonic() + timeout
        while data:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([], [self.fd], [], remaining)[1]:
                raise TimeoutError("Serial write timed out")
            count = os.write(self.fd, data)
            if not count:
                raise OSError("Serial disconnected")
            data = data[count:]

    def readline(self, timeout):
        import select
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            if len(self.buffer) >= MAX_FRAME:
                raise ValueError("Serial frame too large")
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.fd], [], [], remaining)[0]:
                raise TimeoutError("Serial read timed out")
            data = os.read(self.fd, min(1024, MAX_FRAME - len(self.buffer)))
            if not data:
                raise OSError("Serial disconnected")
            self.buffer.extend(data)
        line, _, rest = self.buffer.partition(b"\n")
        self.buffer = bytearray(rest)
        return bytes(line) + b"\n"

    def close(self):
        import termios
        if self.fd is not None:
            try:
                if self.original:
                    termios.tcsetattr(self.fd, termios.TCSANOW, self.original)
            except (OSError, termios.error):
                pass
            finally:
                os.close(self.fd)
                self.fd = None


class PySerialTransport:
    def __init__(self, port):
        try:
            import serial
        except ImportError as error:
            raise ValueError('Windows serial support requires: pip install ".[hardware]"') from error
        self.port = serial.Serial(port, 115200, timeout=2, write_timeout=2)

    def write(self, data, timeout):
        self.port.write_timeout = timeout
        if self.port.write(data) != len(data):
            raise OSError("Incomplete serial write")

    def readline(self, timeout):
        self.port.timeout = timeout
        data = self.port.read_until(b"\n", MAX_FRAME + 1)
        if not data:
            raise TimeoutError("Serial read timed out")
        return data

    def close(self):
        self.port.close()


class SerialDevice:
    def __init__(self, port=None, *, transport=None, timeout=2.0):
        number("timeout", timeout, positive=True)
        if timeout > 3:
            raise ValueError("Serial timeout must be <= 3 seconds")
        self.transport = transport or (PosixTransport(port) if os.name == "posix" else PySerialTransport(port))
        self.timeout = timeout
        self.request_id = 0

    def _request(self, op, **fields):
        self.request_id += 1
        request = {"v": 1, "id": self.request_id, "op": op, **fields}
        deadline = time.monotonic() + self.timeout
        self.transport.write(encode_frame(request), self.timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("No matching device response")
            response = decode_frame(self.transport.readline(remaining))
            if response["id"] != self.request_id:
                continue
            if response.get("ok") is not True:
                raise ValueError(f"Device rejected request: {response.get('error', 'unknown')}")
            return response

    def sample(self):
        return Reading.model_validate(self._request("sample")["sample"])

    def set_mode(self, mode):
        if mode not in MODES:
            raise ValueError("Unknown mode")
        response = self._request("set_mode", mode=mode)
        if response.get("mode") not in MODES:
            raise ValueError("Invalid acknowledged device mode")
        return response["mode"]

    def reset_fault(self):
        return self._request("reset_fault")

    def close(self):
        self.transport.close()
