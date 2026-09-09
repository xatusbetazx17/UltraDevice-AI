import csv
from pathlib import Path


def plot_csv(csv_path, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise ValueError('Plotting requires: pip install ".[plot]"') from error
    with open(csv_path, encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError("No telemetry to plot")
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    times = [float(r["t_min"]) + float(r["dt_min"]) for r in rows]
    outputs = []
    for suffix, column, label in (("soc", "soc", "State of charge (0–1)"),
                                  ("load", "load_w", "Delivered load (W)"),
                                  ("harvest", "harvest_w", "Raw harvest (W)")):
        fig, axis = plt.subplots()
        axis.plot(times, [float(r[column]) for r in rows])
        axis.set(xlabel="Interval end (minutes)", ylabel=label, title="UltraDevice simulation")
        fig.tight_layout()
        output = path.with_name(path.stem + "_" + suffix + ".png")
        fig.savefig(output)
        plt.close(fig)
        outputs.append(str(output))
    return outputs
