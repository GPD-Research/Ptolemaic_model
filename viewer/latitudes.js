// Ptolemy's planetary latitudes (Almagest XIII) from his XIII.5 tables; mirrors src/latitudes.py.
(function (root) {
  const P = typeof module !== "undefined" && module.exports ? require("./ptolemy.js") : root.Ptolemy;
  const T = typeof module !== "undefined" && module.exports ? require("./tables.js") : root.TABLES;

  const NORTHERN_LIMIT = { Saturn: 180, Jupiter: 180, Mars: 120 };
  const INCLINATION = { Venus: 10 / 60, Mercury: -45 / 60 };
  const rad = (d) => (d * Math.PI) / 180;

  function sexagesimal(text) {
    const [whole, frac] = text.split(";");
    return (Number(whole) || 0) + frac.split(",").reduce((s, d, i) => s + Number(d) / 60 ** (i + 1), 0);
  }

  const lat = T.ptolemy_latitude_tables;
  const GRID = lat.rows.map((r) => Number(r[0]));
  const TABLE = {};
  lat.header.slice(1).forEach((k, j) => { TABLE[k] = lat.rows.map((r) => sexagesimal(r[j + 1])); });
  const G_TABLE = [[90, 0], ...T.ptolemy_latitude_interpolation.rows.map((r) => [Number(r[0]), sexagesimal(r[1])])];

  function interp(xs, ys, x) {
    for (let i = 1; i < xs.length; i++) {
      if (x <= xs[i]) return ys[i - 1] + ((x - xs[i - 1]) / (xs[i] - xs[i - 1])) * (ys[i] - ys[i - 1]);
    }
    return ys[ys.length - 1];
  }
  const fold = (a) => { a = ((a % 360) + 360) % 360; return a > 180 ? 360 - a : a; };

  function table(name, a) {
    const ys = TABLE[name];
    return interp([0, ...GRID], [name.endsWith("slant") ? 0 : ys[0], ...ys], fold(a));
  }

  function g(n) {
    n = fold(n);
    const xs = G_TABLE.map((p) => p[0]), ys = G_TABLE.map((p) => p[1]);
    return n < 90 ? interp(xs, ys, 180 - n) : -interp(xs, ys, n);
  }

  const sign = (x) => (x < 0 ? -1 : 1);

  function superiorLatitude(name, n, a) {
    const side = Math.cos(rad(n)) >= 0 ? "north" : "south";
    return g(n) * table(`${name.toLowerCase()}_${side}`, a);
  }

  function inferiorLatitude(name, n, a) {
    const s = name === "Venus" ? 1 : -1, key = name.toLowerCase();
    const beta1 = INCLINATION[name] * g(n) ** 2;
    const dev = table(`${key}_deviation`, a) * (fold(a) < 90 ? 1 : -1);
    const beta2 = -s * sign(Math.sin(rad(n))) * Math.abs(g(n - 90)) * dev;
    let slant = table(`${key}_slant`, a) * sign(Math.sin(rad(a)));
    if (name === "Mercury") slant *= Math.cos(rad(n)) < 0 ? 1.1 : 0.9;
    return beta1 + beta2 + s * g(n) * slant;
  }

  const lonOf = (p) => (((Math.atan2(p[1], p[0]) * 180) / Math.PI) % 360 + 360) % 360;

  // Latitude in degrees north from a planetState (viewer/ptolemy.js).
  function latitudeOf(st) {
    const centre = lonOf(st.epi);
    const a = st.anomaly + st.apogeeDir - centre;
    if (st.name in NORTHERN_LIMIT) return superiorLatitude(st.name, centre - NORTHERN_LIMIT[st.name], a);
    if (st.name in INCLINATION) return inferiorLatitude(st.name, centre - st.apogee, a);
    return 0;
  }

  const latitude = (name, days) => latitudeOf(P.bodyState(name, days));

  const api = { NORTHERN_LIMIT, INCLINATION, sexagesimal, table, g, superiorLatitude, inferiorLatitude, latitudeOf, latitude };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Latitudes = api;
})(this);
