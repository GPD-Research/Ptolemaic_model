import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_observations(path: str | None = None):
    data_path = Path(path or "data/almagest_planetary_logs.csv")
    with data_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot_longitudes(observations, output_path: str | None = None):
    times = np.array([float(row["days_from_epoch"]) for row in observations])
    longitudes = np.array([float(row["ecliptic_longitude_deg"]) for row in observations])

    plt.figure(figsize=(8, 4.5))
    plt.plot(times, longitudes, marker="o", linestyle="-", color="tab:blue")
    plt.title("Mars apparent ecliptic longitude")
    plt.xlabel("Days from epoch")
    plt.ylabel("Longitude (degrees)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=200)
    else:
        plt.show()


def plot_orbit_geometry(observations, output_path: str | None = None):
    times = np.array([float(row["days_from_epoch"]) for row in observations])
    longitudes = np.array([float(row["ecliptic_longitude_deg"]) for row in observations])

    plt.figure(figsize=(8, 4.5))
    plt.plot(times, longitudes, marker="s", linestyle="--", color="tab:orange")
    plt.title("Retrograde loop geometry")
    plt.xlabel("Days from epoch")
    plt.ylabel("Longitude (degrees)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=200)
    else:
        plt.show()


if __name__ == "__main__":
    observations = load_observations()
    plot_longitudes(observations, output_path="plots/mars_longitudes.png")
    plot_orbit_geometry(observations, output_path="plots/mars_retrograde_geometry.png")
