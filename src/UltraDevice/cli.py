import typer
from .models import PowerProfile
from .power import ideal_runtime_hours, reserve_boost, duty_fraction_for_target

app = typer.Typer(help="UltraDevice AI — tiny power & mode simulator")

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
        typer.echo("Net power <= 0 → runtime effectively indefinite (model).")
    else:
        typer.echo(f"Ideal runtime ≈ {t:.2f} hours")

@app.command()
def boost(
    battery_wh: float = typer.Option(..., help="Battery capacity (Wh)"),
    burst_w: float = typer.Option(..., help="Burst power draw (W)"),
    burst_sec: float = typer.Option(..., help="Burst duration (s)"),
):
    from .power import reserve_boost
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
    typer.echo(f"High-power duty fraction needed ≈ {100*f:.1f}% (heuristic)"

)

if __name__ == "__main__":
    app()
