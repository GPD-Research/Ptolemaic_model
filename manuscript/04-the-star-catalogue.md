# Chapter PT-4: The Star Catalogue

Books VII and VIII of the *Almagest* hold the oldest star catalogue to survive complete: 1,028 entries (Toomer's numbering) in 48 constellations, about 1,022 distinct stars. For fourteen centuries it was *the* catalogue; Ulugh Beg's of 1437 was the first wholly new one.

## Coordinates on the ecliptic
Each star is given by **ecliptic longitude**, as a zodiacal sign plus degrees and minutes (Regulus: Leo 2°30′), and **ecliptic latitude** north or south (+0°10′). Measuring from the ecliptic was natural for Ptolemy: the Sun, Moon and planets all move near it, and precession moves every star along it at the same rate while leaving its latitude fixed. Today's equatorial right ascension and declination are the same idea measured from the celestial equator; Book I's spherical trigonometry converts one to the other (Chapter PT-6).

## Magnitudes
Every star has a brightness class from 1 (brightest) to 6 (faintest visible), sometimes marked "a little brighter" or "a little fainter", plus a few marked faint or nebulous. Modern magnitudes keep his scale: Pogson's 1856 definition, five magnitudes = a factor of 100 in brightness, was chosen to match it.

## Accuracy
Matched against Hipparcos (Verbunt & van Gent 2012), the typical random error of a position is about half a degree (median 32′). In addition, all longitudes are systematically about 1° too small for his epoch, AD 137 (Chapter PT-5). `src/star_catalogue.py` holds the catalogue with each star's error.
