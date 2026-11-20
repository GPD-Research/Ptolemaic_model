"""Precession of the equinoxes: Ptolemy's rate against the real one. Mirrors viewer/sky.js.

Time is days from the Nabonassar epoch, as in src/almagest.py. Ptolemy (Almagest VII.2-3) moves
the fixed stars 1 degree per 100 Egyptian years of 365 days about the poles of the ecliptic, the
same rate as the planetary apogees (almagest.APSIDAL_RATE).
"""

from src.almagest import APSIDAL_RATE, EPOCH_JD

PTOLEMY_RATE = APSIDAL_RATE  # degrees per day: 1 degree per 36,500 days
CATALOGUE_DAYS = 884 * 365  # Nabonassar 885 Thoth 1 = AD 137 July 20, start of Antoninus's reign
# Ptolemy (VII.2): 265 years separate Hipparchus's observations from the catalogue epoch,
# so he added 2;40 degrees to Hipparchus's longitudes.
HIPPARCHUS_DAYS = CATALOGUE_DAYS - 265 * 365
HIPPARCHUS_SHIFT = 2 + 40 / 60


def ptolemy_shift(days, since=CATALOGUE_DAYS):
    """Degrees the stars move east between `since` and `days` at Ptolemy's rate."""
    return (days - since) * PTOLEMY_RATE


def true_shift(days, since=CATALOGUE_DAYS):
    """Degrees of real general precession in longitude between `since` and `days` (IAU 2006)."""

    def p(d):
        t = (d + EPOCH_JD - 2451545.0) / 36525
        return (5028.796195 * t + 1.1054348 * t * t) / 3600

    return p(days) - p(since)


def catalogue_error_at_epoch():
    """How far the real sky of AD 137 is ahead of Ptolemy's catalogue longitudes, in degrees.

    His longitudes fit the sky of Hipparchus's time plus his 2;40 degrees, while the real
    precession over those 265 years was about 3 2/3 degrees.
    """
    return true_shift(CATALOGUE_DAYS, HIPPARCHUS_DAYS) - HIPPARCHUS_SHIFT


def star_longitude(lon, days, rate="ptolemy"):
    """Longitude at `days` of a star whose catalogue longitude (AD 137) is lon.

    rate="ptolemy" is the Almagest's prediction; rate="true" is where the star really was or is,
    ignoring proper motion and Ptolemy's random errors.
    """
    if rate == "ptolemy":
        return (lon + ptolemy_shift(days)) % 360
    return (lon + catalogue_error_at_epoch() + true_shift(days)) % 360


def true_obliquity(days):
    """Real mean obliquity of the ecliptic at `days`, degrees (IAU 2006)."""
    t = (days + EPOCH_JD - 2451545.0) / 36525
    return (84381.406 - 46.836769 * t - 0.0001831 * t * t) / 3600
