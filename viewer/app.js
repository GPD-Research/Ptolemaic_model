(function () {
  "use strict";
  const P = window.Ptolemy;
  const L = window.Latitudes;
  const SKY = window.PtolemySky;
  const STARS = window.PtolemyStars;
  const RAD = Math.PI / 180;
  // Constellation abbreviation -> [Ptolemy's name, modern name].
  const CONST = {
    UMi: ["Little Bear", "Ursa Minor"], UMa: ["Great Bear", "Ursa Major"], Dra: ["Dragon", "Draco"],
    Cep: ["Cepheus", "Cepheus"], Boo: ["Boötes", "Boötes"], CrB: ["Northern Crown", "Corona Borealis"],
    Her: ["Kneeler", "Hercules"], Lyr: ["Lyre", "Lyra"], Cyg: ["Bird", "Cygnus"], Cas: ["Cassiopeia", "Cassiopeia"],
    Per: ["Perseus", "Perseus"], Aur: ["Charioteer", "Auriga"], Oph: ["Serpent-holder", "Ophiuchus"],
    Ser: ["Serpent", "Serpens"], Sge: ["Arrow", "Sagitta"], Aql: ["Eagle", "Aquila"], Del: ["Dolphin", "Delphinus"],
    Equ: ["Forepart of the Horse", "Equuleus"], Peg: ["Horse", "Pegasus"], And: ["Andromeda", "Andromeda"],
    Tri: ["Triangle", "Triangulum"], Ari: ["Ram", "Aries"], Tau: ["Bull", "Taurus"], Gem: ["Twins", "Gemini"],
    Cnc: ["Crab", "Cancer"], Leo: ["Lion", "Leo"], Vir: ["Virgin", "Virgo"], Lib: ["Claws", "Libra"],
    Sco: ["Scorpion", "Scorpius"], Sgr: ["Archer", "Sagittarius"], Cap: ["Goat-horned", "Capricornus"],
    Aqr: ["Water-pourer", "Aquarius"], Psc: ["Fishes", "Pisces"], Cet: ["Sea-monster", "Cetus"],
    Ori: ["Orion", "Orion"], Eri: ["River", "Eridanus"], Lep: ["Hare", "Lepus"], CMa: ["Dog", "Canis Major"],
    CMi: ["Procyon", "Canis Minor"], Arg: ["Argo", "Argo Navis"], Hya: ["Hydra", "Hydra"], Crt: ["Bowl", "Crater"],
    Crv: ["Raven", "Corvus"], Cen: ["Centaur", "Centaurus"], Lup: ["Beast", "Lupus"], Ara: ["Censer", "Ara"],
    CrA: ["Southern Crown", "Corona Australis"], PsA: ["Southern Fish", "Piscis Austrinus"],
  };
  const ZODIAC = ["Ari", "Tau", "Gem", "Cnc", "Leo", "Vir", "Lib", "Sco", "Sgr", "Cap", "Aqr", "Psc"];
  // Common names by Hipparcos number.
  const NAMES = {
    32349: "Sirius", 30438: "Canopus", 69673: "Arcturus", 91262: "Vega", 24608: "Capella", 24436: "Rigel",
    37279: "Procyon", 27989: "Betelgeuse", 97649: "Altair", 21421: "Aldebaran", 65474: "Spica", 80763: "Antares",
    37826: "Pollux", 113368: "Fomalhaut", 102098: "Deneb", 49669: "Regulus", 36850: "Castor", 11767: "Polaris",
    25336: "Bellatrix", 54061: "Dubhe", 62956: "Alioth", 65378: "Mizar", 67301: "Alkaid", 14576: "Algol",
    15863: "Mirfak", 57632: "Denebola", 46390: "Alphard", 9884: "Hamal", 86032: "Rasalhague", 76267: "Alphecca",
    113963: "Markab", 677: "Alpheratz", 3179: "Schedar", 68756: "Thuban", 72607: "Kochab", 13847: "Acamar", 26311: "Alnilam",
  };
  // Zodiac constellation label positions: circular-mean longitude and mean latitude (AD 137).
  const CENTROIDS = ZODIAC.map((c) => {
    const rows = STARS.filter((r) => r[1] === c);
    const x = rows.reduce((a, r) => a + Math.cos((r[3] / 60) * RAD), 0), y = rows.reduce((a, r) => a + Math.sin((r[3] / 60) * RAD), 0);
    return [c, Math.atan2(y, x) / RAD, rows.reduce((a, r) => a + r[4] / 60, 0) / rows.length];
  });

  const BODIES = {
    Moon: { color: "#c9d1de", synodic: 29.5, trailDays: 30, step: 0.2, hypotheses: 64, size: 4 },
    Mercury: { color: "#7fd1c7", synodic: 116, trailDays: 365, step: 0.5, hypotheses: 166, size: 3.5 },
    Venus: { color: "#f4e7b5", synodic: 584, trailDays: 2922, step: 2, hypotheses: 1079, size: 4.5 },
    Sun: { color: "#ffc93c", synodic: 365.25, trailDays: 365.25, step: 5, hypotheses: 1260, size: 7 },
    Mars: { color: "#ff6b4a", synodic: 780, trailDays: 15 * 365.25, step: 3, hypotheses: 8820, size: 4 },
    Jupiter: { color: "#e8a96b", synodic: 399, trailDays: 12 * 365.25, step: 5, hypotheses: 14187, size: 5.5 },
    Saturn: { color: "#d7c58a", synodic: 378, trailDays: 30 * 365.25, step: 6, hypotheses: 19865, size: 5 },
  };
  const ORDER = Object.keys(BODIES);
  const SIGNS = ["\u2648", "\u2649", "\u264A", "\u264B", "\u264C", "\u264D", "\u264E", "\u264F", "\u2650", "\u2651", "\u2652", "\u2653"]
    .map((g) => g + "\uFE0E");

  // Greatest distance from Earth in parts, used to scale each body to its ring.
  function maxDistance(name) {
    if (name === "Sun") return P.SUN.R + P.SUN.e;
    if (name === "Moon") return P.MOON.R + P.MOON.e + P.MOON.r;
    const p = P.PLANETS.find((q) => q.name === name);
    return p.R + (p.kind === "mercury" ? 3 * p.e : p.e) + p.r;
  }

  const $ = (id) => document.getElementById(id);
  const canvas = $("sky");
  const ctx = canvas.getContext("2d");
  const opt = {};
  ["showDeferent", "showEpicycle", "showEquant", "showSight", "showZodiac", "showStars", "showEquator", "showConst"].forEach((id) => {
    opt[id] = $(id).checked;
    $(id).addEventListener("change", () => { opt[id] = $(id).checked; });
  });

  let days = P.daysFromDate(new Date());
  let speed = 1;
  let playing = true;
  let direction = 1;
  let scaleMode = "schematic";
  let focus = "All";
  let zoom = 1;
  let pan = [0, 0];
  let lastFrame = performance.now();
  let view3d = false;
  const VIEW0 = { yaw: -0.6, tilt: 1.05 };
  let yaw = VIEW0.yaw, tilt = VIEW0.tilt;
  let starRate = "ptolemy";
  let selected = null;
  let starScreen = [];
  let trailMode = $("trail").value;
  $("trail").addEventListener("change", () => { trailMode = $("trail").value; });

  const focusSel = $("focus");
  ["All", ...ORDER].forEach((n) => {
    const o = document.createElement("option");
    o.value = n;
    o.textContent = n === "All" ? "All bodies" : "Only " + n;
    focusSel.appendChild(o);
  });

  // ---- view geometry ------------------------------------------------------
  let W = 0, H = 0, dpr = 1;
  function resize() {
    dpr = window.devicePixelRatio || 1;
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  }
  window.addEventListener("resize", resize);

  const viewRadius = () => Math.min(W, H) / 2 - (opt.showZodiac ? 44 : 16);

  // Pixels per part for a body before zoom.
  function bodyScale(name) {
    const R = viewRadius();
    if (focus !== "All") return (0.97 * R) / maxDistance(name);
    if (scaleMode === "hypotheses") return (BODIES[name].hypotheses / 19865) * R / maxDistance(name);
    const ring = ORDER.indexOf(name) + 1;
    return ((ring / ORDER.length) * R) / maxDistance(name);
  }

  // 3-D: turn by yaw about the ecliptic pole, then tilt the plane away from a top-down view.
  // Returns [screen x, screen y, depth toward the viewer].
  function toScreen(p, k) {
    const x = p[0] * k * zoom, y = p[1] * k * zoom, z = (p[2] || 0) * k * zoom;
    if (!view3d) return [W / 2 + pan[0] + x, H / 2 + pan[1] - y, z];
    const c = Math.cos(yaw), s = Math.sin(yaw), xr = x * c - y * s, yr = x * s + y * c;
    return [W / 2 + pan[0] + xr, H / 2 + pan[1] - (yr * Math.cos(tilt) + z * Math.sin(tilt)), -yr * Math.sin(tilt) + z * Math.cos(tilt)];
  }

  // ---- drawing ------------------------------------------------------------
  function circle(c, radius, k, stroke, width, dash) {
    const s = toScreen(c, k);
    ctx.beginPath();
    if (view3d) {
      for (let i = 0; i <= 96; i++) {
        const a = (i / 96) * 2 * Math.PI, q = toScreen([c[0] + radius * Math.cos(a), c[1] + radius * Math.sin(a)], k);
        if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]);
      }
    } else ctx.arc(s[0], s[1], radius * k * zoom, 0, 2 * Math.PI);
    ctx.setLineDash(dash || []);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.setLineDash([]);
  }

  function line(a, b, k, stroke, width, dash) {
    const sa = toScreen(a, k), sb = toScreen(b, k);
    ctx.beginPath();
    ctx.moveTo(sa[0], sa[1]);
    ctx.lineTo(sb[0], sb[1]);
    ctx.setLineDash(dash || []);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.setLineDash([]);
  }

  function mark(p, k, color, kind) {
    const [x, y] = toScreen(p, k);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    if (kind === "plus") { ctx.moveTo(x - 4, y); ctx.lineTo(x + 4, y); ctx.moveTo(x, y - 4); ctx.lineTo(x, y + 4); }
    else if (kind === "cross") { ctx.moveTo(x - 4, y - 4); ctx.lineTo(x + 4, y + 4); ctx.moveTo(x - 4, y + 4); ctx.lineTo(x + 4, y - 4); }
    else { ctx.moveTo(x, y - 4); ctx.lineTo(x + 4, y); ctx.lineTo(x, y + 4); ctx.lineTo(x - 4, y); ctx.closePath(); }
    ctx.stroke();
  }

  function alpha(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
  }

  function drawZodiac() {
    const R = viewRadius() + 6;
    const cx = W / 2, cy = H / 2;
    ctx.strokeStyle = "#2a3550";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * Math.PI); ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, R + 30, 0, 2 * Math.PI); ctx.stroke();
    for (let d = 0; d < 360; d += 5) {
      const a = (d * Math.PI) / 180, len = d % 30 === 0 ? 30 : d % 10 === 0 ? 7 : 4;
      ctx.beginPath();
      ctx.moveTo(cx + R * Math.cos(a), cy - R * Math.sin(a));
      ctx.lineTo(cx + (R + len) * Math.cos(a), cy - (R + len) * Math.sin(a));
      ctx.stroke();
    }
    ctx.fillStyle = "#6f7d9c";
    ctx.font = "16px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    SIGNS.forEach((g, i) => {
      const a = ((i * 30 + 15) * Math.PI) / 180;
      ctx.fillText(g, cx + (R + 17) * Math.cos(a), cy - (R + 17) * Math.sin(a));
    });
  }

  // ---- the sphere of the fixed stars (3-D view) -----------------------------
  const sphereRadius = () => viewRadius() + 24;
  const unit = (lon, lat) => [Math.cos(lat * RAD) * Math.cos(lon * RAD), Math.cos(lat * RAD) * Math.sin(lon * RAD), Math.sin(lat * RAD)];
  const onSphere = (v) => toScreen(v, sphereRadius());
  const eqToEcl = (ra, dec, eps) => {
    const [x, y, z] = unit(ra, dec), e = eps * RAD;
    return [x, y * Math.cos(e) + z * Math.sin(e), -y * Math.sin(e) + z * Math.cos(e)];
  };
  const starLon = (r) => SKY.starLongitude(r[3] / 60, days, starRate);

  function greatCircle(pointAt, front, color, width, dash) {
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.setLineDash(front ? [] : dash);
    ctx.beginPath();
    let prev = null;
    for (let i = 0; i <= 180; i++) {
      const q = onSphere(pointAt(i * 2));
      const vis = (q[2] >= 0) === front;
      if (vis && prev) ctx.lineTo(q[0], q[1]); else if (vis) ctx.moveTo(q[0], q[1]);
      prev = vis ? q : null;
    }
    ctx.stroke(); ctx.setLineDash([]);
  }

  function label(v, text, front, color, font) {
    const q = onSphere(v);
    if ((q[2] >= 0) !== front) return;
    ctx.fillStyle = color; ctx.font = font; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(text, q[0], q[1]);
  }

  function drawSphere(front) {
    const S = sphereRadius() * zoom;
    if (!front) {
      ctx.strokeStyle = "#2a3550"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(W / 2 + pan[0], H / 2 + pan[1], S, 0, 2 * Math.PI); ctx.stroke();
      starScreen = [];
    }
    const eps = SKY.OBLIQUITY;
    if (opt.showEquator) {
      greatCircle((a) => eqToEcl(a, 0, eps), front, front ? "rgba(90,160,255,0.75)" : "rgba(90,160,255,0.3)", 1.2, [3, 4]);
      label(eqToEcl(0, 90, eps), "N celestial pole", front, "rgba(120,180,255,0.9)", "11px system-ui, sans-serif");
      label(eqToEcl(0, -90, eps), "S celestial pole", front, "rgba(120,180,255,0.9)", "11px system-ui, sans-serif");
    }
    greatCircle((l) => unit(l, 0), front, front ? "rgba(231,184,74,0.8)" : "rgba(231,184,74,0.3)", 1.4, [3, 4]);
    if (opt.showZodiac) {
      for (let l = 0; l < 360; l += 30) {
        const a = onSphere(unit(l, -3)), b = onSphere(unit(l, 3));
        if ((a[2] >= 0) === front) {
          ctx.strokeStyle = "rgba(231,184,74,0.6)"; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
        }
      }
      SIGNS.forEach((g, i) => label(unit(i * 30 + 15, -6), g, front, front ? "#e7b84a" : "rgba(231,184,74,0.4)", "15px system-ui, sans-serif"));
      label(unit(0, 6), "equinox", front, "#e7b84a", "11px system-ui, sans-serif");
    }
    if (opt.showStars) {
      STARS.forEach((r, i) => {
        const q = onSphere(unit(starLon(r), r[4] / 60));
        if ((q[2] >= 0) !== front) return;
        const m = r[5] === 9 ? 3.5 : Math.min(r[5], 6);
        const size = r[5] === 9 ? 1.6 : 3.1 - 0.42 * m;
        const zod = ZODIAC.includes(r[1]);
        ctx.fillStyle = r[5] === 9 ? "rgba(200,200,255,0.5)" : zod ? "#ffe9b0" : "#e8eefc";
        ctx.globalAlpha = front ? 1 : 0.35;
        ctx.beginPath(); ctx.arc(q[0], q[1], Math.max(0.7, size), 0, 2 * Math.PI); ctx.fill();
        ctx.globalAlpha = 1;
        if (front) {
          starScreen.push([q[0], q[1], i]);
          if (NAMES[r[7]] && r[5] <= 1) {
            ctx.fillStyle = "rgba(200,210,235,0.75)"; ctx.font = "10px system-ui, sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "bottom";
            ctx.fillText(NAMES[r[7]], q[0] + 4, q[1] - 2);
          }
        }
      });
      if (opt.showConst)
        CENTROIDS.forEach(([c, lon, lat]) =>
          label(unit(SKY.starLongitude(lon, days, starRate), lat + (lat > 0 ? 9 : -9)), CONST[c][1], front, front ? "rgba(255,233,176,0.85)" : "rgba(255,233,176,0.3)", "italic 11px system-ui, sans-serif"));
    }
    if (front && selected !== null) {
      const r = STARS[selected], q = onSphere(unit(starLon(r), r[4] / 60));
      ctx.strokeStyle = "#ff7b72"; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(q[0], q[1], 7, 0, 2 * Math.PI); ctx.stroke();
    }
  }

  function drawTrail(name, k) {
    const b = BODIES[name];
    const span = trailMode === "long" ? b.trailDays : b.synodic;
    const start = Math.floor((days - span) / b.step) * b.step;
    ctx.beginPath();
    let first = true;
    for (let t = start; t < days; t += b.step) {
      const s = toScreen(P.bodyState(name, t).pos, k);
      if (first) { ctx.moveTo(s[0], s[1]); first = false; } else ctx.lineTo(s[0], s[1]);
    }
    const s = toScreen(P.bodyState(name, days).pos, k);
    ctx.lineTo(s[0], s[1]);
    ctx.strokeStyle = alpha(b.color, 0.45);
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function drawBody(st) {
    const name = st.name;
    const b = BODIES[name];
    const k = bodyScale(name);
    const faint = alpha(b.color, 0.35);
    const mid = alpha(b.color, 0.65);
    const origin = [0, 0];

    if (trailMode !== "off") drawTrail(name, k);
    if (opt.showDeferent) {
      circle(st.center, st.R, k, faint, 1);
      mark(st.center, k, mid, "plus");
      if (st.crank) circle(st.crank.center, st.crank.radius, k, faint, 1, [2, 3]);
      if (name === "Moon") circle(origin, P.MOON.e, k, faint, 1, [2, 3]);
    }
    if (opt.showEquant && st.equant) {
      mark(st.equant, k, mid, "cross");
      line(st.equant, st.epi, k, faint, 1, [5, 4]);
    }
    if (opt.showEquant && st.prosneusis) {
      mark(st.prosneusis, k, mid, "diamond");
      line(st.prosneusis, st.epi, k, faint, 1, [5, 4]);
    }
    if (opt.showEpicycle && st.epi) {
      circle(st.epi, st.r, k, mid, 1.2);
      line(st.epi, st.pos, k, mid, 1.2);
      const c = toScreen(st.epi, k);
      ctx.fillStyle = mid;
      ctx.beginPath(); ctx.arc(c[0], c[1], 2, 0, 2 * Math.PI); ctx.fill();
    }
    if (opt.showSight) line(origin, st.pos, k, alpha(b.color, 0.25), 1);

    let s = toScreen(st.pos, k);
    if (view3d && L.INCLINATION[name] !== undefined || view3d && L.NORTHERN_LIMIT[name] !== undefined) {
      const beta = L.latitudeOf(st), d = Math.hypot(st.pos[0], st.pos[1]);
      const lifted = [st.pos[0], st.pos[1], d * Math.tan(beta * RAD)];
      line(st.pos, lifted, k, alpha(b.color, 0.6), 1, [2, 2]);
      s = toScreen(lifted, k);
    }
    ctx.fillStyle = b.color;
    ctx.shadowColor = b.color;
    ctx.shadowBlur = name === "Sun" ? 14 : 6;
    ctx.beginPath(); ctx.arc(s[0], s[1], b.size, 0, 2 * Math.PI); ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = b.color;
    ctx.font = "12px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "bottom";
    ctx.fillText(name, s[0] + b.size + 3, s[1] - 2);
  }

  function drawEarth() {
    const [x, y] = toScreen([0, 0], 1);
    ctx.fillStyle = "#3fa7d6";
    ctx.beginPath(); ctx.arc(x, y, 6, 0, 2 * Math.PI); ctx.fill();
    ctx.strokeStyle = "#7cc6a4";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  function draw(states) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (view3d) drawSphere(false);
    else if (opt.showZodiac) drawZodiac();
    const shown = focus === "All" ? ORDER : [focus];
    shown.forEach((n) => drawBody(states[n]));
    drawEarth();
    if (view3d) drawSphere(true);
  }

  // ---- readouts -----------------------------------------------------------
  const pad = (n, w = 2) => String(n).padStart(w, "0");
  function formatDate(d) {
    const y = d.getUTCFullYear();
    const ys = y < 0 ? "-" + pad(-y, 4) : pad(y, 4);
    return `${ys}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())} UTC`;
  }

  function formatLon(lon) {
    const sign = Math.floor(lon / 30) % 12;
    const within = lon - sign * 30;
    let deg = Math.floor(within);
    let min = Math.round((within - deg) * 60);
    if (min === 60) { deg += 1; min = 0; }
    return `${SIGNS[sign]} ${pad(deg)}\u00B0${pad(min)}\u2032`;
  }

  function formatSpeed(x) {
    const units = [[31557600, "yr"], [2629800, "mo"], [604800, "wk"], [86400, "d"], [3600, "h"], [60, "min"], [1, "s"]];
    const [div, unit] = units.find(([d]) => x >= d) || units[units.length - 1];
    const v = x / div;
    const vs = v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2);
    const mult = x < 1000 ? x.toFixed(x < 10 ? 1 : 0) : x.toExponential(1).replace("e+", "e");
    return `1 s = ${vs} ${unit}  (\u00D7${mult})`;
  }

  const rows = {};
  const tbody = $("table");
  ORDER.forEach((n) => {
    const tr = document.createElement("tr");
    tr.className = "body";
    tr.innerHTML = `<td><span class="dot" style="background:${BODIES[n].color}"></span>${n}</td><td class="num"></td><td class="num"></td><td class="num"></td>`;
    tr.addEventListener("click", () => setFocus(focus === n ? "All" : n));
    tbody.appendChild(tr);
    rows[n] = tr;
  });

  let lastTable = -Infinity;
  function updateReadouts(states, now) {
    const d = P.dateFromDays(days);
    $("date").textContent = isNaN(d.getTime()) ? "out of range" : formatDate(d);
    const jd = days + P.EPOCH_JD;
    $("dateSub").textContent = `JD ${jd.toFixed(3)} \u00B7 Nabonassar day ${days.toFixed(2)} \u00B7 proleptic Gregorian`;
    if (now - lastTable < 100) return;
    lastTable = now;
    if (view3d) updateSphereReadouts();
    ORDER.forEach((n) => {
      const cells = rows[n].children;
      cells[1].textContent = formatLon(states[n].lon);
      cells[3].textContent = L.NORTHERN_LIMIT[n] !== undefined || L.INCLINATION[n] !== undefined ? fmtDeg(L.latitudeOf(states[n])) : n === "Sun" ? "+0\u00B000\u2032" : "";
      const m = P.dailyMotion(n, days);
      cells[2].innerHTML = `${m >= 0 ? "+" : ""}${m.toFixed(3)}\u00B0/d${m < 0 ? ' <span class="retro">R</span>' : ""}`;
    });
  }

  const fmtDeg = (x) => {
    const a = Math.abs(x), d = Math.floor(a), m = Math.round((a - d) * 60);
    return `${x < 0 ? "\u2212" : "+"}${m === 60 ? d + 1 : d}\u00B0${pad(m === 60 ? 0 : m)}\u2032`;
  };
  const fmtRA = (ra) => {
    const h = ra / 15, hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    return `${mm === 60 ? (hh + 1) % 24 : hh}h ${pad(mm === 60 ? 0 : mm)}m`;
  };
  function updateSphereReadouts() {
    const moved = starRate === "true" ? SKY.trueShift(days) : SKY.ptolemyShift(days);
    const lag = SKY.catalogueErrorAtEpoch() + SKY.trueShift(days) - SKY.ptolemyShift(days);
    $("precNote").textContent = `Since Ptolemy's catalogue (AD 137) the stars have moved ${fmtDeg(moved)} along the ecliptic (east is +). His predictions are ${fmtDeg(Math.abs(lag)).slice(1)} ${lag >= 0 ? "behind" : "ahead of"} the real sky at this date.`;
    if (selected === null) return;
    const r = STARS[selected], [cst, i] = [r[1], r[2]];
    const lonP = SKY.starLongitude(r[3] / 60, days, "ptolemy"), lonT = SKY.starLongitude(r[3] / 60, days, "true");
    const [ra, dec] = SKY.eclipticToEquatorial(lonT, r[4] / 60, SKY.trueObliquity(days));
    const mag = r[5] === 7 ? "faint" : r[5] === 9 ? "nebulous" : `${r[5]}${r[6] === "b" ? " (brighter)" : r[6] === "f" ? " (fainter)" : ""}`;
    $("starInfo").innerHTML = [
      `<b style="color:var(--text)">${NAMES[r[7]] ? NAMES[r[7]] + " \u00B7 " : ""}${CONST[cst][0]} (${CONST[cst][1]}), star ${i}</b> \u00B7 no. ${r[0]} of the catalogue`,
      `His description: <i>${r[11]}</i>, \u201C${r[12]}\u201D <span style="opacity:.7">(Latin of Baily 1843${/east|west/.test(r[12]) ? "; western = leading in the daily turn" : ""})</span>`,
      `Ptolemy, AD 137: ${formatLon(r[3] / 60)}, latitude ${fmtDeg(r[4] / 60)}, magnitude ${mag}`,
      `At this date, by his precession: ${formatLon(lonP)}`,
      `The real sky at this date: ${formatLon(lonT)}, RA ${fmtRA(ra)}, Dec ${fmtDeg(dec)}`,
      r[7] ? `Hipparcos ${r[7]} (V = ${r[8].toFixed(1)}). His position is off by ${Math.round(Math.hypot(r[9] * Math.cos((r[4] / 60) * RAD), r[10]))}\u2032 after removing his 1\u00B0 precession error.` : "No modern star matches this entry.",
    ].join("<br>");
  }

  // ---- controls -----------------------------------------------------------
  const speedInput = $("speed");
  function setSpeed(x) {
    speed = Math.min(1e10, Math.max(1, x));
    speedInput.value = String(Math.round(Math.log10(speed) * 100));
    $("speedLabel").textContent = formatSpeed(speed);
  }
  speedInput.addEventListener("input", () => {
    speed = 10 ** (Number(speedInput.value) / 100);
    $("speedLabel").textContent = formatSpeed(speed);
  });
  document.querySelectorAll("[data-speed]").forEach((b) =>
    b.addEventListener("click", () => setSpeed(Number(b.dataset.speed))));

  $("play").addEventListener("click", () => {
    playing = !playing;
    $("play").textContent = playing ? "Pause" : "Play";
    $("play").classList.toggle("on", playing);
  });
  $("reverse").addEventListener("click", () => {
    direction = -direction;
    $("reverse").classList.toggle("on", direction < 0);
  });
  $("now").addEventListener("click", () => { days = P.daysFromDate(new Date()); });

  function jump() {
    const m = $("jump").value.trim().match(/^(-?\d{1,6})-(\d{1,2})-(\d{1,2})$/);
    if (!m) { $("jump").style.borderColor = "#ff7b72"; return; }
    const [y, mo, dd] = [Number(m[1]), Number(m[2]), Number(m[3])];
    const d = new Date(Date.UTC(2000, 0, 1));
    d.setUTCFullYear(y, mo - 1, dd);
    if (isNaN(d.getTime()) || d.getUTCFullYear() !== y || d.getUTCMonth() !== mo - 1 || d.getUTCDate() !== dd) {
      $("jump").style.borderColor = "#ff7b72";
      return;
    }
    $("jump").style.borderColor = "";
    days = P.daysFromDate(d);
  }
  $("go").addEventListener("click", jump);
  $("jump").addEventListener("keydown", (e) => { if (e.key === "Enter") jump(); });

  function resetView() { zoom = 1; pan = [0, 0]; yaw = VIEW0.yaw; tilt = VIEW0.tilt; }
  function setView(three) {
    view3d = three;
    $("vFlat").classList.toggle("on", !three); $("v3d").classList.toggle("on", three);
    $("sphereOpts").hidden = $("starBox").hidden = !three;
    $("hint").textContent = three
      ? "Drag to turn the sphere, scroll to zoom, double-click to reset. Click a star for its catalogue entry."
      : "Scroll to zoom, drag to pan, double-click to reset. Click a body in the table to isolate it.";
    resetView(); lastTable = -Infinity;
  }
  $("vFlat").addEventListener("click", () => setView(false));
  $("v3d").addEventListener("click", () => setView(true));
  $("starRate").addEventListener("change", () => { starRate = $("starRate").value; lastTable = -Infinity; });
  function setFocus(n) {
    focus = n;
    focusSel.value = n;
    resetView();
  }
  focusSel.addEventListener("change", () => setFocus(focusSel.value));
  $("scale").addEventListener("change", () => { scaleMode = $("scale").value; resetView(); });

  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left - W / 2, my = e.clientY - rect.top - H / 2;
    const f = Math.exp(-e.deltaY * 0.0015);
    const nz = Math.min(500, Math.max(0.2, zoom * f));
    const g = nz / zoom;
    pan = [mx - (mx - pan[0]) * g, my - (my - pan[1]) * g];
    zoom = nz;
  }, { passive: false });
  let drag = null;
  let last = null, travel = 0;
  canvas.addEventListener("pointerdown", (e) => {
    last = [e.clientX, e.clientY]; travel = 0;
    drag = [e.clientX - pan[0], e.clientY - pan[1]];
    canvas.setPointerCapture(e.pointerId);
    canvas.classList.add("dragging");
  });
  // In 3-D, dragging right turns the near side right and dragging down tips it down.
  canvas.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - last[0], dy = e.clientY - last[1];
    last = [e.clientX, e.clientY]; travel += Math.abs(dx) + Math.abs(dy);
    if (!view3d) { pan = [e.clientX - drag[0], e.clientY - drag[1]]; return; }
    yaw += dx * 0.008;
    tilt = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, tilt - dy * 0.008));
  });
  canvas.addEventListener("pointerup", (e) => {
    if (drag && view3d && travel < 5 && opt.showStars) {
      const rect = canvas.getBoundingClientRect(), x = e.clientX - rect.left, y = e.clientY - rect.top;
      let best = null, bd = 100;
      starScreen.forEach(([sx, sy, i]) => { const d = (sx - x) ** 2 + (sy - y) ** 2; if (d < bd) { bd = d; best = i; } });
      selected = best;
      lastTable = -Infinity;
    }
    drag = null; canvas.classList.remove("dragging");
  });
  canvas.addEventListener("dblclick", resetView);

  // ---- loop ---------------------------------------------------------------
  function frame(now) {
    const dt = Math.min(0.1, (now - lastFrame) / 1000);
    lastFrame = now;
    if (playing) days += (direction * speed * dt) / 86400;
    const states = {};
    P.state(days).forEach((s) => { states[s.name] = s; });
    draw(states);
    updateReadouts(states, now);
    requestAnimationFrame(frame);
  }

  resize();
  setSpeed(1);
  requestAnimationFrame(frame);
})();
