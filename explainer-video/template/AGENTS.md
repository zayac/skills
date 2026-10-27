# AGENTS.md

3Blue1Brown-style explainer video project, built from the explainer template.
Topic and source: see `script/storyboard.md` (fill it in first).

## Library: ManimGL, NOT Manim Community
- Installed editable from `ref/manim` into `.venv`. Import with `from manimlib import *`.
- Use `Tex(R"...")`, never `MathTex`. `ShowCreation`, not `Create`. No `config` object.
- Style reference: `ref/videos` (Grant's real source code). Follow the code style described in the notes at the root of `ref/videos`.
  Find prior art for the topic there before inventing visuals (e.g. `_2024/transformers/`).

## Project layout
- `paper/`: the source (PDF + `pdftotext -layout` copy). Every number on screen must come from here.
- `script/storyboard.md`: sections, beats and visuals. Scenes implement it.
- `script/narration.md`: spoken text per scene with `[cue]` marks; fact-checked against the source.
- `script/youtube.md`: title, description, chapters, upload checklist.
- `scenes/style.py`: shared colours (one per concept) and building blocks: `Table`, `VectorColumn`,
  `StateMatrix`, `AttentionGrid`, `ResultsTable`, `PaperFigure`, `NarratedScene`, `merge_into`.
  Add reusable pieces here.
- `scenes/sNN_<name>.py`: one file per storyboard section.
- `tools/`: `tts_narration.py`, `assemble.sh` (holds the scene order), `make_subtitles.py`,
  `finalize.sh`, `crop_figures.py`, `contact_sheet.sh`.
- `renders/`, `audio/placeholder/`, `.venv*`, `ref/`: generated, gitignored.

## Workflow (narration first; stop at ★ for the user)
1. Read the source fully; write `script/storyboard.md` with the one key insight and, for every
   visual, whether it is exact math, real data, a source figure, or a labelled illustration. ★
2. Write all of `script/narration.md` with `[cue]` marks and fact-check every claim BEFORE animating.
3. Build one key section, timed via cues, and hand over a voiced preview. ★
4. Build the remaining sections the same way; review frames after every render.
5. Deliver: `tools/assemble.sh --render --uhd`, `make_subtitles.py`, `finalize.sh`, fill
   `script/youtube.md` with chapter times computed from the renders. ★

## Commands
- Draft render: `.venv/bin/manimgl scenes/<file>.py <Scene> -w -l`
- Interactive: `.venv/bin/manimgl scenes/<file>.py <Scene> -se <line>`
- Narration: `python3 -I tools/tts_narration.py <Scene ...>` → `audio/placeholder/<Scene>.wav/.json`
- Full video: `tools/assemble.sh` (concat + delivery encode); `tools/assemble.sh --render --uhd`
  re-renders everything in 4K first.
- Subtitles: `python3 -I tools/make_subtitles.py` → `renders/full_video.srt` (after rendering)
- Final file: `tools/finalize.sh [music volume]` → `renders/final.mp4` (adds `audio/music.*` if
  present, ducked under the voice)
- Review: `tools/contact_sheet.sh renders/<Scene>.mp4 sheet.png <seconds between frames>`;
  single frame: `ffmpeg -loglevel error -y -ss <sec> -i renders/<Scene>.mp4 -frames:v 1 f.png`
- Paper figures: add boxes to `tools/crop_figures.py`, run `.venv/bin/python -I tools/crop_figures.py`

## Honesty rules for visuals
- Numbers on screen come from exact formulas, real computation, or the source's figures/tables.
- Anything schematic (toy simulations, cartoons) is labelled "illustration" on screen.
- Source figures are always credited (set `PAPER_CITATION` in `style.py`, including the licence).
  Only CC BY-style sources may be shown as-is; for arXiv's default licence or all-rights-reserved
  papers, redraw results from the paper's numbers or ask the user first.
- Annotate figures with `figure.point(px, py)` using pixels measured on the cropped png, never guesses.

## Narration timing
- Scenes subclass `NarratedScene` and call `self.cue()` where the narration has `[cue]`; counts must
  match (renders warn about late or unused cues; fix any warning over ~0.3 s by shortening the beat).
- Don't add fixed `self.wait()` between beats in narrated scenes; it only makes cues late.
- Pacing lives at the top of `tools/tts_narration.py` (sentence gap, pause, paragraph gap, speed).
- A real recording goes in `audio/final/<Scene>.wav` + `.json` (same format; cue times and captions
  from forced alignment, e.g. WhisperX) and takes precedence over the placeholder.

## Breeze voice (personal, non-commercial videos only)
- `TTS_BACKEND=breeze python3 tools/tts_narration.py` voices every sentence with Breeze TTS 2
  (github.com/breezeblue-ai/breeze-tts, weights HF `BreezeBlue/breeze-tts-2`) and writes
  `audio/final/`, so it replaces the Piper placeholder. Start the server first:
  `python -m breeze_infer.api <weights> --host 127.0.0.1 --port 7860` (about 7.5 GB GPU; it
  needs Python 3.12, torch 2.9.1 fails on 3.14).
- One voice for the whole project: design a reference clip once with
  `infer.py <weights> --text "<2-3 sentences>" --instruction "<voice description>" --cfg-scale 4
  --seed N` for a few seeds, let the user pick one, and save it as `audio/voices/breeze_ref.wav`
  with its exact text in `breeze_ref.txt`. Every sentence clones that clip (fixed seed 7).
- Every sentence is transcribed back with faster-whisper on the CPU (`tools/check_sentences.py`,
  run with `WHISPER_PYTHON`) and retried with other seeds below 0.9 similarity; the best take is
  kept and leftovers are printed as "still unclear". Listen to those before accepting them
  (rare terms are often Whisper's misspelling, not the voice's). `TTS_VERIFY=0` skips the check.
- Words the voice slurs go in `PRONUNCIATION` (spoken spelling only; captions keep the text).
- Breeze weights and outputs are research/non-commercial: state it in the video description and
  never use it for a monetised upload.

## Voice licensing
- Only use TTS voices whose training data is public domain or CC0 and not fine-tuned from a
  restricted voice. Default: Piper `en_US-norman-medium`. Public-domain alternatives:
  `en_US-john-medium`, `en_US-ljspeech-high`, `en_US-kristin-medium`. Avoid `ryan`, `hfc_*`
  (CC BY-NC-SA) and `joe` (fine-tuned from `lessac`). Check the voice's MODEL_CARD before switching.
- Exception: the Breeze voice above, only when the user asks for it and the video is not monetised.

## Delivery encoding
- Scenes render near-lossless (`crf: 8` in `custom_config.yml`); `tools/assemble.sh` does the one
  delivery encode (x264 crf 12, tune animation, keyframe every 2 s, faststart). Don't `-c copy`
  ManimGL's output into the final file: low bitrate plus sparse keyframes showed block artifacts in
  players.

## ManimGL gotchas
- Updaters with a second positional parameter receive `dt`; build closures with a factory method
  instead of default-argument lambdas.
- `TransformFromCopy(VGroup(a, b), VGroup(t, t.copy()))` leaves an orphan copy; use `merge_into`.
- Animate changing numbers with `animate_values` (frame-by-frame), not `.animate.set_values`, or
  digits ghost.
- `FadeOut` of a submobject removes its parent from the scene; fade the child's opacity instead.
- `self.play(..., path_arc=...)` isn't accepted; use `mob.animate.method().set_anim_args(path_arc=...)`.
- `-s` without `-w` opens a window and blocks; always pass `-w` when rendering headless.
- The default tex template needs `texlive-fontsextra`; `custom_config.yml` uses `basic`.
- Upstream ManimGL compiles all Tex via one `working.tex`; `setup.sh` patches it to one file per
  process so parallel renders don't swap formulas. If it ever reports the patch failed, render one
  scene at a time and clear `~/.cache/manim` after any parallel run.

## Workflow for writing a scene
1. Read the storyboard section, its narration and beat lengths (cue gaps in `audio/placeholder/<Scene>.json`).
2. Write the scene with one `self.cue()` per `[cue]`; render a draft with `-l`.
3. Make a contact sheet and look at it: overlaps, off-screen text, unreadable sizes, black openings,
   colour consistency, stray copies. Check render warnings for late cues.
4. Fix and repeat until clean, then commit.

## Python code style
- Match the `ref/videos` style notes: no whitespace on blank lines, declarative `VGroup(...)`, layout
  methods (`arrange`, `next_to`) over coordinate arithmetic, `get_*` helper names.
