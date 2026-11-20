"""Ptolemy's planetary latitudes (Almagest XIII), computed from his own tables in XIII.5.

Tables: data/ptolemy_latitude_tables.csv and data/ptolemy_latitude_interpolation.csv, Ptolemy's
values as transcribed in G. Van Brummelen, *Mathematical Tables in Ptolemy's Almagest* (PhD
thesis, Simon Fraser University, 1993), Tables 14.2-14.13. Positions of the northern limits and
the inclinations of the inferior planets' deferents: Almagest XIII.1-3 (Manitius 1912-13).

Superior planets (XIII.6): with n the argument of latitude counted from the northern limit and
a the true anomaly from the epicycle's true apogee,

    beta = g(n) * beta_north(a)   for cos n >= 0,   g(n) * beta_south(a) otherwise,

where g is the latitude interpolation table (about cos n, Moon's latitude / 5 deg). For Venus and
Mercury n is the true centrum and beta = beta1 + beta2 + beta3 (inclination, deviation, slant).
Latitudes in degrees, north positive.
"""

import csv
import math
from pathlib import Path

from src import almagest

ROOT = Path(__file__).resolve().parents[1]

NORTHERN_LIMIT = {"Saturn": 180.0, "Jupiter": 180.0, "Mars": 120.0}
INCLINATION = {"Venus": 10 / 60, "Mercury": -45 / 60}


def sexagesimal(text):
    whole, frac = text.split(";")
    return int(whole or 0) + sum(int(d) / 60 ** (i + 1) for i, d in enumerate(frac.split(",")))


def _load():
    with (ROOT / "data" / "ptolemy_latitude_tables.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tables = {k: [sexagesimal(r[k]) for r in rows] for k in rows[0] if k != "anomaly"}
    grid = [int(r["anomaly"]) for r in rows]
    with (ROOT / "data" / "ptolemy_latitude_interpolation.csv").open(encoding="utf-8") as f:
        g = [(int(r["n"]), sexagesimal(r["g"])) for r in csv.DictReader(f)]
    return grid, tables, [(90, 0.0), *g]


GRID, TABLES, G_TABLE = _load()


def _interp(xs, ys, x):
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def _fold(a):
    a = a % 360.0
    return 360.0 - a if a > 180.0 else a


def table(name, a):
    """Ptolemy's tabulated value at anomaly a (degrees), symmetric about 0 and 180."""
    ys = TABLES[name]
    first = 0.0 if name.endswith("slant") else ys[0]
    return _interp([0, *GRID], [first, *ys], _fold(a))


def g(n):
    """Signed interpolation fraction: +1 at the northern limit, -1 at the southern, 0 at nodes."""
    n = _fold(n)
    xs, ys = zip(*G_TABLE, strict=True)
    return _interp(xs, ys, 180.0 - n) if n < 90.0 else -_interp(xs, ys, n)


def superior_latitude(name, n, a):
    side = "north" if math.cos(math.radians(n)) >= 0 else "south"
    return g(n) * table(f"{name.lower()}_{side}", a)


def inferior_latitude(name, n, a):
    s = 1.0 if name == "Venus" else -1.0
    key = name.lower()
    beta1 = INCLINATION[name] * g(n) ** 2
    dev = table(f"{key}_deviation", a) * (1.0 if _fold(a) < 90.0 else -1.0)
    beta2 = -s * math.copysign(1.0, math.sin(math.radians(n))) * abs(g(n - 90.0)) * dev
    slant = table(f"{key}_slant", a) * math.copysign(1.0, math.sin(math.radians(a)))
    if name == "Mercury":
        slant *= 1.1 if math.cos(math.radians(n)) < 0 else 0.9
    return beta1 + beta2 + s * g(n) * slant


def _lon(p):
    return math.degrees(math.atan2(p[1], p[0])) % 360.0


def latitude(name, days):
    """Ptolemy's latitude of a planet at `days` after his epoch, in degrees north."""
    st = almagest.planet_state(name, days)
    centre = _lon(st.epi)
    true_anomaly = st.anomaly + st.apogee_dir - centre
    if name in NORTHERN_LIMIT:
        return superior_latitude(name, centre - NORTHERN_LIMIT[name], true_anomaly)
    apogee = almagest.PLANETS[name]["apogee0"] + almagest.APSIDAL_RATE * days
    return inferior_latitude(name, centre - apogee, true_anomaly)
