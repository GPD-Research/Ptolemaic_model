// Tables and Credits dialogs: Ptolemy's tables to read, copy (tab-separated) or download (CSV).
(function () {
  const $ = (id) => document.getElementById(id);
  const SKY = window.PtolemySky, T = window.TABLES, STARS = window.PtolemyStars;
  const sx = (x) => SKY.toSexagesimal(x, 2);

  const TABLES = {
    chords: {
      title: "Table of chords (Almagest I.11)",
      note: "Chord of each arc in a circle of diameter 120 parts, crd a = 120 sin(a/2), recomputed in Ptolemy's base 60, every half degree.",
      build: () => [["arc (deg)", "chord (parts)", "sixtieths per half degree"],
        ...Array.from({ length: 360 }, (_, i) => {
          const a = (i + 1) / 2;
          return [String(a), sx(SKY.chord(a)), SKY.toSexagesimal((SKY.chord(a + 0.5) - SKY.chord(a)) / 30, 3)];
        })],
    },
    latitudes: {
      title: "Latitude tables (Almagest XIII.5)",
      note: "Latitude in degrees;minutes at the northern and southern limits (superior planets), and the deviation and slant (Venus, Mercury), by true anomaly on the epicycle. Ptolemy's values as given by Van Brummelen (1993), Tables 14.2-14.13.",
      build: () => [T.ptolemy_latitude_tables.header, ...T.ptolemy_latitude_tables.rows],
    },
    interpolation: {
      title: "Latitude interpolation table (Almagest XIII.5)",
      note: "Fraction g(n) of the full latitude at argument of latitude n (from the northern limit); g(180 - n) for n < 90. Van Brummelen (1993), Table 14.8.",
      build: () => [T.ptolemy_latitude_interpolation.header, ...T.ptolemy_latitude_interpolation.rows],
    },
    hypotheses: {
      title: "Sizes and distances (Planetary Hypotheses I)",
      note: "Least and greatest distance from Earth in Earth radii, apparent diameter as a fraction of the Sun's, and true diameter in Earth diameters. Ptolemy's values as given by Goldstein (1967). His Earth (Geography I) is 180,000 stades round, about 28,600 stades in radius. The viewer's dot sizes go as the square root of the diameter.",
      build: () => [["body", "least distance (Earth radii)", "greatest distance (Earth radii)", "apparent diameter (Sun = 1)", "diameter (Earth = 1)", "diameter (decimal)"],
        ...T.ptolemy_planetary_hypotheses.rows],
    },
    stars: {
      title: "Star catalogue (Almagest VII.5-VIII.1)",
      note: "1,028 entries: ecliptic longitude and latitude for AD 137, magnitude, Hipparcos match (Verbunt & van Gent 2012), Latin description (Baily 1843) and English gloss.",
      build: () => [["no", "constellation", "star", "longitude (deg)", "latitude (deg)", "magnitude", "qualifier", "Hipparcos", "V", "Latin", "English"],
        ...STARS.map((r) => [r[0], r[1], r[2], (r[3] / 60).toFixed(2), (r[4] / 60).toFixed(2), r[5], r[6], r[7] || "", r[8] ?? "", r[11], r[12]].map(String))],
    },
    precession: {
      title: "Precession (Almagest VII.2-3)",
      note: "Shift of the stars along the ecliptic since Ptolemy's catalogue: his 1 deg per century against the modern rate (about 1 deg per 72 years).",
      build: () => [["years after AD 137", "Ptolemy (deg)", "modern (deg)"],
        ...Array.from({ length: 21 }, (_, i) => {
          const y = i * 100, d = SKY.CATALOGUE_DAYS + y * 365.25;
          return [String(y), SKY.ptolemyShift(d).toFixed(2), SKY.trueShift(d).toFixed(2)];
        })],
    },
  };

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const csvCell = (s) => (/[",\n]/.test(s) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
  let current = null;

  function show(key) {
    const t = TABLES[key];
    current = { key, rows: t.build() };
    $("tblNote").textContent = t.note;
    const [head, ...body] = current.rows;
    $("tblView").innerHTML = `<table><thead><tr>${head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${
      body.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
  }

  const sel = $("tblSelect");
  Object.entries(TABLES).forEach(([k, t]) => sel.add(new Option(t.title, k)));
  sel.addEventListener("change", () => show(sel.value));
  $("tablesBtn").addEventListener("click", () => { show(sel.value); $("tablesDlg").showModal(); });
  $("creditsBtn").addEventListener("click", () => $("creditsDlg").showModal());
  document.querySelectorAll("dialog .close").forEach((b) => b.addEventListener("click", () => b.closest("dialog").close()));
  $("tblCopy").addEventListener("click", async () => {
    await navigator.clipboard.writeText(current.rows.map((r) => r.join("\t")).join("\n"));
    $("tblCopy").textContent = "Copied"; setTimeout(() => { $("tblCopy").textContent = "Copy"; }, 1200);
  });
  $("tblDownload").addEventListener("click", () => {
    const blob = new Blob([current.rows.map((r) => r.map(csvCell).join(",")).join("\n") + "\n"], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = `ptolemy_${current.key}.csv`; a.click();
    URL.revokeObjectURL(a.href);
  });
})();
