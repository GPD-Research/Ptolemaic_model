import json
import shutil
import subprocess
import sys

import pytest

from src import latitudes

PLANETS = ["Saturn", "Jupiter", "Mars", "Venus", "Mercury"]


def test_tables_have_ptolemys_grid():
    assert latitudes.GRID == [*range(6, 91, 6), *range(93, 181, 3)]
    assert all(len(v) == 45 for v in latitudes.TABLES.values())
    assert latitudes.TABLES["mars_south"][-1] == pytest.approx(7 + 7 / 60)
    assert latitudes.TABLES["venus_deviation"][-1] == pytest.approx(6 + 22 / 60)


def test_interpolation_fraction_follows_cosine():
    assert latitudes.g(0) == 1 and latitudes.g(180) == -1 and latitudes.g(90) == 0
    for n in range(0, 360, 15):
        cos_n = latitudes.math.cos(latitudes.math.radians(n))
        assert latitudes.g(n) == pytest.approx(cos_n, abs=0.01)


def test_superior_planets_at_their_limits():
    # Mars at its northern limit, on the epicycle's perigee: 4;21 N; southern limit: 7;7 S.
    assert latitudes.superior_latitude("Mars", 0, 180) == pytest.approx(4 + 21 / 60)
    assert latitudes.superior_latitude("Mars", 180, 180) == pytest.approx(-(7 + 7 / 60))
    assert latitudes.superior_latitude("Saturn", 90, 77) == pytest.approx(0, abs=1e-12)


def test_venus_and_mercury_follow_xiii_3():
    # At the node after apogee Venus's epicycle perigee tilts up: 6;22 N (Manitius XIII.3).
    assert latitudes.inferior_latitude("Venus", 90, 180) == pytest.approx(6 + 22 / 60)
    # At apogee and perigee of the epicycle, on the apsidal line: only the deferent's tilt.
    assert latitudes.inferior_latitude("Venus", 0, 0) == pytest.approx(10 / 60)
    assert latitudes.inferior_latitude("Mercury", 180, 180) == pytest.approx(-45 / 60)


@pytest.mark.parametrize("name", PLANETS)
def test_latitudes_stay_within_ptolemys_range(name):
    values = [latitudes.latitude(name, d) for d in range(0, 365 * 60, 7)]
    limit = {"Saturn": 3.1, "Jupiter": 2.2, "Mars": 7.2, "Venus": 6.5, "Mercury": 4.2}[name]
    assert max(map(abs, values)) <= limit
    assert min(values) < 0 < max(values)


def test_javascript_mirror_matches_python():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    days = [0, 1000, 12345.6, 54321, -30000, 690000]
    script = (
        "const L = require('./viewer/latitudes.js');"
        f"console.log(JSON.stringify({json.dumps(PLANETS)}.map(p => "
        f"{json.dumps(days)}.map(d => L.latitude(p, d)))));"
    )
    out = subprocess.run([node, "-e", script], capture_output=True, text=True, check=True).stdout
    for name, row in zip(PLANETS, json.loads(out), strict=True):
        for d, v in zip(days, row, strict=True):
            assert v == pytest.approx(latitudes.latitude(name, d), abs=1e-9)


def test_generated_tables_js_is_fresh():
    subprocess.run([sys.executable, "tools/build_tables_js.py", "--check"], check=True)
