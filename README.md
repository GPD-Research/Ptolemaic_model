# The Ptolemaic Geocentric Model

A kinematic model of the cosmos based on Aristotelian physics and Alexandrian geometry. This package places a stationary Earth at the center of the universe and models celestial motion entirely through uniform circular paths (deferents, epicycles, and equants).

## Overview
This module relies purely on geometry rather than dynamical forces. It is designed to test how a fundamentally flawed physical premise can still produce highly accurate observational predictions if given enough mathematical flexibility.

## Core Modules
* `src/core.py` - Calculates the 2D Cartesian spirograph paths of planetary orbits using nested circular frequencies.
* `src/astronomy.py` - Converts 2D physical paths into apparent angular longitudes as seen from an Earth-bound observer.
* `src/metrics.py` - Statistical engine customized for circular data, handling 360-degree wraparounds and aggressive parameter penalties.

## The sphere of the fixed stars
The Almagest is more than a planetary model. It also holds a star catalogue, a theory of precession and the trigonometry behind both, all still visible in how astronomy works today.
* `src/star_catalogue.py` - **Ptolemy's star catalogue** (Books VII-VIII): 1,028 entries in 48 constellations, each with ecliptic longitude and latitude for AD 137 and a magnitude from 1 to 6 (plus "faint" and "nebulous"). His magnitude scale is the one astronomers still use. Data: `data/ptolemy_star_catalogue.csv`, from the machine-readable edition of Verbunt & van Gent (2012, A&A 544, A31; CDS J/A+A/544/A31), based on Toomer's translation. That edition matches each star to its Hipparcos counterpart, so each entry carries Ptolemy's positional error: about half a degree typically (median 32'). Each entry's description in Latin, after Baily's 1843 edition (public domain), is in `data/ptolemy_star_descriptions.csv` with this repository's own English gloss (for example *Quae est in corde et vocatur Regulus*, "the one on the heart, called Regulus"); `tools/build_star_descriptions.py` re-extracts the Latin.
* `src/precession.py` - **Precession of the equinoxes**, discovered by Hipparchus: the stars drift east along the ecliptic. Ptolemy's rate is 1° per century, while the real rate is about 1° per 72 years. He added 2°40' to Hipparchus's longitudes, so his catalogue is already about 1° behind the real sky of AD 137, and his predictions fall further behind with time.
* `src/trigonometry.py` - **Chords and spherical trigonometry** (Book I): the table of chords, crd(a) = 120 sin(a/2) in base 60 at every half degree, and the Menelaus-theorem conversions from ecliptic longitude to declination and right ascension, using his obliquity of 23°51'20". The step from his ecliptic coordinates to the equatorial right ascension and declination used today is one of these conversions.
* `src/latitudes.py` - **Planetary latitudes** (Book XIII): each planet's distance north or south of the ecliptic, computed with Ptolemy's own XIII.5 tables (limits for Saturn, Jupiter and Mars, deviation and slant for Venus and Mercury, and the interpolation table). Data: `data/ptolemy_latitude_tables.csv` and `data/ptolemy_latitude_interpolation.csv`, Ptolemy's values as given in G. Van Brummelen, *Mathematical Tables in Ptolemy's Almagest* (PhD thesis, Simon Fraser University, 1993), Tables 14.2-14.13. The positions of the northern limits and the inclinations of Venus's and Mercury's deferents are from Manitius's 1912-13 German translation (public domain), XIII.1-3.

`viewer/sky.js`, `viewer/stars.js`, `viewer/latitudes.js` and `viewer/tables.js` are the viewer's copies; the tests check they match the Python. `python tools/build_star_catalogue.py` rebuilds both data files from CDS; `python tools/build_tables_js.py` rebuilds `viewer/tables.js`.

## Almagest Visualizer (animated viewer)
Run it online at https://gpd-research.com/Ptolemaic_model/viewer/, or open `viewer/index.html` in any browser (no build or server needed; `make viewer` opens it). It draws the full Almagest model in 2D, centred on a fixed Earth, and animates it in time:
* **Kinematics** (`viewer/ptolemy.js`, mirrored in `src/almagest.py`): eccentric deferents, equants and epicycles for the planets, the eccentric Sun, the lunar crank with its prosneusis point, and Mercury's moving deferent centre. Parameters, mean motions and epoch values (Nabonassar era) are Ptolemy's own.
* **Speed slider** from 1:1 real time up to about 3 years per second, with presets, play/pause, reverse, "Now" and jump-to-date.
* **Views**: schematic ring spacing or the absolute nesting distances of the *Planetary Hypotheses*, isolate a single body, zoom and pan, trails that trace each body's looping path relative to Earth, and a live table of apparent longitude and daily motion with retrograde flags.

* **3-D sphere of stars**: the "3-D sphere of stars" button tilts the planetary plane, which is the ecliptic, inside the sphere of the fixed stars. The sphere shows Ptolemy's 1,028 catalogue stars sized by his magnitude, the ecliptic with the twelve signs, and the celestial equator and poles at his obliquity. Drag to turn it. Precession moves the stars at his rate or the real one; the speed now goes up to 100 years per second, so the drift is visible. Click a star for its catalogue entry, its real position at that date and Ptolemy's error.
* **Planet latitudes**: in the 3-D view each planet sits north or south of the ecliptic by its Book XIII latitude, on a dotted line down to the plane, and the readout lists the latitude.
* **Tables and Credits**: the "Tables" button opens Ptolemy's chord table, star catalogue, latitude tables, interpolation table and a precession table, each of which can be copied or downloaded as CSV. "Credits" lists every source.

Positions are Ptolemy's predictions, not the modern sky: about 1° behind the real sky in his day (his equinox error), drifting to about 10° behind today because his tropical year is slightly too long.

## Suggested Experiments

### 1. Confirming the Model: Retrograde Motion
* **The Test:** Run historical Mars observation logs through `core.py` to generate the planet's path, then execute `detect_retrograde_motion()` in `astronomy.py`.
* **The Expected Result:** The epicycle mechanism perfectly replicates the visual "looping" behavior of Mars against the background stars, solving the greatest naked-eye observational puzzle of antiquity without violating the requirement for circular motion.

### 2. Confirming the Model: Naked-Eye Accuracy
* **The Test:** Compare the model's apparent longitude predictions against a dataset of naked-eye observations (e.g., Tycho Brahe's logs) and calculate the `mean_absolute_angular_error`.
* **The Expected Result:** When properly tuned with equants, the model's error rate drops to within 1-2 degrees. This confirms why the model remained the undisputed scientific consensus for 1,500 years: it successfully predicted eclipses and planetary alignments within the error margins of human vision.

### 3. Challenging the Model: Parameter Overfitting (AIC/BIC)
* **The Test:** Add secondary and tertiary epicycles to the core algorithm to force the prediction curve to perfectly match a high-precision modern orbital dataset. Run the `evaluate_kinematic_model()` function to check the Akaike Information Criterion (AIC).
* **The Expected Result:** While the Chi-squared value drops (indicating a better fit), the AIC score will skyrocket. This mathematically proves the model is suffering from extreme parameter bloat, structurally exposing "epicycle stacking" as a statistical failure rather than a physical truth.

### 4. Challenging the Model: The Phases of Venus
* **The Test:** Calculate the Earth-to-planet distance vector over time for Venus, and map it to a visual illumination phase (simulating telescopic data).
* **The Expected Result:** Because the Ptolemaic model locks Venus's epicycle between the Earth and the Sun, it predicts that Venus can only ever appear as a crescent. Modern datasets showing a "full" Venus utterly destroy the geometric architecture, completely invalidating the geocentric premise.

### 5. Challenging the Model: The Apparent Diameter of Mars
* **The Test:** Use the IDE to fit the deferent and epicycle radii ($R$ and $r$) to perfectly match the *angular* retrograde loop data in `almagest_planetary_logs.csv`. Then, run a distance calculator (e.g., `np.sqrt(x**2 + y**2)`) to plot the model's predicted variation in Mars's physical distance from Earth, comparing it to historical data on Mars's changing brightness and apparent diameter.
* **The Expected Result:** To make the angles work, the Ptolemaic geometry forces a specific $r/R$ ratio that predicts only a minor change in distance. However, observational data shows Mars's apparent diameter changes by a factor of 7 (and brightness by a factor of ~60) during opposition. The model cannot simultaneously satisfy the angular data and the distance data—proving that while epicycles can spoof 2D coordinates on the sky, they fail catastrophically as a 3D physical architecture. This anomaly is naturally solved by a heliocentric co-orbital system where Earth physically "laps" Mars.

**Cache-busting:** every local script, stylesheet and image an HTML page loads carries `?v=<hash of the file>`, so visitors get changes at once instead of mixing new and cached files. After editing one, run `python tools/stamp_assets.py`; CI fails (`--check`) if a tag is stale.
