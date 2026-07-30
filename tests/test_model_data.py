import csv
from pathlib import Path

import numpy as np

from src.astronomy import calculate_illumination_phase, detect_retrograde_motion
from src.core import calculate_epicycle_path
from src.metrics import calculate_chi_squared, mean_absolute_angular_error


def load_observation_rows():
    data_path = Path(__file__).resolve().parents[1] / "data" / "almagest_planetary_logs.csv"
    with data_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_retrograde_motion_is_detected_in_dataset():
    rows = load_observation_rows()
    times = np.array([float(row["days_from_epoch"]) for row in rows])
    longitudes = np.array([float(row["ecliptic_longitude_deg"]) for row in rows])

    retrograde_times = detect_retrograde_motion(times, longitudes)

    assert len(retrograde_times) > 0


def test_metrics_are_zero_when_predictions_match_observations():
    rows = load_observation_rows()
    longitudes = np.array([float(row["ecliptic_longitude_deg"]) for row in rows])
    errors = np.ones(len(longitudes)) * 0.016

    assert np.isclose(mean_absolute_angular_error(longitudes, longitudes), 0.0)
    assert np.isclose(calculate_chi_squared(longitudes, longitudes, errors), 0.0)


def test_venus_phase_is_restricted_in_ptolemaic_geometry():
    t_array = np.linspace(0.0, 2.0 * np.pi, 8)
    x, y = calculate_epicycle_path(
        t_array,
        R=2.0,
        r=0.6,
        omega_d=1.0,
        omega_e=2.0,
    )

    phases = calculate_illumination_phase(x, y)

    assert np.all(phases >= 0.0)
    assert np.all(phases <= 1.0)
    assert np.any(phases < 0.5)
    assert np.any(phases > 0.5)
