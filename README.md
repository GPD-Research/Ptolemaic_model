# The Ptolemaic Geocentric Model

A kinematic model of the cosmos based on Aristotelian physics and Alexandrian geometry. This package places a stationary Earth at the center of the universe and models celestial motion entirely through uniform circular paths (deferents, epicycles, and equants).

## Overview
This module relies purely on geometry rather than dynamical forces. It is designed to test how a fundamentally flawed physical premise can still produce highly accurate observational predictions if given enough mathematical flexibility.

## Core Modules
* `src/core.py` - Calculates the 2D Cartesian spirograph paths of planetary orbits using nested circular frequencies.
* `src/astronomy.py` - Converts 2D physical paths into apparent angular longitudes as seen from an Earth-bound observer.
* `src/metrics.py` - Statistical engine customized for circular data, handling 360-degree wraparounds and aggressive parameter penalties.

## Geocentric Simulator (animated viewer)
Run it online at https://gpd-research.com/Ptolemaic_model/viewer/, or open `viewer/index.html` in any browser (no build or server needed; `make viewer` opens it). It draws the full Almagest model in 2D, centred on a fixed Earth, and animates it in time:
* **Kinematics** (`viewer/ptolemy.js`, mirrored in `src/almagest.py`): eccentric deferents, equants and epicycles for the planets, the eccentric Sun, the lunar crank with its prosneusis point, and Mercury's moving deferent centre. Parameters, mean motions and epoch values (Nabonassar era) are Ptolemy's own.
* **Speed slider** from 1:1 real time up to about 3 years per second, with presets, play/pause, reverse, "Now" and jump-to-date.
* **Views**: schematic ring spacing or the absolute nesting distances of the *Planetary Hypotheses*, isolate a single body, zoom and pan, trails that trace each body's looping path relative to Earth, and a live table of apparent longitude and daily motion with retrograde flags.

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
