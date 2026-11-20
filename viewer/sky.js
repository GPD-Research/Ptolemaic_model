/*
 * Ptolemy's sphere of the fixed stars: chords (Almagest I.11), Menelaus conversions (I.14-16)
 * and precession (VII.2-3) against the real rate. Mirrors src/trigonometry.py and
 * src/precession.py; tests/test_star_catalogue.py checks the two agree. Time is days from the
 * Nabonassar epoch, as in ptolemy.js.
 */
(function (root) {
  "use strict";

  const P = typeof module !== "undefined" && module.exports ? require("./ptolemy.js") : root.Ptolemy;
  const RAD = Math.PI / 180;

  // Almagest I.12: the arc between the tropics is 47;42,40 degrees.
  const OBLIQUITY = 23 + 51 / 60 + 20 / 3600;
  const chord = (a) => 120 * Math.sin((a * RAD) / 2);
  const arc = (c) => (2 * Math.asin(Math.max(-1, Math.min(1, c / 120)))) / RAD;

  function toSexagesimal(x, places = 2) {
    let n = Math.round(x * 60 ** places);
    const digits = [];
    for (let i = 0; i < places; i++) {
      digits.unshift(n % 60);
      n = Math.floor(n / 60);
    }
    return [n, ...digits];
  }

  const quadrant = (lon) => {
    lon = ((lon % 360) + 360) % 360;
    return [lon, lon <= 90 ? lon : lon <= 270 ? 180 - lon : lon - 360];
  };

  // crd(2δ) = crd(2ε) crd(2λ) / 120, i.e. sin δ = sin ε sin λ.
  function declinationOfEcliptic(lon, eps = OBLIQUITY) {
    const [, q] = quadrant(lon);
    return Math.sign(q) * (arc((chord(2 * eps) * chord(2 * Math.abs(q))) / 120) / 2);
  }

  // crd(2α) = 120 crd(2δ) crd(180 − 2ε) / (crd(180 − 2δ) crd(2ε)), i.e. sin α = tan δ / tan ε.
  function rightAscensionOfEcliptic(lon, eps = OBLIQUITY) {
    const [l, q] = quadrant(lon);
    if (eps === 0) return l;
    const d = Math.abs(declinationOfEcliptic(q, eps));
    const a0 = arc((120 * chord(2 * d) * chord(180 - 2 * eps)) / (chord(180 - 2 * d) * chord(2 * eps))) / 2;
    return l <= 90 ? a0 : l <= 180 ? 180 - a0 : l <= 270 ? 180 + a0 : 360 - a0;
  }

  function eclipticToEquatorial(lon, lat, eps = OBLIQUITY) {
    const [l, b, e] = [lon * RAD, lat * RAD, eps * RAD];
    const dec = Math.asin(Math.sin(b) * Math.cos(e) + Math.cos(b) * Math.sin(e) * Math.sin(l));
    const ra = Math.atan2(Math.sin(l) * Math.cos(e) - Math.tan(b) * Math.sin(e), Math.cos(l));
    return [((ra / RAD) % 360 + 360) % 360, dec / RAD];
  }

  // 1 degree per 100 Egyptian years, the same rate as the planetary apogees.
  const PTOLEMY_RATE = 1 / 36500;
  const CATALOGUE_DAYS = 884 * 365; // AD 137 July 20, start of Antoninus's reign
  const HIPPARCHUS_DAYS = CATALOGUE_DAYS - 265 * 365;
  const HIPPARCHUS_SHIFT = 2 + 40 / 60;

  const ptolemyShift = (days, since = CATALOGUE_DAYS) => (days - since) * PTOLEMY_RATE;
  // General precession in longitude, IAU 2006.
  const pA = (d) => {
    const t = (d + P.EPOCH_JD - 2451545) / 36525;
    return (5028.796195 * t + 1.1054348 * t * t) / 3600;
  };
  const trueShift = (days, since = CATALOGUE_DAYS) => pA(days) - pA(since);
  const trueObliquity = (days) => {
    const t = (days + P.EPOCH_JD - 2451545) / 36525;
    return (84381.406 - 46.836769 * t - 0.0001831 * t * t) / 3600;
  };
  const catalogueErrorAtEpoch = () => trueShift(CATALOGUE_DAYS, HIPPARCHUS_DAYS) - HIPPARCHUS_SHIFT;
  const norm = (x) => ((x % 360) + 360) % 360;
  const starLongitude = (lon, days, rate = "ptolemy") =>
    norm(rate === "ptolemy" ? lon + ptolemyShift(days) : lon + catalogueErrorAtEpoch() + trueShift(days));

  const api = {
    OBLIQUITY, chord, arc, toSexagesimal, declinationOfEcliptic, rightAscensionOfEcliptic,
    eclipticToEquatorial, PTOLEMY_RATE, CATALOGUE_DAYS, HIPPARCHUS_DAYS, HIPPARCHUS_SHIFT,
    ptolemyShift, trueShift, trueObliquity, catalogueErrorAtEpoch, starLongitude,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PtolemySky = api;
})(this);
