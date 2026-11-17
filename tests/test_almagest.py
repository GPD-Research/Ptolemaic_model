import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

from src import almagest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DAYS = [0.0, 12345.6, 320000.25, 1012345.0, 1013000.5]


def wrap(deg):
    return (deg + 180.0) % 360.0 - 180.0


def direction(frm, to):
    return math.degrees(math.atan2(to[1] - frm[1], to[0] - frm[0]))


def test_sexagesimal_conversion():
    assert almagest.sexa(2, 30) == pytest.approx(2.5)
    assert almagest.sexa(0, 59, 8, 17, 13, 12, 31) == pytest.approx(0.9856353, abs=1e-7)


@pytest.mark.parametrize("name", ["Mars", "Jupiter", "Saturn"])
def test_outer_epicycle_radius_stays_parallel_to_mean_sun(name):
    for days in SAMPLE_DAYS:
        s = almagest.planet_state(name, days)
        assert wrap(direction(s.epi, s.pos) - almagest.mean_sun(days)) == pytest.approx(
            0.0, abs=1e-9
        )


@pytest.mark.parametrize("name", ["Mercury", "Venus"])
def test_inner_epicycle_centre_follows_mean_sun_from_equant(name):
    for days in SAMPLE_DAYS:
        s = almagest.planet_state(name, days)
        assert wrap(direction(s.equant, s.epi) - almagest.mean_sun(days)) == pytest.approx(
            0.0, abs=1e-9
        )


def test_epicycle_centres_lie_on_their_deferents():
    for days in SAMPLE_DAYS:
        for name, s in almagest.state(days).items():
            if s.epi is None:
                continue
            radius = almagest.MOON["R"] if name == "Moon" else almagest.PLANETS[name]["R"]
            assert math.dist(s.center, s.epi) == pytest.approx(radius, abs=1e-9)


def test_moon_epicycle_reaches_perigee_at_quadrature():
    distances = []
    for days in [d * 0.05 for d in range(0, 600)]:
        s = almagest.moon_state(days)
        distances.append((math.hypot(*s.epi), wrap(s.mean_lon - almagest.mean_sun(days))))
    nearest = min(distances)
    farthest = max(distances)
    assert nearest[0] == pytest.approx(60 - 2 * almagest.MOON["e"], abs=0.01)
    assert abs(abs(nearest[1]) - 90) < 1.0
    assert farthest[0] == pytest.approx(60.0, abs=0.01)
    assert abs(farthest[1]) < 1.0 or abs(abs(farthest[1]) - 180) < 1.0


def test_mercury_deferent_has_two_perigees_near_120_degrees():
    p = almagest.PLANETS["Mercury"]
    apogee = p["apogee0"]
    samples = []
    for k in range(3600):
        mean_lon = apogee + k * 0.1
        days = (mean_lon - almagest.SUN["mean_lon0"]) / almagest.SUN["mean_lon_rate"]
        s = almagest.planet_state("Mercury", days)
        samples.append((math.hypot(*s.epi), wrap(s.mean_lon - apogee)))
    dist = [d for d, _ in samples]
    minima = [
        samples[i][1]
        for i in range(1, len(samples) - 1)
        if dist[i] < dist[i - 1] and dist[i] < dist[i + 1]
    ]
    assert len(minima) == 2
    assert all(abs(abs(m) - 120) < 2 for m in minima)


def test_mars_retrogrades_for_about_ten_weeks_at_opposition():
    days = [800000 + d for d in range(0, 800)]
    motion = [almagest.daily_motion("Mars", d) for d in days]
    retro = [d for d, m in zip(days, motion) if m < 0]
    assert 60 <= len(retro) <= 85
    assert retro[-1] - retro[0] == len(retro) - 1
    middle = retro[len(retro) // 2]
    elongation = wrap(almagest.planet_state("Mars", middle).lon - almagest.mean_sun(middle))
    assert abs(abs(elongation) - 180) < 10


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_viewer_kinematics_match_python():
    script = (
        "const P = require(process.argv[1]);"
        "const days = JSON.parse(process.argv[2]);"
        "console.log(JSON.stringify(days.map(d => P.state(d).map(s => [s.name, s.pos, s.lon]))));"
    )
    out = subprocess.run(
        ["node", "-e", script, str(ROOT / "viewer" / "ptolemy.js"), json.dumps(SAMPLE_DAYS)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for days, bodies in zip(SAMPLE_DAYS, json.loads(out)):
        for name, pos, lon in bodies:
            s = almagest.body_state(name, days)
            assert pos == pytest.approx(list(s.pos), abs=1e-6)
            assert wrap(lon - s.lon) == pytest.approx(0.0, abs=1e-6)
