"""Ptolemy's star catalogue (Almagest VII.5-VIII.1): 48 constellations, ecliptic coordinates.

Read from data/ptolemy_star_catalogue.csv, the machine-readable edition of Verbunt & van Gent
2012 (A&A 544, A31, CDS J/A+A/544/A31) after Toomer's edition, with Hipparcos identifications.
Longitudes are for the catalogue epoch, AD 137.
"""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from src import precession, trigonometry

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "ptolemy_star_catalogue.csv"
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpius",
         "Sagittarius", "Capricornus", "Aquarius", "Pisces"]  # fmt: skip

# Abbreviation -> (modern name, Ptolemy's name in English).
CONSTELLATIONS = {
    "UMi": ("Ursa Minor", "Little Bear"), "UMa": ("Ursa Major", "Great Bear"),
    "Dra": ("Draco", "Dragon"), "Cep": ("Cepheus", "Cepheus"), "Boo": ("Boötes", "Boötes"),
    "CrB": ("Corona Borealis", "Northern Crown"), "Her": ("Hercules", "Kneeler"),
    "Lyr": ("Lyra", "Lyre"), "Cyg": ("Cygnus", "Bird"), "Cas": ("Cassiopeia", "Cassiopeia"),
    "Per": ("Perseus", "Perseus"), "Aur": ("Auriga", "Charioteer"),
    "Oph": ("Ophiuchus", "Serpent-holder"), "Ser": ("Serpens", "Serpent"),
    "Sge": ("Sagitta", "Arrow"), "Aql": ("Aquila", "Eagle"), "Del": ("Delphinus", "Dolphin"),
    "Equ": ("Equuleus", "Forepart of the Horse"), "Peg": ("Pegasus", "Horse"),
    "And": ("Andromeda", "Andromeda"), "Tri": ("Triangulum", "Triangle"),
    "Ari": ("Aries", "Ram"), "Tau": ("Taurus", "Bull"), "Gem": ("Gemini", "Twins"),
    "Cnc": ("Cancer", "Crab"), "Leo": ("Leo", "Lion"), "Vir": ("Virgo", "Virgin"),
    "Lib": ("Libra", "Claws"), "Sco": ("Scorpius", "Scorpion"),
    "Sgr": ("Sagittarius", "Archer"), "Cap": ("Capricornus", "Goat-horned"),
    "Aqr": ("Aquarius", "Water-pourer"), "Psc": ("Pisces", "Fishes"),
    "Cet": ("Cetus", "Sea-monster"), "Ori": ("Orion", "Orion"), "Eri": ("Eridanus", "River"),
    "Lep": ("Lepus", "Hare"), "CMa": ("Canis Major", "Dog"), "CMi": ("Canis Minor", "Procyon"),
    "Arg": ("Argo Navis", "Argo"), "Hya": ("Hydra", "Hydra"), "Crt": ("Crater", "Bowl"),
    "Crv": ("Corvus", "Raven"), "Cen": ("Centaurus", "Centaur"), "Lup": ("Lupus", "Beast"),
    "Ara": ("Ara", "Censer"), "CrA": ("Corona Australis", "Southern Crown"),
    "PsA": ("Piscis Austrinus", "Southern Fish"),
}  # fmt: skip


@dataclass(frozen=True)
class Star:
    number: int
    constellation: str
    index: int
    lon: float  # ecliptic longitude, degrees, epoch AD 137
    lat: float  # ecliptic latitude, degrees (north positive)
    magnitude: int  # 1-6; 7 = "faint", 9 = "nebulous"
    qualifier: str  # "b" brighter or "f" fainter than the magnitude, or ""
    hip: int  # Hipparcos identification, 0 if none
    d_lon: float | None  # Hipparcos - Ptolemy at equinox -128, arcmin
    d_lat: float | None
    error: float | None  # distance between the two positions, arcmin

    @property
    def sign(self):
        """Ptolemy's notation: (sign, degrees, minutes) of longitude."""
        s, rest = divmod(round(self.lon * 60), 1800)
        return SIGNS[s], rest // 60, rest % 60


def load():
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    stars = []
    for r in rows:
        lat = int(r["lat_deg"]) + int(r["lat_min"]) / 60
        hip = int(r["hip"] or 0)
        num = lambda k: float(r[k]) if hip else None  # noqa: E731
        stars.append(
            Star(
                number=int(r["number"]),
                constellation=r["constellation"],
                index=int(r["index"]),
                lon=(int(r["lon_sign"]) - 1) * 30 + int(r["lon_deg"]) + int(r["lon_min"]) / 60,
                lat=-lat if r["lat_dir"] == "A" else lat,
                magnitude=int(r["magnitude"]),
                qualifier=r["qualifier"],
                hip=hip,
                d_lon=num("d_lon_arcmin"),
                d_lat=num("d_lat_arcmin"),
                error=num("dist_arcmin"),
            )
        )
    return stars


def position(star, days, rate="ptolemy"):
    """Ecliptic (lon, lat) of a star at `days`; precession moves only the longitude."""
    return precession.star_longitude(star.lon, days, rate), star.lat


def equatorial(star, days, rate="ptolemy"):
    """(right ascension, declination) at `days`, with Ptolemy's obliquity of 23;51,20."""
    return trigonometry.ecliptic_to_equatorial(*position(star, days, rate))


def median_error(stars):
    errs = sorted(s.error for s in stars if s.error is not None)
    n = len(errs)
    return (errs[n // 2] + errs[(n - 1) // 2]) / 2 if n else math.nan
