import typer
from .models import PowerProfile
from .power import ideal_runtime_hours, reserve_boost, duty_fraction_for_target

app = typer.Typer(help="UltraDevice AI — power & mode simulator")

@app.command()
def runtime(
    battery_wh: float = typer.Option(..., help="Battery capacity (Wh)"),
    avg_load_w: float = typer.Option(..., help="Average load (W)"),
    solar_w: float = typer.Option(0.0, help="Solar harvest (W)"),
    kinetic_w: float = typer.Option(0.0, help="Kinetic harvest (W)"),
    thermal_w: float = typer.Option(0.0, help="Thermal harvest (W)"),
):
    profile = PowerProfile(
        battery_wh=battery_wh,
        avg_load_w=avg_load_w,
        solar_w=solar_w,
        kinetic_w=kinetic_w,
        thermal_w=thermal_w,
    )
    t = ideal_runtime_hours(profile)
    if t == float('inf'):
        typer.echo("Net power <= 0 → runtime effectively indefinite (idealized model).")
    else:
        typer.echo(f"Ideal runtime ≈ {t:.2f} hours")

@app.command()
def boost(
    battery_wh: float = typer.Option(..., help="Battery capacity (Wh)"),
    burst_w: float = typer.Option(..., help="Burst power draw (W)"),
    burst_sec: float = typer.Option(..., help="Burst duration (s)"),
):
    remaining = reserve_boost(battery_wh, burst_w, burst_sec)
    typer.echo(f"Remaining battery after burst ≈ {remaining:.2f} Wh (idealized)")

@app.command()
def duty(
    battery_wh: float = typer.Option(..., help="Battery capacity (Wh)"),
    avg_load_w: float = typer.Option(..., help="Average load target (W)"),
    target_hours: float = typer.Option(..., help="Desired runtime (hours)"),
    P_hi: float = typer.Option(6.0, help="High-power mode draw (W)"),
    P_lo: float = typer.Option(1.2, help="Low-power mode draw (W)"),
    harvest_w: float = typer.Option(0.5, help="Average harvest (W)"),
):
    f = duty_fraction_for_target(battery_wh, P_hi, P_lo, harvest_w, target_hours)
    typer.echo(f"High-power duty fraction needed ≈ {100*f:.1f}% (heuristic)")

@app.command()
def simulate(
    scenario: str = typer.Option(..., help="Path to scenario JSON"),
    out: str = typer.Option("outputs/sim.csv", help="Output CSV path"),
):
    import json, os
    from .config import Scenario
    from .simulate import simulate as run_sim
    from .telemetry import write_csv
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(scenario, "r", encoding="utf-8") as f:
        scn = Scenario.model_validate_json(f.read())
    rows = run_sim(scn)
    write_csv(out, rows)
    typer.echo(f"Wrote {len(rows)} rows to {out}")

@app.command()
def plot(
    csv: str = typer.Option(..., help="CSV produced by simulate"),
    out: str = typer.Option("outputs/plot.png", help="Base PNG path"),
):
    import os
    from .plotter import plot_csv
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plot_csv(csv, out)
    typer.echo(f"Plots saved near {out}")

if __name__ == "__main__":
    app()


@app.command()
def optimize(
    battery_wh: float = typer.Option(..., help="Battery capacity (Wh)"),
    P_hi: float = typer.Option(6.0, help="High-power draw (W)"),
    P_lo: float = typer.Option(1.2, help="Low-power draw (W)"),
    harvest_w: float = typer.Option(0.5, help="Average harvest (W)"),
    target_hours: float = typer.Option(..., help="Target runtime (hours)"),
    out: str = typer.Option("outputs/optimized.json", help="Where to write schedule JSON")
):
    import json, os
    from .optimizer import optimize_duty
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = optimize_duty(target_hours, battery_wh, P_hi, P_lo, harvest_w)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    typer.echo(f"Suggested duty fraction ≈ {res['duty_fraction']:.3f}. Schedule saved to {out}.")

@app.command()
def report(
    csv: str = typer.Option(..., help="CSV produced by simulate"),
    out: str = typer.Option("outputs/report.md", help="Markdown report"),
):
    import os
    from .report import summarize, write_markdown
    os.makedirs(os.path.dirname(out), exist_ok=True)
    s = summarize(csv)
    write_markdown(s, out)
    typer.echo(f"Wrote report to {out}")

@app.command()
def profile(
    out: str = typer.Option("examples/scenarios/custom.json", help="Path to write a scenario skeleton"),
):
    import json, os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    skel = {
        "name": "custom",
        "battery_wh": 12.0,
        "base_load_w": 1.0,
        "features": {"radio": {"on": True, "w": 0.5}, "ui": {"on": True, "w": 0.4}},
        "harvest": {"solar": {"scale": 0.001, "irradiance_csv": "data/sky_irradiance_clear.csv"}},
        "boosts": [],
        "dt_minutes": 5
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(skel, f, indent=2)
    typer.echo(f"Wrote scenario skeleton to {out}")

@app.command()
def simulate_physics(
    scenario: str = typer.Option(..., help="Path to scenario JSON"),
    out: str = typer.Option("outputs/sim_physics.csv", help="Output CSV path"),
    rth: float = typer.Option(4.0, help="Thermal resistance C/W"),
    tlim: float = typer.Option(42.0, help="Thermal limit C"),
    derate_start: float = typer.Option(39.0, help="Thermal derate start C"),
    v_nom: float = typer.Option(3.7, help="Battery nominal voltage"),
    r_int: float = typer.Option(0.15, help="Battery internal resistance"),
    c_rate: float = typer.Option(2.0, help="Max C-rate"),
):
    import json, os
    from .config import Scenario
    from .simulate import simulate_physics as run_phys
    from .telemetry import write_csv
    from .battery import Battery
    from .thermal import ThermalModel
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(scenario, "r", encoding="utf-8") as f:
        scn = Scenario.model_validate_json(f.read())
    bat = Battery(capacity_wh=scn.battery_wh, v_nom=v_nom, r_int=r_int, max_c_rate=c_rate)
    th = ThermalModel(r_th_c_per_w=rth, t_limit_c=tlim, derate_start_c=derate_start)
    rows = run_phys(scn, bat, th)
    write_csv(out, rows)
    typer.echo(f"Wrote {len(rows)} rows to {out} with thermal+battery modeling")


@app.command()
def size_battery(
    target_hours: float = typer.Option(..., help="Target runtime (hours)"),
    avg_load_w: float = typer.Option(..., help="Average load (W)"),
    harvest_w: float = typer.Option(0.0, help="Average harvest (W)")
):
    from .sizing import size_pack
    res = size_pack(target_hours, avg_load_w, harvest_w)
    typer.echo(f"Required battery ≈ {res['battery_wh']} Wh (~{res['approx_mass_kg']} kg at 240 Wh/kg)")

@app.command()
def validate_scenario(
    scenario: str = typer.Option(..., help="Path to scenario JSON"),
):
    import json
    from .config import Scenario
    from .validate import validate_scenario as _validate
    with open(scenario, "r", encoding="utf-8") as f:
        scn = Scenario.model_validate_json(f.read())
    errs = _validate(scn)
    if errs:
        for e in errs: typer.echo(f"- {e}")
        raise typer.Exit(code=1)
    typer.echo("Scenario looks valid ✔")

@app.command()
def randomize(
    out: str = typer.Option("examples/scenarios/random_day.json", help="Output scenario path"),
    seed: int = typer.Option(0, help="Random seed"),
):
    import json, os
    from .randomize import random_scenario
    os.makedirs(os.path.dirname(out), exist_ok=True)
    scn = random_scenario(seed)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(scn, f, indent=2)
    typer.echo(f"Wrote randomized scenario to {out}")
