"""Ptolemaic kinematics with the Almagest parameters (Toomer's translation).

Lengths are in parts (deferent radius = 60), angles are tropical longitudes in
degrees counted eastward, and time is days from the Nabonassar epoch
(-746 Feb 26, noon at Alexandria). Mirrors viewer/ptolemy.js, which drives the
animated viewer in viewer/index.html.
"""

import math
from dataclasses import dataclass


def sexa(*digits):
    """Sexagesimal digits (degrees; minutes, seconds, ...) to decimal degrees."""
    return sum(v / 60**i for i, v in enumerate(digits))


EPOCH_JD = 1448638.0 - 29.9 / 360
APSIDAL_RATE = 1 / 36500

SUN = dict(
    R=60.0,
    e=sexa(2, 30),
    apogee0=sexa(65, 30),
    mean_lon0=sexa(330, 45),
    mean_lon_rate=sexa(0, 59, 8, 17, 13, 12, 31),
)

MOON = dict(
    R=sexa(49, 41),
    e=sexa(10, 19),
    r=sexa(5, 15),
    mean_lon0=sexa(41, 22),
    mean_lon_rate=sexa(13, 10, 34, 58, 33, 30, 30),
    anomaly0=sexa(268, 49),
    anomaly_rate=sexa(13, 3, 53, 56, 17, 51, 59),
)

PLANETS = {
    "Mercury": dict(
        kind="mercury",
        R=60.0,
        e=3.0,
        r=sexa(22, 30),
        apogee0=sexa(181, 10),
        anomaly0=sexa(21, 55),
        anomaly_rate=sexa(3, 6, 24, 6, 59, 35, 50),
    ),
    "Venus": dict(
        kind="inner",
        R=60.0,
        e=sexa(1, 15),
        r=sexa(43, 10),
        apogee0=sexa(46, 10),
        anomaly0=sexa(71, 7),
        anomaly_rate=sexa(0, 36, 59, 25, 53, 11, 28),
    ),
    "Mars": dict(
        kind="outer",
        R=60.0,
        e=6.0,
        r=sexa(39, 30),
        apogee0=sexa(106, 40),
        mean_lon0=sexa(3, 32),
        mean_lon_rate=sexa(0, 31, 26, 36, 53, 51, 33),
    ),
    "Jupiter": dict(
        kind="outer",
        R=60.0,
        e=sexa(2, 45),
        r=sexa(11, 30),
        apogee0=sexa(152, 9),
        mean_lon0=sexa(184, 41),
        mean_lon_rate=sexa(0, 4, 59, 14, 26, 46, 31),
    ),
    "Saturn": dict(
        kind="outer",
        R=60.0,
        e=sexa(3, 25),
        r=sexa(6, 30),
        apogee0=sexa(224, 10),
        mean_lon0=sexa(296, 43),
        mean_lon_rate=sexa(0, 2, 0, 33, 31, 28, 51),
    ),
}

BODY_NAMES = ["Sun", "Moon", *PLANETS]


@dataclass
class BodyState:
    name: str
    center: tuple  # deferent centre
    pos: tuple  # body position, Earth at the origin
    lon: float  # apparent longitude seen from Earth
    mean_lon: float
    epi: tuple | None = None  # epicycle centre
    equant: tuple | None = None
    anomaly: float | None = None
    apogee_dir: float | None = None  # epicycle apogee direction


def _norm(deg):
    return deg % 360.0


def _polar(length, deg):
    a = math.radians(deg)
    return (length * math.cos(a), length * math.sin(a))


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _angle_of(frm, to):
    return _norm(math.degrees(math.atan2(to[1] - frm[1], to[0] - frm[0])))


def _ray_circle(origin, deg, center, radius):
    u = _polar(1.0, deg)
    d = (origin[0] - center[0], origin[1] - center[1])
    b = d[0] * u[0] + d[1] * u[1]
    t = -b + math.sqrt(b * b - (d[0] ** 2 + d[1] ** 2) + radius**2)
    return (origin[0] + t * u[0], origin[1] + t * u[1])


def mean_sun(days):
    return _norm(SUN["mean_lon0"] + SUN["mean_lon_rate"] * days)


def sun_state(days):
    center = _polar(SUN["e"], SUN["apogee0"])
    mean_lon = mean_sun(days)
    pos = _add(center, _polar(SUN["R"], mean_lon))
    return BodyState("Sun", center, pos, _angle_of((0, 0), pos), mean_lon)


def moon_state(days):
    sun_lon = mean_sun(days)
    mean_lon = _norm(MOON["mean_lon0"] + MOON["mean_lon_rate"] * days)
    elong = _norm(mean_lon - sun_lon)
    center = _polar(MOON["e"], sun_lon - elong)
    prosneusis = _polar(MOON["e"], sun_lon - elong + 180)
    epi = _ray_circle((0, 0), mean_lon, center, MOON["R"])
    anomaly = _norm(MOON["anomaly0"] + MOON["anomaly_rate"] * days)
    apogee_dir = _angle_of(prosneusis, epi)
    pos = _add(epi, _polar(MOON["r"], apogee_dir - anomaly))
    return BodyState(
        "Moon", center, pos, _angle_of((0, 0), pos), mean_lon, epi, None, anomaly, apogee_dir
    )


def planet_state(name, days):
    p = PLANETS[name]
    apogee = _norm(p["apogee0"] + APSIDAL_RATE * days)
    if "mean_lon_rate" in p:
        mean_lon = _norm(p["mean_lon0"] + p["mean_lon_rate"] * days)
        anomaly = _norm(mean_sun(days) - mean_lon)
    else:
        mean_lon = mean_sun(days)
        anomaly = _norm(p["anomaly0"] + p["anomaly_rate"] * days)
    if p["kind"] == "mercury":
        equant = _polar(p["e"], apogee)
        center = _add(_polar(2 * p["e"], apogee), _polar(p["e"], apogee - (mean_lon - apogee)))
    else:
        equant = _polar(2 * p["e"], apogee)
        center = _polar(p["e"], apogee)
    epi = _ray_circle(equant, mean_lon, center, p["R"])
    apogee_dir = _angle_of(equant, epi)
    pos = _add(epi, _polar(p["r"], apogee_dir + anomaly))
    return BodyState(
        name, center, pos, _angle_of((0, 0), pos), mean_lon, epi, equant, anomaly, apogee_dir
    )


def body_state(name, days):
    if name == "Sun":
        return sun_state(days)
    if name == "Moon":
        return moon_state(days)
    return planet_state(name, days)


def state(days):
    return {name: body_state(name, days) for name in BODY_NAMES}


def daily_motion(name, days):
    """Signed motion in longitude, degrees per day (negative = retrograde)."""
    a = body_state(name, days - 0.5).lon
    b = body_state(name, days + 0.5).lon
    return (b - a + 540.0) % 360.0 - 180.0


def days_from_jd(jd):
    return jd - EPOCH_JD
