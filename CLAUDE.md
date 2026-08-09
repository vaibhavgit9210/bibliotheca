# bibliotheca — GATE 2026 CS1 mock test

Repo `vaibhavgit9210/bibliotheca`, live at https://vaibhavkumar.is-a.dev/bibliotheca/ (Pages from `gh-pages` — push **both** `main` and `main:gh-pages`).

`index.html` is the whole app: no build step, no dependencies, house style. Questions are images in `q/`, so the app never parses PDFs at runtime.

## Two copies of the answer key — keep them in sync

The key lives in **both** `exam.json` (machine-readable) and the inlined `QDATA` array at the top of the `<script>` in `index.html`. Only `QDATA` is used at runtime; `exam.json` is reference. Change one, change the other.

`QDATA` rows are `[n, type, section, marks, answer]` where answer is `"ACD"` for MCQ/MSQ (letters concatenated) and `[lo, hi]` for NAT.

## Marking scheme (implemented in `gradeOne`)

MCQ wrong → `−marks/3` (so −1/3 and −2/3). MSQ → all-or-nothing, no negative. NAT → inside `[lo, hi]`, no negative. Verified by a test suite that pins a perfect attempt at exactly 100.

## Regenerating the question images

The non-obvious part. Source PDFs:
`https://gate2026.iitg.ac.in/doc/download/2026/QPs/CS1.pdf` and `.../Keys/CS1_Keys.pdf`.

Crops are cut by **text coordinates**, not by eyeballing pixels:

1. `pdftotext -bbox-layout CS1.pdf bbox.html` gives every word and line with a bounding box, in points (page is 595.32 × 841.92).
2. Find each question's start: scan `<line>` elements in document order for a word matching `Q\.\d+` at `xMin < 120`, and accept it only if it's the **next expected** number. Two traps: the section banners (`Q.1 – Q.5 Carry ONE mark Each`) contain matching tokens — skip any line containing `Carry`; and taking the first match per number picks up the banner instead of the question.
3. A question's real top is **not** its `Q.N` label's y. pdftotext emits the label column and the text column as separate `<line>`s, and the text column can start ~7pt higher (Q.31 does). Use the minimum `yMin` over lines overlapping the label's row — otherwise the *previous* question's crop ends with a sliver of the next question's first line.
4. Page bands: header text ends at y=37, the **GATE logo is a top-left page header** at y≈17–73 (not a footer — this one is easy to get backwards), first body text is at y≥91.3, lowest body text is y=749, footer text starts at y=804. So the safe content band is **y 78 → 755**.
5. Crop with `pdftoppm -r 200 -x -y -W -H -singlefile` over x = 60→540pt. Questions that span pages get one crop per page, whitespace-trimmed and stacked with a 16px gap. Drop any strip whose dark-pixel fraction is `< 1e-4` (blank continuation rows).
6. Special-case Q5, Q10 and Q35: each is followed by a section banner, so end those crops at the banner's y instead of the next question's.
7. Resize to 1100px wide, save WebP quality 88 → ~3.1 MB for all 65.

## Verifying

Grading logic — extract the block between `const QDATA=[` and the `helpers` comment out of `index.html` and run it in node with a `localStorage` stub. That tests the shipped code without shipping test hooks.

Visual — the app has no screenshot hooks; make a throwaway copy that appends `startExam(true); renderQ(42);` (or fills `S.ans` then calls `doSubmit(false)`) to the `refreshResume();` line, screenshot it with headless Chrome, then delete the copy.
