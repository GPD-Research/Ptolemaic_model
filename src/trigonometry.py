"""Ptolemy's trigonometry: the chord table (Almagest I.11) and Menelaus conversions (I.14-16).

Ptolemy had no sine. He worked with chords of a circle of radius 60 parts:
crd(a) = 120 sin(a/2), written in base 60. Mirrors viewer/sky.js.
"""

import math

# Almagest I.12: the arc between the tropics is 47;42,40 degrees, so the obliquity is 23;51,20.
OBLIQUITY = 23 + 51 / 60 + 20 / 3600


def chord(arc_deg):
    """Chord of an arc, in parts of a circle of radius 60."""
    return 120 * math.sin(math.radians(arc_deg) / 2)


def arc(chord_parts):
    """Arc (degrees) whose chord is chord_parts."""
    return 2 * math.degrees(math.asin(max(-1.0, min(1.0, chord_parts / 120))))


def to_sexagesimal(x, places=2):
    """Non-negative x as (whole, sixtieths, ...) with `places` base-60 places, rounded."""
    n = round(x * 60**places)
    digits = []
    for _ in range(places):
        n, r = divmod(n, 60)
        digits.append(r)
    return (n, *reversed(digits))


def chord_table():
    """Ptolemy's table, recomputed: arcs every 1/2 degree to 180 degrees.

    Each row is (arc, chord as parts;minutes,seconds, sixtieths as 0;minutes,seconds,thirds).
    The sixtieths column is 1/30 of the step to the next chord, for interpolating to one minute of
    arc. Ptolemy's printed values agree with these to within a few seconds.
    """
    rows = []
    for i in range(1, 361):
        a = i / 2
        step = (chord(a + 0.5) - chord(a)) / 30
        rows.append((a, to_sexagesimal(chord(a)), to_sexagesimal(step, 3)))
    return rows


def _quadrant(lon):
    lon %= 360
    return lon, (lon if lon <= 90 else 180 - lon if lon <= 270 else lon - 360)


def declination_of_ecliptic(lon, obliquity=OBLIQUITY):
    """Declination of the ecliptic point at longitude lon, Ptolemy's way (I.14).

    Menelaus's theorem on the sphere gives crd(2 delta) = crd(2 eps) crd(2 lambda) / 120,
    which is sin(delta) = sin(eps) sin(lambda) in modern notation.
    """
    lon, q = _quadrant(lon)
    c = chord(2 * obliquity) * chord(2 * abs(q)) / 120
    return math.copysign(arc(c) / 2, q)


def right_ascension_of_ecliptic(lon, obliquity=OBLIQUITY):
    """Right ascension of the ecliptic point at longitude lon (I.16), from chords only.

    crd(2 alpha) = 120 crd(2 delta) crd(180 - 2 eps) / (crd(180 - 2 delta) crd(2 eps)),
    that is sin(alpha) = tan(delta) / tan(eps).
    """
    lon, q = _quadrant(lon)
    d = abs(declination_of_ecliptic(q, obliquity))
    c = (
        120
        * chord(2 * d)
        * chord(180 - 2 * obliquity)
        / (chord(180 - 2 * d) * chord(2 * obliquity))
    )
    a0 = arc(c) / 2
    if lon <= 90:
        return a0
    if lon <= 180:
        return 180 - a0
    if lon <= 270:
        return 180 + a0
    return 360 - a0


def ecliptic_to_equatorial(lon, lat, obliquity=OBLIQUITY):
    """(right ascension, declination) in degrees of a star at ecliptic (lon, lat)."""
    lam, beta, eps = (math.radians(v) for v in (lon, lat, obliquity))
    dec = math.asin(math.sin(beta) * math.cos(eps) + math.cos(beta) * math.sin(eps) * math.sin(lam))
    ra = math.atan2(math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps), math.cos(lam))
    return math.degrees(ra) % 360, math.degrees(dec)
