# bibliotheca

Full-length **GATE 2026** mock tests, played in the browser and graded against the official answer keys.

| Paper | Session | Questions | Marks |
|---|---|---|---|
| Computer Science & IT (CS1) | 3 | 65 | 100 |
| Computer Science & IT (CS2) | 4 | 65 | 100 |

## What it is

A CBT-style interface over the real papers: 3-hour countdown, question palette, mark-for-review, and a scorecard computed with the actual GATE marking scheme.

Questions are rendered straight from the official IIT Guwahati PDFs, so every figure, control-flow graph, matrix and code block appears exactly as it did in the exam — nothing was retyped, so nothing could be mistranscribed.

## Marking scheme

| Type | Correct | Wrong | Unattempted |
|---|---|---|---|
| MCQ · 1 mark | +1 | −1/3 | 0 |
| MCQ · 2 marks | +2 | −2/3 | 0 |
| MSQ · 1 & 2 marks | +1 / +2 | 0 | 0 |
| NAT · 1 & 2 marks | +1 / +2 | 0 | 0 |

- **MSQ** has no partial credit — every correct option must be selected and no incorrect one.
- **NAT** is graded against the official accepted range (e.g. CS1 Q.58 accepts 4.24–4.26).

Both papers split 15 marks General Aptitude / 85 marks Technical.

## Using it

Pick a paper from the landing page, answer with the on-screen options (or keys **A**–**D**), type NAT answers into the keypad, and submit. Progress is saved per paper in `localStorage`, so you can close the tab and resume; the timer auto-submits at 00:00:00.

The scorecard breaks the result down by section and question type, and the review list filters to just the ones you got wrong, each expandable to the original question.

Keyboard: **A–D** select · **←/→** navigate · **Enter** save & next.

## Layout

```
index.html           paper picker, with per-paper progress
test.html            the exam app — ?p=cs1 | ?p=cs2
q/<paper>/qNN.webp   65 question images per paper
exam-<paper>.json    machine-readable answer key
build.py             regenerates images + keys from the official PDFs
```

Regenerate assets with `python3 build.py cs1 cs2` (needs poppler and Pillow).

## Sources

Question papers and answer keys published by **IIT Guwahati**, organizing institute for GATE 2026, at [gate2026.iitg.ac.in](https://gate2026.iitg.ac.in/). Question content is their copyright and is reproduced here for personal exam practice.
