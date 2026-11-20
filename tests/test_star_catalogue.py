import json
import math
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from src import precession, star_catalogue, trigonometry

ROOT = Path(__file__).resolve().parents[1]
STARS = star_catalogue.load()


def by(cst, index):
    return next(s for s in STARS if s.constellation == cst and s.index == index)


def test_chord_table_matches_ptolemys_values():
    table = {a: (c, s) for a, c, s in trigonometry.chord_table()}
    assert len(table) == 360
    assert table[0.5] == ((0, 31, 25), (0, 1, 2, 50))
    assert table[1.0][0] == (1, 2, 50)
    assert table[60.0] == ((60, 0, 0), (0, 0, 54, 21))
    assert table[90.0][0] == (84, 51, 10)
    assert table[120.0][0] == (103, 55, 23)
    assert table[180.0][0] == (120, 0, 0)
    assert table[180.0][1] == (0, 0, 0, 0)
    assert all(min(step) >= 0 for _, step in table.values())


def test_zero_obliquity_leaves_longitude_unchanged():
    for lon in (0, 30, 135, 250, 359):
        assert trigonometry.right_ascension_of_ecliptic(lon, 0) == pytest.approx(lon)
        assert trigonometry.declination_of_ecliptic(lon, 0) == pytest.approx(0)


def test_obliquity_is_half_the_arc_between_the_tropics():
    assert 2 * trigonometry.OBLIQUITY == pytest.approx(47 + 42 / 60 + 40 / 3600)


@pytest.mark.parametrize("lon", [0, 12.5, 30, 60, 90, 133, 180, 222, 270, 301, 359])
def test_menelaus_chords_give_the_modern_formulas(lon):
    ra, dec = trigonometry.ecliptic_to_equatorial(lon, 0)
    assert trigonometry.declination_of_ecliptic(lon) == pytest.approx(dec, abs=1e-9)
    assert trigonometry.right_ascension_of_ecliptic(lon) == pytest.approx(ra, abs=1e-9)


def test_ecliptic_pole_and_equinox():
    assert trigonometry.ecliptic_to_equatorial(0, 0) == pytest.approx((0, 0), abs=1e-9)
    ra, dec = trigonometry.ecliptic_to_equatorial(90, 90)
    assert dec == pytest.approx(90 - trigonometry.OBLIQUITY)
    assert ra == pytest.approx(270)


def test_catalogue_shape():
    assert len(STARS) == 1028
    assert [s.number for s in STARS] == list(range(1, 1029))
    assert len({s.constellation for s in STARS}) == 48 == len(star_catalogue.CONSTELLATIONS)
    assert all(0 <= s.lon < 360 and -90 <= s.lat <= 90 for s in STARS)
    mags = Counter(s.magnitude for s in STARS)
    assert mags[7] == 12 and mags[9] == 5  # "faint" and "nebulous"
    assert sum(1 for s in STARS if not s.hip) == 4


def test_famous_stars_in_ptolemys_notation():
    regulus, spica, sirius = by("Leo", 8), by("Vir", 14), by("CMa", 1)
    assert regulus.sign == ("Leo", 2, 30) and regulus.lat == pytest.approx(1 / 6)
    assert spica.sign == ("Virgo", 26, 40) and spica.lat == pytest.approx(-2)
    assert sirius.sign == ("Gemini", 17, 40) and sirius.lat == pytest.approx(-(39 + 1 / 6))
    assert regulus.magnitude == spica.magnitude == sirius.magnitude == 1


def test_positions_are_good_to_about_half_a_degree():
    assert 25 < star_catalogue.median_error(STARS) < 40


def test_precession_rates():
    year = 365
    assert precession.ptolemy_shift(precession.CATALOGUE_DAYS + 100 * year) == pytest.approx(1)
    assert 265 * year * precession.PTOLEMY_RATE == pytest.approx(2.65)
    real = precession.true_shift(precession.CATALOGUE_DAYS + 72 * 365.25)
    assert real == pytest.approx(1, abs=0.02)  # about 1 degree in 72 years


def test_catalogue_is_a_degree_behind_the_sky_of_ad_137():
    assert precession.catalogue_error_at_epoch() == pytest.approx(1.0, abs=0.05)


def test_ptolemy_falls_further_behind_with_time():
    spica = by("Vir", 14)
    today = 2461000.5 - precession.EPOCH_JD
    lag = precession.star_longitude(spica.lon, today, "true") - precession.star_longitude(
        spica.lon, today, "ptolemy"
    )
    assert 7 < lag < 10


def test_stars_js_is_current():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_star_catalogue

    assert (ROOT / "viewer" / "stars.js").read_text(
        encoding="utf-8"
    ) == build_star_catalogue.render_js(build_star_catalogue.read_csv())


def test_js_matches_python():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    days = [0.0, 200000.0, precession.CATALOGUE_DAYS, 1013000.5]
    lons = [0, 47.3, 133.0, 222.2, 301.9]
    script = f"""
      const S = require({json.dumps(str(ROOT / "viewer" / "sky.js"))});
      const rows = require({json.dumps(str(ROOT / "viewer" / "stars.js"))});
      const days = {json.dumps(days)}, lons = {json.dumps(lons)};
      console.log(JSON.stringify({{
        chords: lons.map(S.chord), sexa: lons.map((l) => S.toSexagesimal(S.chord(l))),
        dec: lons.map((l) => S.declinationOfEcliptic(l)),
        ra: lons.map((l) => S.rightAscensionOfEcliptic(l)),
        eq: lons.map((l) => S.eclipticToEquatorial(l, 20 - l / 10)),
        ptol: days.map((d) => S.starLongitude(100, d, "ptolemy")),
        tru: days.map((d) => S.starLongitude(100, d, "true")),
        obl: days.map((d) => S.trueObliquity(d)),
        n: rows.length, first: rows[0],
      }}));
    """
    js = json.loads(
        subprocess.run([node, "-e", script], capture_output=True, text=True, check=True).stdout
    )
    t, p = trigonometry, precession
    assert js["chords"] == pytest.approx([t.chord(v) for v in lons])
    assert [tuple(x) for x in js["sexa"]] == [t.to_sexagesimal(t.chord(v)) for v in lons]
    assert js["dec"] == pytest.approx([t.declination_of_ecliptic(v) for v in lons])
    assert js["ra"] == pytest.approx([t.right_ascension_of_ecliptic(v) for v in lons])
    for got, v in zip(js["eq"], lons):
        assert got == pytest.approx(list(t.ecliptic_to_equatorial(v, 20 - v / 10)))
    assert js["ptol"] == pytest.approx([p.star_longitude(100, d) for d in days])
    assert js["tru"] == pytest.approx([p.star_longitude(100, d, "true") for d in days])
    assert js["obl"] == pytest.approx([p.true_obliquity(d) for d in days])
    first = STARS[0]
    assert js["n"] == len(STARS)
    assert js["first"][3] / 60 == pytest.approx(first.lon) and js["first"][4] / 60 == pytest.approx(
        first.lat
    )
    assert math.isclose(js["first"][7], first.hip)


def test_true_obliquity():
    j2000 = 2451545.0 - precession.EPOCH_JD
    assert precession.true_obliquity(j2000) == pytest.approx(23.4393, abs=1e-4)
    assert precession.true_obliquity(precession.CATALOGUE_DAYS) == pytest.approx(23.68, abs=0.01)
