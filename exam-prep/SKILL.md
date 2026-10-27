---
name: exam-prep
description: Build a complete, exam-driven study kit for a university course from its materials (lecture script, slides, recordings, homework, past exams). The kit has a frequency analysis of past exams, a day-by-day study plan, a dense 1–2 page cheatsheet, narrated 3Blue1Brown-style theory and worked-example videos, practice sheets with answer keys and solutions, and a mock exam. Use this skill whenever the user wants to prepare for an exam, revise a course, make a study plan, a cheatsheet or summary sheet, exam-prep videos, exercise or practice sheets, or a mock exam, or wants past exams analysed for what comes up most, even if they don't say "skill". Also use it when continuing a prep project made with it (a folder with `prep/dayNN/` and `prep-videos/`).
---

# Exam prep

Turn a course folder into a study kit organised around what the exam actually asks:

```
<course>/
  cheatsheet/cheatsheet.tex/.pdf        dense summary, if the exam allows one
  prep/plan.md                          day-by-day plan with topics, videos and sheets
  prep/dayNN/                           per day: Video A (theory), Video B (worked examples),
                                        practice PDF, README, video-info.md
  prep/mock/                            timed mock exam at the end
  prep-videos/                          ManimGL project that renders all videos (git repo)
    script/frequencies.md               exam-frequency table (source of every badge)
```

The method has three parts:
- **Frequency first.** Count how many past papers contain each question type, then let the counts
  decide what gets screen time, which questions go in the sheets, and which recipes go on the
  cheatsheet. Every question in a video or PDF shows its count as a badge: "In exams: 3/8 papers ·
  medium".
- **One day = 1–2 hours.** Each day has a theory video (~15–20 min), a worked-examples video
  (~12–15 min) ending in pause-and-solve questions, and a practice sheet (~45 min) that matches the
  real exam's format, with an answer key, a self-check and solutions that point back to the
  timestamps of the lecture recordings.
- **Everything verified.** Every number in a video or sheet comes from an exact computation that
  you ran, and every answer in the key is checked numerically or by an explicit derivation.

The videos use the `explainer-video` skill (ManimGL, Piper narration, `NarratedScene` with
`[cue]` timing); read its SKILL.md once before building the first video. This skill adds a course
layer on top of it: `video-kit/` (shared scene pieces, a playlist build that turns many scenes into
one video per day with subtitles, chapters and metadata) and the LaTeX templates in `templates/`.

## 1. Gather what's missing, in one go

Check what the user already said, then ask once, compactly, only for what's missing:

- **Course folder** and what's in it (script, slides, recordings, homework, past exams).
- **Exam**: date, duration, format (multiple choice / true-false / open questions / numeric),
  allowed aids (cheatsheet size and rules, e.g. "2 A4 pages, handwritten?", calculator). Past
  exams usually answer the format question; read them before asking.
- **Scope**: which topics have been lectured so far. Default: build only lectured topics and add
  later ones as the course goes on.
- **Language** of videos and sheets (default: the course language). For a non-English narrator,
  pick a Piper voice with public-domain/CC0 training data and check its MODEL_CARD.
- **Voice**: Piper (publish-safe) or a designed Breeze TTS 2 voice (more natural; non-commercial
  licence, fine for personal study videos). For Breeze, design 2–3 candidates on a real intro
  paragraph and let the user pick; then follow "Breeze voice" in the explainer template's AGENTS.md.
- **Time budget**: days until the exam, hours per day (default 1–2 h per study day).
- **Autonomy**: may you run unattended (e.g. overnight) without checkpoints? If yes, skip the ★
  stops below, make the calls yourself and list every decision in the final report.

Don't ask about resolution, colours, encoding or file naming; use the defaults here.

## 2. Organise the materials

Work on copies or renames inside the course folder, and never delete. Move duplicates to the trash
(`trash-put`), and only after comparing size, duration and content.

1. **Rename by date** so that sorting is chronological: `YYYY-MM-DD lecture N - topic.pdf`,
   `YYYY-MM-DD exam - questions.pdf` / `- solutions.pdf`. Get the dates from the files themselves
   (title pages, exam headers), the course page or the metadata. Exam files often have misleading
   names: work out each paper's real date and drop duplicates (the same exam under two names).
2. **Recordings**: list them, check lengths against the course page, number them in order
   (`NN lecture - topic.mp4`), then transcribe them with timestamps into `transcripts/` (`.txt` with
   `[hh:mm:ss]` paragraphs plus `.srt`). If the user has a local whisper tool
   (e.g. a `transcribe.sh OUT FILES --language xx` script), use it; otherwise
   use faster-whisper large-v3 on the GPU. Run it in the background while you read. The transcripts
   are what make the "Revisit: L03 01:04:14" pointers in the solutions possible.
3. Extract text from every PDF (`pdftotext -layout`) into the scratchpad for searching.

## 3. Analyse past exams → `prep-videos/script/frequencies.md`

This is the backbone; do it before planning. Template: `templates/frequencies.md`.

- List the distinct papers (N). Read every question with its official solution.
- Tag each question with a **question type** at the level of something you can practise ("variance
  of a linear combination", "is this kernel valid?"), not at the level of a chapter title.
- Count **papers**, not questions: a type appearing twice in one paper counts once. Record where
  each type appears (`2025-01 Q5`).
- Separate **direct** questions (testing the idea itself) from **as a tool** (the idea is needed
  inside another question). Both counts matter, and they get different notes on the badge.
- Levels relative to N: **high** ≥ 50% of papers, **medium** ≥ 25%, **low** below that. The
  thresholds live in `video-kit/kit.py` and in the `\freq` macro, so both stay consistent.
- Note the trends too: format changes (e.g. "MC only since 2022") and topics that dropped out of
  the syllabus. Weight recent papers more when choosing what to cover.

## 4. Plan the days → `prep/plan.md` ★

Template: `templates/plan.md`. Group the lectured topics into study days of 1–2 h each. A heavy
topic gets several days, and so several video pairs. End with a review day (mock exam). For each day,
list the subtopics, the frequency counts that justify them, and the sources (script chapter,
recordings, tutorial, homework, papers). Show the plan to the user before building anything, unless
they are running you unattended.

## 5. Cheatsheet → `cheatsheet/cheatsheet.tex` (if aids are allowed)

Template: `templates/cheatsheet.tex` (A4, 4 columns, 8.5 pt, coloured section bars). Rules:
- Respect the allowed format exactly (pages, handwritten-only rules, font size).
- One section per topic in lecture order, then a final **Exam recipes** section: step-by-step
  procedures for the high-frequency question types ("GP with 1–2 points: build K_y, invert with the
  2×2 rule, …").
- Mark traps with a red `\T` ("!"), taken from mistakes that are common in past solutions and
  from distractor answers in multiple-choice questions.
- Prioritise by frequency: high-frequency formulas in full, rare topics in one line.
- Compile with `latexmk -pdf`, check the page count, render the pages to PNG and look at them for
  overflow. Fit the space by trimming low-frequency content, not by shrinking the font below
  readability (~7.5 pt minimum).

## 6. Build a day

Create the video project once per course:
```bash
<skills-dir>/exam-prep/scripts/new_course.sh <course>/prep-videos
```
This runs explainer-video's `new_project.sh`. It then adds `scenes/kit.py`, `tools/build_video.py`,
`tools/draft.sh` and `script/playlists.json`, and copies the sheet templates into
`<course>/prep/templates/`.

Per day, in this order:

1. **Narration** in `script/narration.md`, one `## SNN Title — SceneClass` block per scene with
   `[cue]` marks. Fact-check every statement against the script and slides before animating.
   - Video A (theory): intro with the plan → one scene per concept → recap of the exam traps.
     ~150 words/min, 15–20 min in total.
   - Video B (worked examples): intro with the badge legend → 4–6 examples, each with its badge
     and a variant of a real past-exam question (cite it, e.g. "variant of Jan 2026 Q6") →
     "pause and solve" (3 questions, pause sign, then answers) → wrap-up.
   - Spell out what TTS mangles: Piper swallowed a standalone "A" ("sigma A B" came out as
     "sigma B"). Write "sigma of A and B" or "x sub A" and listen to the result, or transcribe it
     back with whisper and compare. With Breeze this check runs automatically for every sentence.
2. **Scenes**: `scenes/sNN_name.py` with `class X(NarratedScene)`, one `self.cue()` per `[cue]`,
   built from the pieces in `kit.py` (`get_header`, `get_bullets`, `get_verdict`, `get_pause_sign`,
   `get_frequency_badge`, `ProbTable`, `fit`). Add course-specific pieces (axes, ellipses, plots)
   to `kit.py`. Draft each scene with `tools/draft.sh <file> <Scene>`, then look at the contact
   sheet: overlaps, cut-off text, unreadable sizes, late-cue warnings.
3. **Playlist**: add the day to `script/playlists.json` (scenes in order, a chapter name per scene,
   a title, and a description file in `script/descriptions/`). Then run
   `python3 -I tools/build_video.py dayNNa`. It renders the scenes at 1080p, concatenates and
   encodes once, builds the `.srt`, and muxes subtitles, title, description and chapters into
   `prep/dayNN/<name>.mp4`. It also writes `<name>.info.md` with paste-ready title, description and
   chapters.
4. **Practice sheet** `prep/dayNN/dayNN-practice.tex` from `templates/practice.tex`:
   - A "how to use" box, then a key-results box (the formulas of the day).
   - ~15–20 questions in the **real exam's format** and point scale, grouped into parts, each with
     `\freq{count}{where}`. Use new variants of past questions, not copies; the index at the end
     lists the originals.
   - Choose distractors from real mistakes (swapped conditional, forgot the square, forgot to
     subtract the mean).
   - Answer key → self-check table (score bands → what to do) → solutions with a one-line reason
     for every wrong option and `Revisit:` pointers (recording + timestamp, video chapter) → index
     of original past-exam questions.
   - **Verify every answer** with a small Python script in the scratchpad (numpy/sympy, a
     simulation for "is it Gaussian?" claims) before compiling, and fix the sheet if it disagrees.
   - Compile, render the pages to PNG, look at them.
5. **Day README** from `templates/day-README.md` (order: video A → video B → sheet, timings,
   badge legend, sources).
6. Commit the video project after each day.

★ For the first day, render one scene and hand it over as a voiced preview before building the
rest: voice, pace and difficulty are where the user's feedback changes the most work. When
running unattended, build Day 1 completely, then stop and ask for feedback before Day 2.

## 7. Mock exam (review day)

Make a timed paper in the exact real format, with the length and point total of a real exam.
Sample questions in proportion to the frequency table, mix the days, and include 2–3
low-frequency questions so the paper isn't predictable. Add an answer key, solutions with pointers
to the days, and a score-to-action table (which days to redo).

## 8. Hand-off report

Give the absolute paths of the deliverables, durations and chapters, and the most frequent
question types. List every decision taken without the user (skipped checkpoints, voice,
resolution, lengths, question style) and what you did and didn't verify (e.g. "looked at sampled
frames, not every frame"). Ask for feedback on length, pace, voice and difficulty before the next
day.

## Gotchas from the first run

- ManimGL `DotCloud` must go in a `Group`, not a `VGroup`.
- `badge.next_to(header, DOWN)` centres on the badge's x; follow it with `.set_x(0)` or
  `.to_edge(...)`.
- Wide `Tex` overflows the frame silently; wrap it in `fit(mob)` from `kit.py`.
- Clip random samples to the axes range before plotting, or dots land on the header.
- Render at 1080p (`--quality` default in `build_video.py`) unless the user wants 4K; a day's two
  videos take tens of minutes at 1080p.
- Count the past papers yourself; file names lie (the same exam under two names, "winter"/"summer"
  instead of dates).
- Keep the recording numbering stable once transcripts and solutions refer to it.
