"""Build Ptolemy's star descriptions in Latin, after Baily's 1843 edition (public domain).

Source: the Almagest star catalogue page formerly at astro.isi.edu (archived by the Internet
Archive), which lists Baily's Latin description for each of the 1,028 entries in the same order as
data/ptolemy_star_catalogue.csv. Writes data/ptolemy_star_descriptions.csv with columns
number, latin, english. The English glosses are this repository's own translation of the Latin;
re-running keeps them, matched by entry number.

    python tools/build_star_descriptions.py         # download, write the CSV
    python tools/build_star_descriptions.py FILE    # use a local copy of the page
"""

import csv
import html
import io
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "ptolemy_star_descriptions.csv"
URL = "https://web.archive.org/web/2007id_/http://astro.isi.edu/reference/almagest.html"

ENTRY = re.compile(r"^\s{0,3}\d[\dI]{0,3}\s+\d+\.?\s+(\S.*)$")
CONTINUATION = re.compile(r"^\s{6,}\S")
POSITION = re.compile(r"\d{1,3} \d\d\??\s+\*?[+-]\d\d \d\d")
END = re.compile(r"\.{2,}|\s{3,}|\*?\s*\d{1,3} \d\d\??\s+\*?[+-]\d\d \d\d")

# Typing errors in the source page, checked against the Latin.
FIXES = {
    "Ausralissima": "Australissima", "Austalis": "Australis", "Horealis": "Borealis",
    "Vraecedens": "Praecedens", "Boreali sede": "Borealis de", "horeali": "boreali",
    "rhornbum": "rhombum", "reliquarium": "reliquarum", "cluarum": "duarum",
    "superrilio": "supercilio", "ociilo": "oculo", "rnedio": "medio", "dexro": "dextro",
    "ion extremo": "in extremo", "hcedi": "haedi", "circiilum": "circulum",
    "extrem itate": "extremitate", "tribue": "tribus", "qum": "quae", "subipsis": "sub ipsis",
    "antecedetibus": "antecedentibus", "sagittaea": "sagittae", "quator": "quatuor",
    "{chi eta nu iota sigma kappa o upsilon}": "chenisco",
}  # fmt: skip


def parse(text):
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    out, parts = [], None
    for line in text.split("\n"):
        m = ENTRY.match(line)
        if parts is None and m:
            parts, line = [], m.group(1)
        elif parts is None or not CONTINUATION.match(line):
            continue
        parts.append(END.split(line.strip())[0])
        if POSITION.search(line):
            latin = re.sub(r"\s+", " ", " ".join(parts)).strip().rstrip(".,")
            for bad, good in FIXES.items():
                latin = re.sub(rf"(?<!\w){re.escape(bad)}(?!\w)", good, latin)
            out.append(latin)
            parts = None
    if len(out) != 1028:
        sys.exit(f"expected 1028 entries, parsed {len(out)}")
    return out


def main(argv):
    if argv:
        text = Path(argv[0]).read_text(encoding="latin-1")
    else:
        text = urllib.request.urlopen(URL, timeout=60).read().decode("latin-1")
    english = {}
    if CSV_PATH.exists():
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            english = {r["number"]: r["english"] for r in csv.DictReader(f)}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["number", "latin", "english"])
    for i, latin in enumerate(parse(text), 1):
        w.writerow([i, latin, english.get(str(i), "")])
    CSV_PATH.write_text(buf.getvalue(), encoding="utf-8")
    print(f"1028 entries -> {CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
