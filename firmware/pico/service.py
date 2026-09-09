"""Hardware-independent protocol handler shared by board and integration tests."""


class DeviceService:
    def __init__(self, policy, temp_source="die"):
        self.policy = policy
        self.temp_source = temp_source
        self.seq = 0

    def handle(self, request, now_ms, temp_c, sensor_ok, stop_pressed=False):
        request_id = 0
        try:
            if not isinstance(request, dict):
                raise ValueError("Expected object")
            request_id = request.get("id", -1)
            if type(request_id) is not int or not 0 <= request_id <= 2147483647:
                request_id = 0
                raise ValueError("Invalid id")
            if type(request.get("v")) is not int or request["v"] != 1:
                raise ValueError("Unsupported version")
            operation = request.get("op")
            response = {"v": 1, "id": request_id, "ok": True}
            self.policy.tick(now_ms, temp_c, sensor_ok, stop_pressed)
            if operation == "sample" and set(request) == {"v", "id", "op"}:
                self.seq += 1
                response["sample"] = {
                    "seq": self.seq, "uptime_ms": now_ms, "temp_c": temp_c,
                    "temp_source": self.temp_source,
                    "battery_soc": None, "load_w": None, "harvest_w": None,
                    "device_mode": self.policy.mode, "sensor_ok": sensor_ok,
                }
            elif operation == "set_mode" and set(request) == {"v", "id", "op", "mode"}:
                response["mode"] = self.policy.command(request["mode"], now_ms, temp_c, sensor_ok, stop_pressed)
            elif operation == "reset_fault" and set(request) == {"v", "id", "op"}:
                if not self.policy.reset(temp_c, sensor_ok):
                    raise ValueError("Reset requires a valid cool sensor")
            else:
                raise ValueError("Unknown operation or fields")
            return response
        except (ValueError, TypeError, KeyError) as error:
            return {"v": 1, "id": request_id, "ok": False, "error": str(error)}
