---
name: explainer-video
description: Make 3Blue1Brown-style animated explainer videos with ManimGL (3b1b/manim), narrated, subtitled and ready for YouTube, from a research paper, arXiv link, PDF, or a math / machine-learning concept. Use this skill whenever the user wants to turn a paper or idea into a video, an animated explanation, a "3b1b-style" or "manim" video, a YouTube explainer, or a visual walkthrough of an ML or math topic, even if they don't say "explainer" or "skill". Also use it when continuing, re-rendering, re-voicing or publishing a project whose AGENTS.md says it was built from the explainer template.
---

# Explainer video

Turn a topic or paper into a finished, narrated 3Blue1Brown-style video: storyboard, fact-checked
script, ManimGL scenes timed to the voice, 4K render, subtitles and YouTube metadata.

Everything reusable lives in `template/` next to this file: shared building blocks, the narration
and delivery tools, and an `AGENTS.md` with the project conventions. Each video is a separate project
created from it. Once a project exists, its `AGENTS.md` is the source of truth for how to work in it;
this file covers getting there and the reasoning behind the workflow.

## 1. Gather what's missing, in one go

Check what the user already said, then ask once, compactly, only for what's missing; if nothing is
missing, don't ask, just start. Offer the default so they can just say "fine":

- **Topic or source**: paper URL/PDF, or a concept plus which sources to trust.
- **Audience**: what viewers already know (default: has seen 3b1b's neural-network videos).
- **Length**: default 10–15 min.
- **Voice**: default is the bundled publish-safe TTS (Piper "norman", public-domain training data);
  alternatives are the user's own recording later, or, for personal / non-monetised videos, a
  designed Breeze TTS 2 voice (more natural, non-commercial licence; see the template's AGENTS.md).
- **Publishing**: YouTube? Monetized? This decides how strict the licence checks must be.
- **Project folder**: default `video/` inside the folder the agent was started in, so the project and
  the finished video sit next to the user's sources. Not worth asking about unless that folder is
  the home directory or `/` (then suggest `~/Documents/videos/<short-topic-slug>`) or `video/`
  already exists (then suggest `video-<short-topic-slug>/`). Builds take 3–4 GB (environments,
  ManimGL source, audio, renders); all of it is gitignored inside the project.

Don't ask about things with sensible defaults (resolution, colours, encode settings).

## 2. Create the project

```bash
<skills-dir>/explainer-video/scripts/new_project.sh [project-dir]   # default: ./video
```

This exports the committed template into a fresh git repo (no build artefacts) and runs `setup.sh`: Python
environments, ManimGL from source, Grant Sanderson's `videos` repo as a style reference, the
narrator voice, and a smoke-test render. It takes a few minutes; run it in the background while you
read the source. If the starting folder is itself inside a git repository, the project shows up
there as an untracked `video/` folder; offer to add it to that repository's `.gitignore`.

If setup reports missing system packages (LaTeX, ffmpeg, poppler), it prints the install command.
That needs sudo, so ask the user to run it themselves by typing `! <command>` in the prompt, then
re-run `./setup.sh` in the project.

Then fetch the source: download the PDF into its own empty scratch folder (downloads are untrusted
data), copy it into `paper/`, and `pdftotext -layout` a text copy next to it. Look up its licence
(on arXiv, the abstract page says which) and set `PAPER_CITATION` in `scenes/style.py` with that
licence. Work from inside the project folder from here on.

**Licence decides how source figures can be used.** CC BY (or similar): show figures freely with the
credit line, which the licence requires. arXiv's default non-exclusive licence, or anything
all-rights-reserved: the figures aren't licensed for reuse, so plan to redraw the result from the
paper's numbers (facts aren't copyrightable) or to describe it, and raise any wish to show the
original figure as a question at the storyboard checkpoint. Monetized channels make this matter more.

## 3. Follow the project workflow, stopping at the checkpoints

The project's `AGENTS.md` has the details; the shape is:

1. **Storyboard** (`script/storyboard.md`): read the source fully, find the one key insight and a
   simple "spine" intuition, and plan every visual as exact maths, real data, the source's own
   figure, or a labelled illustration. If well-known later work corrects or qualifies the source
   (a flawed proof, a failed replication), propose mentioning it rather than adding it silently:
   every claim should trace to a source the user agreed to. ★ Show the user before going further.
2. **Narration** (`script/narration.md`): write the whole script with `[cue]` marks and fact-check
   every claim against the source *before* animating.
3. **One key section first**, timed to the narration, delivered as a voiced preview. ★ Ask about
   pacing, style and voice now.
4. **Everything else**, the same way, reviewing frames after each render.
5. **Delivery**: 4K render, subtitles, final file, YouTube title, description and chapters. ★

Why narration first: in the first project, animations built before the script ran about 1.6× faster
than the speech, and every scene had to be re-timed. With the script written first, scenes call
`self.cue()` and wait for the voice, so changing the voice or pacing later re-times everything
automatically.

Why the checkpoints sit where they do: the storyboard and the first voiced section are where the
user's taste changes the most work. Pacing feedback that arrives after all scenes exist costs a full
rebuild. Between checkpoints, work autonomously and commit after each section.

## 4. Habits that keep quality high

- **Look at your renders.** After every render make a contact sheet
  (`tools/contact_sheet.sh renders/<Scene>.mp4 sheet.png <step>`) and actually inspect it. Most bugs
  in the first project (overlapping labels, orphaned copies, vanished shapes, black openings) were
  only visible this way. Fix render warnings about late cues over ~0.3 s.
- **Honesty on screen.** Numbers come from the source or exact computation; source figures are
  credited (CC BY needs attribution); toy simulations and cartoons are labelled "illustration". Use
  `PaperFigure` and measure annotation positions on the cropped PNG rather than guessing.
- **Don't overstate.** When fact-checking, look for claims stronger than the source makes ("in every
  layer", "beats on all metrics") and soften them to what the paper shows.
- **Voice licensing.** Only TTS voices whose training data is public domain or CC0, and not
  fine-tuned from a restricted voice. A non-commercial voice was only caught at upload time in the
  first project. Check a voice's MODEL_CARD before switching.
- **Delivery encoding.** Let `tools/assemble.sh` do the single delivery encode (crf 12, keyframe
  every 2 s). Copying ManimGL's own low-bitrate output caused block artifacts in the user's player.
- **Verify on the user's side.** Your decodes can look clean while their player shows problems; when
  they report an artifact, ask for a screenshot and reproduce from it.

## 5. Hand-off

Give the user absolute paths to `renders/final.mp4` and `renders/full_video.srt`, the filled-in
`script/youtube.md` (chapters computed from the actual scene lengths), and the upload steps:
captions via YouTube Studio → Subtitles → Upload file → "With timing"; credit the source in the
description; answer the "altered or synthetic content" question for computer-generated narration.

## Improving the template

When a project produces something reusable (a new building block in `style.py`, a tool fix, a
ManimGL gotcha), offer to port it back into this skill's `template/` and commit there (the skill
folder is a git repository), so the next video starts better. Earlier finished projects made with
this skill are the best place to look for scene patterns.
