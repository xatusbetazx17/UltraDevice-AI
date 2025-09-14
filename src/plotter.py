from __future__ import annotations
import matplotlib.pyplot as plt
import csv

def plot_csv(csv_path: str, out_path: str):
    t, soc, load, harvest = [], [], [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            t.append(int(row["t_min"]))
            soc.append(float(row["soc"]))
            load.append(float(row["load_w"]))
            harvest.append(float(row["harvest_w"]))

    # SoC
    plt.figure()
    plt.plot(t, soc)
    plt.title("State of Charge")
    plt.xlabel("Time (min)"); plt.ylabel("SoC (0..1)")
    plt.tight_layout()
    plt.savefig(out_path.replace(".png","_soc.png"))
    plt.close()

    # Load
    plt.figure()
    plt.plot(t, load)
    plt.title("Load (W)")
    plt.xlabel("Time (min)"); plt.ylabel("Watts")
    plt.tight_layout()
    plt.savefig(out_path.replace(".png","_load.png"))
    plt.close()

    # Harvest
    plt.figure()
    plt.plot(t, harvest)
    plt.title("Harvest (W)")
    plt.xlabel("Time (min)"); plt.ylabel("Watts")
    plt.tight_layout()
    plt.savefig(out_path.replace(".png","_harvest.png"))
    plt.close()
