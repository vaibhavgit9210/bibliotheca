# bibliotheca — GATE mock tests

Repo `vaibhavgit9210/bibliotheca`. Full-length GATE papers as browser mock tests, graded against the official answer keys.

> ⚠️ **Not deployed. Do not push without asking.** Commit locally only — that was an explicit instruction on 9 Aug 2026. The CS1-only version was live at https://vaibhavkumar.is-a.dev/bibliotheca/ before the two-paper restructure, so the remote is now *behind* local. When a push is authorised, push **both** `main` and `main:gh-pages`.

## Mock roster — what's built, what's solved

Update the Status column as you sit each paper, so the next batch doesn't repeat one.

| Mock | Session | Source | Status | Score | Attempted |
|---|---|---|---|---|---|
| GATE 2026 CS1 | 3 | official paper + key | **built · unsolved** | — | — |
| GATE 2026 CS2 | 4 | official paper + key | **built · unsolved** | — | — |

### Deliberately not built (checked 9 Aug 2026 — don't re-research these)

| Candidate | Why not |
|---|---|
| GATE 2026 DA (Data Science & AI) | Paper + key **are** live at the 2026 site and would build with `build.py` in minutes. Out of scope by your call; it's not in the `padhai` plan (that plan's lane is GATE **CS**). Reconsider only if DA becomes a target. |
| GATE 2025 / 2024 / earlier | Past organising-institute sites are **404** (`gate2025.iitr.ac.in`, `gate2024.iisc.ac.in`). PYQs exist on GATE Overflow but not as official PDF + key pairs, so the coordinate pipeline can't run on them. Would need a mirror hunt. |
| RBI Grade B · SEBI Grade A · NABARD Grade A · IRDAI · IB ACIO | These bodies **never publish question papers or answer keys**. Any mock would be AI-authored questions with an AI-authored key — a different fidelity class from everything here. Also contradicts the `padhai` one-lane rule: GATE owns Aug–Dec 2026, and the plan says *read the notification PDFs, don't enrol*. |

Plan context lives in `~/Documents/personal/job/padhai/` (private repo): `gov-exams-study-plan.md` §3 is the sequencing calendar. The only live calendar item as of Aug 2026 is **GATE 2027 registration, 14 Aug – 21 Sep 2026**.

## Layout

```
index.html        hub — paper picker, reads each attempt's status from localStorage
test.html         the exam app for every paper; ?p=cs1|cs2 selects one
q/<paper>/qNN.webp   65 question images per paper
exam-<paper>.json    machine-readable key (reference; runtime uses the inlined copy)
build.py          regenerates images + key JSON from the official PDFs
```

No build step for serving, no dependencies, house style. `build.py` is a one-off asset generator, not part of the page.

## Adding a paper

1. Add an entry to `PAPERS` in `build.py` (id, title, session, paper URL, key URL) and run `python3 build.py <id>`. It asserts 65 questions and 100 marks, so a bad parse fails loudly rather than shipping.
2. Add the same id to `PAPERS` in `test.html` — paste the answer literal generated from `exam-<id>.json` (rows are `[n, type, section, marks, answer]`; answer is `"ACD"` for MCQ/MSQ, `[lo, hi]` for NAT).
3. Add it to the `PAPERS` list in `index.html`.
4. Add a roster row above.

**The key exists in two places** — `exam-<id>.json` and the inlined `PAPERS[id].data` in `test.html`. Only the inlined copy is used at runtime (a `fetch` would break under `file://`). Change one, change the other.

## Marking scheme (`gradeOne` in test.html)

MCQ wrong → `−marks/3` (−1/3 and −2/3). MSQ → all-or-nothing, no negative, no partial credit. NAT → inside `[lo, hi]`, no negative. Verified by a suite that pins a perfect attempt at exactly 100 for every paper.

## The crop pipeline (why `build.py` looks the way it does)

Questions are **images cropped by text coordinates**, not transcribed text: `pdftotext` flattens superscripts (`2³²` becomes `232`) and drops every figure, and ~20 questions per paper carry control-flow graphs, matrices, grids or code.

`pdftotext -bbox-layout` gives every word and line a bounding box in points (A4 = 595.32 × 841.92). The traps, all of which cost a debugging round:

- **Section banners collide with markers.** `Q.1 – Q.5 Carry ONE mark Each` contains a matching token, and taking the first match per number picks the banner over the question. Skip any line containing `Carry`, and accept only the *next expected* number.
- **Label spacing differs per paper.** CS1 writes `Q.4`, CS2 writes `Q. 4`. Match `Q\.\s*(\d+)`.
- **A question's row top is not its label's y.** The label column and text column are separate `<line>`s and the text can start ~7pt higher (CS1 Q.31). Use the minimum `yMin` over lines overlapping the label's row, or the previous question's crop ends with a sliver of the next one's first line.
- **A question must not stop on itself.** The stop-point list contains its own row top; search strictly past it or every crop collapses to ~20pt.
- **The GATE logo is a top-left page *header*** (y ≈ 17–73), not a footer — easy to get backwards. With first body text at y ≥ 91.3, lowest body text at y = 749 and footer text at y = 804, the safe content band is **y 78 → 755**.
- Three questions per paper are followed by a section banner; they must stop at the banner, not at the next question. Handled generically by treating banners as stop points.

Multi-page questions get one crop per page, whitespace-trimmed and stacked with a 16px gap; strips with a dark-pixel fraction below `1e-4` are dropped. Output is 1100px-wide WebP q88, ≈3 MB per paper.

**Regression check:** rebuilding CS1 after the generalisation was pixel-identical to the previously committed images. Keep it that way — diff against `git archive` before committing a pipeline change.

## Verifying

**Grading** — extract the block between `const PAPERS = {` and the `helpers` comment from `test.html` and run it in node with `localStorage` and `location` stubbed (`{search:'?p=cs1', replace(){}}`). Tests the shipped code without shipping test hooks. Cover both papers; assert 65 questions, 100 marks, GA = 15, perfect = 100, MSQ subset/superset = 0, NAT range edges inclusive.

**Visual** — no screenshot hooks in the shipped files. Make a throwaway `_t_*.html` copy (gitignored) that appends `startExam(true); renderQ(9);` to the `refreshResume();` line, or stubs `attempt()` in `index.html` to fake a scored/in-progress state, then screenshot with headless Chrome and delete it.
