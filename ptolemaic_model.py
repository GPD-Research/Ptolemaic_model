from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import csv
from pathlib import Path
from typing import Iterable


EPOCH = date(2000, 1, 1)


@dataclass(frozen=True)
class Observation:
    body: str
    observation_date: date
    observed_longitude_deg: float


PTOLEMAIC_PARAMETERS = {
    "mars": {"period_days": 686.98, "epoch_longitude_deg": 120.0},
    "venus": {"period_days": 224.70, "epoch_longitude_deg": 75.0},
    "jupiter": {"period_days": 4332.59, "epoch_longitude_deg": 200.0},
}


def normalize_angle(degrees: float) -> float:
    return degrees % 360.0


def angular_error_deg(predicted: float, observed: float) -> float:
    delta = (predicted - observed + 180.0) % 360.0 - 180.0
    return abs(delta)


def predict_geocentric_longitude_deg(body: str, observation_date: date) -> float:
    params = PTOLEMAIC_PARAMETERS[body.lower()]
    days_since_epoch = (observation_date - EPOCH).days
    raw_longitude = (
        params["epoch_longitude_deg"]
        + (360.0 * days_since_epoch / params["period_days"])
    )
    return normalize_angle(raw_longitude)


def load_reference_observations(csv_path: str | Path) -> list[Observation]:
    observations: list[Observation] = []
    with Path(csv_path).open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            observations.append(
                Observation(
                    body=row["body"].strip().lower(),
                    observation_date=date.fromisoformat(row["observation_date"]),
                    observed_longitude_deg=float(row["observed_longitude_deg"]),
                )
            )
    return observations


def evaluate_model_errors(observations: Iterable[Observation]) -> list[float]:
    return [
        angular_error_deg(
            predict_geocentric_longitude_deg(obs.body, obs.observation_date),
            obs.observed_longitude_deg,
        )
        for obs in observations
    ]
