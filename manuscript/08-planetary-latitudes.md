# Chapter PT-8: Planetary Latitudes (Book XIII)

The planets do not stay on the ecliptic: Mars wanders up to about 7° south of it, Venus about 6° north. Book XIII, Ptolemy's last, models this by tilting the circles of the earlier books out of the ecliptic plane, so his model is three-dimensional.

* **Saturn, Jupiter and Mars.** Each deferent is tilted to the ecliptic, with fixed nodes. The northern limit lies at the beginning of Libra for Saturn and Jupiter, and at the end of Cancer, near the apogee, for Mars (XIII.1). The epicycle is tilted too, by an amount that follows the deferent, so the planet is farthest from the ecliptic when it is nearest the Earth, at opposition.
* **Venus and Mercury.** The deferent swings above and below the ecliptic: Venus's stays north by up to 1/6°, Mercury's south by up to 3/4°. The epicycle rocks about two diameters, a *deviation* (about the line through the epicycle's apogee) and a *slant* (about the line across it), each of which changes with the epicycle's place on the deferent (XIII.2-3).

## The tables (XIII.5)

Rather than leave the reader with three-dimensional geometry, Ptolemy tabulates the result. For the superior planets he gives the latitude at the northern and southern limits as a function of the planet's true anomaly *a* on the epicycle, and one shared interpolation table g(n), the Moon's latitude divided by its maximum of 5°. At argument of latitude *n*, counted from the northern limit,

    beta(n, a) = g(n) * beta_north(a)   when cos n >= 0,
    beta(n, a) = g(n) * beta_south(a)   otherwise,

with g close to cos n. For Venus and Mercury, with *n* the true centrum from the apogee, the latitude is the sum of three terms read from the same kind of tables: beta = beta1 + beta2 + beta3, the deferent's tilt (about i g(n)^2), the deviation and the slant. Mercury's slant is multiplied by 0.9 or 1.1, depending on which half of its deferent the epicycle is on.

`src/latitudes.py` (mirrored in `viewer/latitudes.js`) applies exactly this procedure to Ptolemy's tabulated values, so the numbers are his own, not a modern recomputation. In the viewer's 3-D sphere each planet is lifted off the ecliptic by its latitude, on a dotted line, and the "Tables" button shows every table.

## What it shows about the method

Book XIII is Ptolemy at his most empirical, and he says so: the latitude models are the hardest part of the work, and he admits their circles cannot all be physically real. He fits tilts that reproduce the observed extremes, and keeps the geometry only as far as it serves prediction. The approximations are good to a few minutes of arc against his own exact geometry (Van Brummelen 1993), and his latitudes are typically within a degree of the real sky. Kepler's single tilted plane per planet, through the Sun, replaced the whole apparatus.

Sources: the tables as given by G. Van Brummelen, *Mathematical Tables in Ptolemy's Almagest* (PhD thesis, Simon Fraser University, 1993), Tables 14.2-14.13; the limits and inclinations from K. Manitius's German translation (1912-13), XIII.1-3.
