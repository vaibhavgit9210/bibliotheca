# bibliotheca

Full-length **GATE 2026 Computer Science & IT (CS1)** mock test, played in the browser and graded against the official answer key.

**Live:** https://vaibhavkumar.is-a.dev/bibliotheca/

## What it is

The complete 65-question paper (Session 3) with a CBT-style interface: 3-hour countdown, question palette, mark-for-review, and a scorecard computed with the real GATE marking scheme.

Questions are rendered straight from the official PDF, so every figure, control-flow graph, matrix and code block appears exactly as it did in the exam — nothing was retyped, so nothing could be mistranscribed.

## Marking scheme

| Type | Correct | Wrong | Unattempted |
|---|---|---|---|
| MCQ · 1 mark | +1 | −1/3 | 0 |
| MCQ · 2 marks | +2 | −2/3 | 0 |
| MSQ · 1 & 2 marks | +1 / +2 | 0 | 0 |
| NAT · 1 & 2 marks | +1 / +2 | 0 | 0 |

- **MSQ** has no partial credit — every correct option must be selected and no incorrect one.
- **NAT** is graded against the official accepted range (e.g. Q.58 accepts 4.24–4.26).

Paper composition: 65 questions / 100 marks — General Aptitude 15, Technical 85. 28 MCQ, 24 MSQ, 13 NAT.

## Using it

Start the test, answer with the on-screen options (or keys **A**–**D**), type NAT answers into the keypad, and submit. Progress is saved to `localStorage` continuously, so you can close the tab and resume; the timer auto-submits at 00:00:00.

The scorecard breaks the result down by section and question type, and the review list filters to just the ones you got wrong, each expandable to the original question.

Keyboard: **A–D** select · **←/→** navigate · **Enter** save & next.

## Layout

```
index.html    the whole app — no build step, no dependencies
q/qNN.webp    65 question images cropped from the official PDF
exam.json     machine-readable answer key (type, section, marks, answer)
```

## Sources

- Question paper — [GATE 2026 CS1](https://gate2026.iitg.ac.in/doc/download/2026/QPs/CS1.pdf)
- Answer key — [GATE 2026 CS1 keys](https://gate2026.iitg.ac.in/doc/download/2026/Keys/CS1_Keys.pdf)

Both published by IIT Guwahati, the organizing institute for GATE 2026. Question content is their copyright and is reproduced here for personal exam practice.
