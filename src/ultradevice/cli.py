"""CLI uses the standard library; optional tools are imported on demand."""
import argparse
import json
import sys
from pathlib import Path

from .telemetry import write_csv, write_json


def parser():
    cli = argparse.ArgumentParser(prog="ultradevice", description="UltraDevice AI reference controller and power simulator")
    cli.add_argument("--version", action="version", version="ultradevice 0.3.0")
    commands = cli.add_subparsers(dest="command")

    def command(name, help_text, aliases=()):
        return commands.add_parser(name, help=help_text, aliases=list(aliases))

    def option(p, name, **kwargs):
        p.add_argument("--" + name.replace("_", "-"), dest=name, **kwargs)

    for name in ("runtime", "boost", "duty", "optimize", "size-battery"):
        p = command(name, "Calculate an engineering budget", ("size_battery",) if name == "size-battery" else ())
        if name != "size-battery":
            option(p, "battery_wh", type=float, required=True)
        if name in ("runtime", "size-battery"):
            option(p, "avg_load_w", type=float, required=True)
        if name == "runtime":
            for h in ("solar_w", "kinetic_w", "thermal_w"):
                option(p, h, type=float, default=0)
        if name == "boost":
            option(p, "burst_w", type=float, required=True)
            option(p, "burst_sec", type=float, required=True)
        if name in ("duty", "optimize", "size-battery"):
            option(p, "target_hours", type=float, required=True)
            option(p, "harvest_w", type=float, default=0)
        if name in ("duty", "optimize"):
            p.add_argument("--p-hi", "--P_hi", dest="p_hi", type=float, default=6)
            p.add_argument("--p-lo", "--P_lo", dest="p_lo", type=float, default=1.2)
        if name == "duty":
            option(p, "avg_load_w", type=float, help="Optional additional average-load ceiling")
        if name == "optimize":
            option(p, "out", default="outputs/optimized.json")
    for name in ("simulate", "simulate-physics", "validate-scenario"):
        p = command(name, "Run or validate a JSON scenario", (name.replace("-", "_"),) if "-" in name else ())
        option(p, "scenario", required=True)
        if name != "validate-scenario":
            option(p, "out", default="outputs/" + name + ".csv")
        if name == "simulate-physics":
            for flag, value in (("rth", 4), ("tlim", 42), ("derate_start", 39), ("v_nom", 3.7), ("r_int", 0.15), ("c_rate", 2)):
                option(p, flag, type=float, default=value)
    for name in ("plot", "report"):
        p = command(name, "Read simulation telemetry")
        option(p, "csv", required=True)
        option(p, "out", default="outputs/plot.png" if name == "plot" else "outputs/report.md")
    for name in ("profile", "randomize"):
        p = command(name, "Write a validated example scenario")
        option(p, "out", default="outputs/" + name + ".json")
        if name == "randomize":
            option(p, "seed", type=int, default=0)
    p = command("demo", "Run a deterministic virtual device; no hardware needed")
    option(p, "seconds", type=float, default=95)
    option(p, "out", default="outputs/demo.jsonl")
    p = command("device", "Connect to the Pico USB reference firmware")
    option(p, "port", required=True)
    option(p, "seconds", type=float, default=60)
    option(p, "out", default="outputs/device.jsonl")
    option(p, "mode", choices=("normal", "conserve", "stealth", "boost"), default="normal")
    option(p, "config")
    option(p, "target_hours", type=float)
    option(p, "battery_wh", type=float)
    option(p, "reset_fault", action="store_true")
    p = command("check-log", "Verify a local hash-linked telemetry log")
    option(p, "input", required=True)
    p = command("schema", "Export versioned JSON schemas")
    option(p, "kind", choices=("scenario", "controller", "reading"), default="scenario")
    option(p, "out", default="outputs/schema.json")
    command("doctor", "Check local installation and optional dependencies")
    return cli


def execute(args):
    command = args.command.replace("_", "-")
    if command == "runtime":
        from .models import PowerProfile
        from .power import ideal_runtime_hours
        profile = PowerProfile(battery_wh=args.battery_wh, avg_load_w=args.avg_load_w,
                               solar_w=args.solar_w, kinetic_w=args.kinetic_w, thermal_w=args.thermal_w)
        hours = ideal_runtime_hours(profile)
        print(f"Ideal runtime: {hours:.2f} hours" if hours != float("inf") else "No net discharge in this ideal constant-power model; not perpetual power.")
    elif command == "boost":
        from .power import reserve_boost
        print(f"Ideal remaining energy: {reserve_boost(args.battery_wh, args.burst_w, args.burst_sec):.6g} Wh")
    elif command in ("duty", "optimize"):
        from .optimizer import optimize_duty
        result = optimize_duty(args.target_hours, args.battery_wh, args.p_hi, args.p_lo, args.harvest_w)
        if command == "duty" and args.avg_load_w is not None:
            from .power import duty_fraction_for_target
            limit = duty_fraction_for_target(0, args.p_hi, args.p_lo, args.avg_load_w, 1)
            result["duty_fraction"] = min(result["duty_fraction"], limit)
            fraction = result["duty_fraction"]
            result["average_load_w"] = fraction * args.p_hi + (1 - fraction) * args.p_lo
            result["schedule"] = {str(h): fraction for h in range(24)}
        if command == "optimize":
            write_json(args.out, result)
        print(json.dumps(result, indent=2))
    elif command == "size-battery":
        from .sizing import size_pack
        print(json.dumps(size_pack(args.target_hours, args.avg_load_w, args.harvest_w)))
        print("Model minimum, excluding reserve, aging, enclosure, wiring and protection mass.")
    elif command in ("simulate", "simulate-physics", "validate-scenario"):
        from .config import load_scenario
        from .validate import validate_scenario
        scenario = load_scenario(args.scenario)
        errors = validate_scenario(scenario)
        if errors:
            raise ValueError("; ".join(errors))
        if command == "validate-scenario":
            print("Scenario and profiles are valid")
            return
        from .simulate import simulate, simulate_physics
        if command == "simulate-physics":
            from .battery import Battery
            from .thermal import ThermalModel
            battery = Battery(scenario.battery_wh, v_nom=args.v_nom, r_int=args.r_int, max_c_rate=args.c_rate)
            thermal = ThermalModel(r_th_c_per_w=args.rth, t_limit_c=args.tlim, derate_start_c=args.derate_start)
            rows = simulate_physics(scenario, battery, thermal)
        else:
            rows = simulate(scenario)
        write_csv(args.out, rows)
        print(f"Wrote {len(rows)} intervals to {args.out}")
    elif command == "plot":
        from .plotter import plot_csv
        print("\n".join(plot_csv(args.csv, args.out)))
    elif command == "report":
        from .report import summarize, write_markdown
        write_markdown(summarize(args.csv), args.out)
        print(f"Wrote {args.out}")
    elif command in ("profile", "randomize"):
        from .config import Scenario
        if command == "profile":
            scenario = Scenario(name="custom", battery_wh=2, base_load_w=0.05)
        else:
            from .randomize import random_scenario
            scenario = Scenario.model_validate(random_scenario(args.seed))
        write_json(args.out, scenario.model_dump())
        print(f"Wrote {args.out}")
    elif command == "demo":
        from .device import run_demo
        print(json.dumps(run_demo(args.seconds, args.out), indent=2))
    elif command == "device":
        from .controller import ControllerConfig
        from .device import run_session
        from .protocol import SerialDevice
        config = ControllerConfig.model_validate_json(Path(args.config).read_text()) if args.config else ControllerConfig()
        device = SerialDevice(args.port)
        if args.reset_fault:
            try:
                device.reset_fault()
            except Exception:
                device.close()
                raise
        print(json.dumps(run_session(device, args.seconds, args.out, requested=args.mode, config=config,
                                     target_hours=args.target_hours, capacity_wh=args.battery_wh), indent=2))
    elif command == "check-log":
        from .audit import verify_log
        print(json.dumps(verify_log(args.input), indent=2))
    elif command == "schema":
        from .config import Scenario
        from .controller import ControllerConfig, Reading
        model = {"scenario": Scenario, "controller": ControllerConfig, "reading": Reading}[args.kind]
        write_json(args.out, model.model_json_schema())
        print(f"Wrote {args.out}")
    elif command == "doctor":
        import importlib.util
        print(json.dumps({"python": sys.version.split()[0], "package": str(Path(__file__).parent),
                          "optional": {m: importlib.util.find_spec(m) is not None for m in ("matplotlib", "serial")},
                          "hardware_status": "unverified; use device with a physical board"}, indent=2))


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if not args.command:
        cli.print_help()
        return 0
    try:
        execute(args)
        return 0
    except KeyboardInterrupt:
        print("Stopped", file=sys.stderr)
        return 130
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def app():
    raise SystemExit(main())


if __name__ == "__main__":
    app()
