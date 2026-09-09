"""Deterministic desktop device and bounded real USB sessions."""
import time

from .ai import PolicyLearner
from .audit import AuditLog
from .battery import Battery
from .controller import DeviceController, Reading
from .thermal import ThermalModel
from .validation import number


class SimulatedDevice:
    def __init__(self):
        self.clock_s = 0.0
        self.seq = 0
        self.mode = "conserve"
        self.battery = Battery(2.0)
        self.energy_wh = 1.5
        self.thermal = ThermalModel()
        self.temp_c = 25.0
        self.closed = False

    def sample(self):
        self.seq += 1
        load = {"boost": 1.0, "normal": 0.4, "conserve": 0.2, "stealth": 0.1,
                "reserve": 0.05, "shutdown": 0.01, "fault": 0.01}[self.mode]
        return Reading(seq=self.seq, uptime_ms=int(self.clock_s * 1000), temp_c=self.temp_c,
                       temp_source="simulated", battery_soc=self.energy_wh / self.battery.capacity_wh,
                       load_w=load, harvest_w=0.02, device_mode=self.mode, sensor_ok=True)

    def advance(self, seconds):
        load = {"boost": 1.0, "normal": 0.4, "conserve": 0.2, "stealth": 0.1,
                "reserve": 0.05, "shutdown": 0.01, "fault": 0.01}[self.mode]
        self.energy_wh = self.battery.step_discharge(self.energy_wh, max(0, load - 0.02), seconds / 3600)
        self.temp_c = self.thermal.step(self.temp_c, load, seconds / 3600)
        self.clock_s += seconds

    def set_mode(self, mode):
        self.mode = mode
        return mode

    def close(self):
        self.closed = True


def run_session(device, seconds, out, *, requested="normal", config=None, realtime=True,
                schedule=None, target_hours=None, capacity_wh=None, clock=time.monotonic, sleep=time.sleep):
    """Run until duration, interrupt or failure. Every exit attempts LED shutdown."""
    log = None
    samples = 0
    modes = set()
    try:
        number("seconds", seconds, positive=True)
        if seconds > 86400:
            raise ValueError("Session duration is limited to 24 hours")
        if (target_hours is None) != (capacity_wh is None):
            raise ValueError("Predictive policy needs both target_hours and capacity_wh")
        if target_hours is not None:
            number("target_hours", target_hours, positive=True)
            number("capacity_wh", capacity_wh, positive=True)
        controller = DeviceController(config)
        learner = PolicyLearner()
        log = AuditLog(out)
        log.append("session", {"version": 1, "source": "usb" if realtime else "simulated",
                               "requested_seconds": seconds, "limits": controller.config.model_dump()})
        start = clock() if realtime else 0.0
        elapsed = 0.0
        while elapsed < seconds:
            before_sample = clock() if realtime else elapsed
            reading = device.sample()
            now = clock() if realtime else elapsed
            requested_mode = schedule(elapsed) if schedule else requested
            forecast = None
            if reading.load_w is not None and reading.harvest_w is not None:
                learner.update(reading.load_w, reading.harvest_w)
                if capacity_wh is not None and reading.battery_soc is not None:
                    forecast = learner.forecast(reading.battery_soc * capacity_wh)
                    remaining_target = max(0, target_hours - elapsed / 3600)
                    if forecast is not None and forecast < remaining_target and requested_mode == "normal":
                        requested_mode = "conserve"
            decision = controller.step(reading, now, requested_mode, received_s=before_sample)
            actual = device.set_mode(decision.mode)
            log.append("sample", {"elapsed_s": now - start, "reading": reading.model_dump(),
                                  "decision": decision.to_dict(), "acknowledged_mode": actual,
                                  "predicted_hours_ideal": forecast})
            modes.add(actual)
            samples += 1
            if actual in ("fault", "shutdown") or decision.mode == "fault":
                raise RuntimeError(f"Device stopped: {decision.reason}; firmware mode {actual}")
            period = min(decision.sample_period_s, seconds - elapsed)
            if realtime:
                sleep(max(0, period - (clock() - before_sample)))
                elapsed = clock() - start
            else:
                device.advance(period)
                elapsed += period
        log.append("complete", {"samples": samples})
        return {"samples": samples, "modes": sorted(modes), "log": str(out), "source": "usb" if realtime else "simulated"}
    except BaseException as error:
        if log:
            log.append("error", {"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        try:
            actual = device.set_mode("shutdown")
            if log:
                log.append("stop", {"acknowledged_mode": actual})
        except Exception as error:
            if log:
                log.append("stop_unconfirmed", {"error": str(error), "fallback": "firmware heartbeat timeout"})
        finally:
            device.close()
            if log:
                log.close()


def run_demo(seconds, out):
    def schedule(elapsed):
        if 65 <= elapsed < 80:
            return "boost"
        return "stealth" if elapsed >= 85 else "normal"
    return run_session(SimulatedDevice(), seconds, out, realtime=False, schedule=schedule)
