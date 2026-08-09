#!/usr/bin/env python3
"""Cut a GATE paper into per-question images + a machine-readable answer key.

    python3 build.py cs1 cs2

Needs poppler (`brew install poppler`) for pdftotext/pdftoppm, and Pillow.
Writes q/<paper>/qNN.webp and exam-<paper>.json. Downloaded PDFs are cached
in .cache/ and are not committed.

Why coordinates and not text: pdftotext flattens superscripts (2^32 renders as
"232") and drops every figure, so the questions are cropped as images instead.
See CLAUDE.md for the traps this code works around.
"""
import json, re, subprocess, sys, urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

ROOT = Path(__file__).parent
CACHE = ROOT / ".cache"

PAPERS = {
    "cs1": dict(
        title="Computer Science & IT (CS1)", session=3,
        qp="https://gate2026.iitg.ac.in/doc/download/2026/QPs/CS1.pdf",
        key="https://gate2026.iitg.ac.in/doc/download/2026/Keys/CS1_Keys.pdf"),
    "cs2": dict(
        title="Computer Science & IT (CS2)", session=4,
        qp="https://gate2026.iitg.ac.in/doc/download/2026/QPs/CS2.pdf",
        key="https://gate2026.iitg.ac.in/doc/download/2026/Keys/CS2_Keys.pdf"),
}

# page geometry, in points (A4 = 595.32 x 841.92)
TOP, BOT = 78.0, 755.0   # content band: below the top-left GATE logo (ends y=73), above the footer (y=804)
X0, X1 = 60, 540
PAD = 8.0                # clearance above a row top, so no sliver of the next question bleeds in
DPI = 200
MAXW = 1100

LINE = re.compile(r'<line xMin="[\d.]+" yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">(.*?)</line>', re.S)
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="[\d.]+" yMax="[\d.]+">(.*?)</word>')


def fetch(url, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  downloading {url}")
        urllib.request.urlretrieve(url, dest)
    return dest


def parse_key(pdf):
    """Answer-key table -> [{n, type, section, marks, answer}]. NAT answers are [lo, hi]."""
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    out = {}
    for line in txt.splitlines():
        m = re.match(r"\s*(\d{1,2})\s+\d\s+(MCQ|MSQ|NAT)\s+(GA|CS-\d)\s+(.+?)\s+([12])\s*$", line)
        if not m:
            continue
        n, typ, sec, key, marks = int(m[1]), m[2], m[3], m[4].strip(), int(m[5])
        if typ == "NAT":
            lo, hi = re.match(r"([-\d.]+)\s*to\s*([-\d.]+)", key).groups()
            ans = [float(lo), float(hi)]
        else:
            ans = "".join(s.strip() for s in key.split(";"))
        out[n] = dict(n=n, type=typ, section="GA" if sec == "GA" else "CS", marks=marks, answer=ans)
    missing = [i for i in range(1, 66) if i not in out]
    if missing:
        raise SystemExit(f"answer key: missing questions {missing}")
    return [out[i] for i in range(1, 66)]


def layout(pdf):
    """-> {page: [(yMin, yMax, text)]} sorted by y."""
    bbox = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    pages = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', bbox, re.S)
    return {i: sorted((float(a), float(b), " ".join(w for _, w in WORD.findall(body)))
                      for a, b, body in LINE.findall(p))
            for i, p in enumerate(pages, 1)}


def question_starts(pg):
    """Locate Q.1..Q.65 in document order.

    Two traps: section banners ("Q.1 - Q.5 Carry ONE mark Each") contain matching
    tokens, and a plain first-match-per-number picks the banner over the question.
    So: skip any line containing "Carry", and accept only the next expected number.
    """
    cands = []
    for p in sorted(pg):
        for ymin, _, text in pg[p]:
            if "Carry" in text:
                continue
            m = re.match(r"Q\.\s*(\d+)\b", text)   # CS1 writes "Q.4", CS2 writes "Q. 4"
            if m and float(ymin) > 40:
                cands.append((p, ymin, int(m[1])))
    pos, expect = {}, 1
    for p, y, n in cands:
        if n == expect:
            pos[n] = (p, y)
            expect += 1
    missing = [i for i in range(1, 66) if i not in pos]
    if missing:
        raise SystemExit(f"question markers: missing {missing}")
    return pos


def row_top(pg, page, y):
    """True top of a question's row.

    pdftotext emits the "Q.N" label column and the text column as separate lines,
    and the text column can start ~7pt higher (CS1 Q.31 does). Taking the label's
    y would leave a sliver of this question at the bottom of the previous crop.
    """
    c = [a for a, b, _ in pg[page] if a > 40 and a < y + 4 and b > y - 4]
    return min(c) if c else y


def stops(pg, pos):
    """Every point a question must stop at: the next question's row top, or a
    section banner (three questions in each paper are followed by one)."""
    pts = [(p, row_top(pg, p, y)) for p, y in pos.values()]
    pts += [(p, ymin) for p in pg for ymin, _, t in pg[p] if "Carry" in t]
    return sorted(set(pts))


def trim(im):
    g = im.convert("L")
    bb = ImageChops.difference(g, Image.new("L", g.size, 255)).point(
        lambda v: 255 if v > 18 else 0).getbbox()
    if not bb:
        return None
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - 14), max(0, y0 - 12),
                    min(im.width, x1 + 14), min(im.height, y1 + 12)))


def render(pdf, page, y0, y1, tag):
    s = DPI / 72.0
    out = CACHE / f"{tag}"
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-f", str(page), "-l", str(page),
                    "-x", str(int(X0 * s)), "-y", str(int(y0 * s)),
                    "-W", str(int((X1 - X0) * s)), "-H", str(int((y1 - y0) * s)),
                    "-singlefile", str(pdf), str(out)], check=True)
    return Image.open(f"{out}.png").convert("RGB")


def build(paper):
    meta = PAPERS[paper]
    print(f"{paper}: {meta['title']}")
    qp = fetch(meta["qp"], CACHE / f"{paper}.pdf")
    key = fetch(meta["key"], CACHE / f"{paper}_keys.pdf")

    exam = parse_key(key)
    total = sum(q["marks"] for q in exam)
    if total != 100:
        raise SystemExit(f"{paper}: key totals {total} marks, expected 100")
    (ROOT / f"exam-{paper}.json").write_text(json.dumps(exam, indent=1))

    pg = layout(qp)
    pos = question_starts(pg)
    stop = stops(pg, pos)
    outdir = ROOT / "q" / paper
    outdir.mkdir(parents=True, exist_ok=True)

    for n in range(1, 66):
        p0, ylab = pos[n]
        rt = row_top(pg, p0, ylab)
        start = max(TOP, rt - PAD)
        # strictly past this question's own row top, else it stops on itself
        nxt = next(((p, y) for p, y in stop if (p, y) > (p0, rt + 0.5)), None)
        p1, y1 = nxt if nxt else (max(pg), BOT)
        y1 = min(BOT, y1 - PAD)

        if p0 == p1:
            spans = [(p0, start, max(start + 20, y1))]
        else:
            spans = [(p0, start, BOT)] + [(p, TOP, BOT) for p in range(p0 + 1, p1)]
            if y1 > TOP + 8:
                spans.append((p1, TOP, y1))

        parts = []
        for i, (p, a, b) in enumerate(spans):
            im = render(qp, p, a, b, f"{paper}_{n:02d}_{i}")
            if (np.asarray(im.convert("L")) < 160).mean() < 1e-4:
                continue                      # blank continuation strip
            t = trim(im)
            if t and t.height > 16:
                parts.append(t)
        if not parts:
            raise SystemExit(f"{paper} Q{n}: produced no image")

        w = max(p.width for p in parts)
        h = sum(p.height for p in parts) + 16 * (len(parts) - 1)
        canvas = Image.new("RGB", (w, h), "white")
        y = 0
        for p in parts:
            canvas.paste(p, (0, y))
            y += p.height + 16
        if canvas.width > MAXW:
            canvas = canvas.resize((MAXW, round(canvas.height * MAXW / canvas.width)), Image.LANCZOS)
        canvas.save(outdir / f"q{n:02d}.webp", quality=88, method=6)

    size = sum(f.stat().st_size for f in outdir.glob("*.webp"))
    print(f"  65 questions, 100 marks, {size/1e6:.1f} MB -> q/{paper}/")


if __name__ == "__main__":
    for p in sys.argv[1:] or PAPERS:
        if p not in PAPERS:
            raise SystemExit(f"unknown paper {p!r}; known: {', '.join(PAPERS)}")
        build(p)
