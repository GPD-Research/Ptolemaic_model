"""Ptolemy's sizes and distances from Planetary Hypotheses I."""

import csv
from fractions import Fraction
from pathlib import Path

ROWS = list(
    csv.DictReader(
        (Path(__file__).resolve().parents[1] / "data" / "ptolemy_planetary_hypotheses.csv").open(
            encoding="utf-8"
        )
    )
)


def parse(text):
    """'4 1/3 + 1/20' -> 4.3833..."""
    return float(sum(Fraction(t) for t in text.replace("+", " ").split()))


def test_spheres_nest_without_gaps_except_venus_to_sun():
    for below, above in zip(ROWS[1:], ROWS[2:], strict=False):
        least, top = int(above["least_distance"]), int(below["greatest_distance"])
        if above["body"] == "Sun":
            assert (top, least) == (1079, 1160)
        else:
            assert least == top, above["body"]


def test_decimal_diameters_match_fractions():
    for r in ROWS:
        assert abs(parse(r["diameter"]) - float(r["diameter_decimal"])) < 5e-4, r["body"]


def test_size_order():
    d = {r["body"]: float(r["diameter_decimal"]) for r in ROWS}
    assert d["Sun"] > d["Saturn"] > d["Jupiter"] > d["Mars"] > d["Earth"]
    assert d["Earth"] > d["Venus"] > d["Moon"] > d["Mercury"]
