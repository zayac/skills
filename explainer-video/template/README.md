# Explainer video template

A starting point for 3Blue1Brown-style explainer videos made with ManimGL and a coding agent:
narration-first workflow, cue-timed scenes, a publish-safe placeholder voice, subtitles, 4K
delivery encode, and YouTube metadata.

## Start a new video

This template ships inside the `explainer-video` agent skill: asking the agent to make an
explainer video sets everything up. By hand:

    <skills-dir>/explainer-video/scripts/new_project.sh ~/Documents/videos/<new-video>

That copies this template into a fresh repository and runs `setup.sh`, which creates the Python environments, clones the ManimGL source and Grant Sanderson's videos
repo (style reference), downloads the narrator voice and renders a smoke-test frame. It tells you
which system packages to install if any are missing.

Improvements made while working on a video (new building blocks, fixes, gotchas) belong back here:
edit `<skills-dir>/explainer-video/template/` and commit.

Then put the source PDF in `paper/` (if there is one), start the agent in the folder, and paste the
prompt from `PROMPT.md`.

## Try the example

    python3 -I tools/tts_narration.py ExampleIntro
    .venv/bin/manimgl scenes/s01_example.py ExampleIntro -w -l
    tools/assemble.sh && python3 -I tools/make_subtitles.py && tools/finalize.sh

`renders/final.mp4` is a 20-second narrated, subtitled example.

## What's inside

| Path | Purpose |
|---|---|
| `AGENTS.md` | Conventions and workflow the agent follows in this project |
| `PROMPT.md` | Prompt to start a new video |
| `scenes/style.py` | Colours and building blocks (`NarratedScene`, `PaperFigure`, `ResultsTable`, …) |
| `scenes/s01_example.py` | Example cue-timed scene; replace |
| `script/` | Storyboard, narration and YouTube templates |
| `tools/` | Narration, assembly/encode, subtitles, finalize, figure cropping, contact sheets |
| `custom_config.yml` | ManimGL config: black background, serif text, near-lossless scene renders |
