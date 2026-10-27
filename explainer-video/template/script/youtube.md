# YouTube metadata

Chapter times come from the rendered scene lengths; recompute after any re-render that changes
timing (ask the agent, or sum `ffprobe` durations of renders/<Scene>.mp4 in tools/assemble.sh order).
YouTube needs the first chapter at 0:00, at least 3 chapters, each at least 10 s.

## Title (pick one)

1. <curiosity hook the video answers>
2. <alternative>

## Description

<2 short paragraphs: the question, and what the video shows>

Source:
<Authors. "Title." arXiv:XXXX.XXXXX (YEAR). https://arxiv.org/abs/XXXX.XXXXX>
Code: <link>

Chapters
0:00 <first chapter>

Credits
- Figures <N, M> and all benchmark numbers are from the source above, used under <license>.
- Animated with ManimGL (github.com/3b1b/manim), the open-source library by Grant Sanderson.
  This video is not affiliated with 3Blue1Brown.
- Narration is computer-generated (Piper text-to-speech, "norman" voice, trained on public-domain
  LibriVox recordings).

## Tags

<comma-separated>

## Upload checklist

- [ ] Video: renders/final.mp4
- [ ] Subtitles: renders/full_video.srt → Subtitles → English → Upload file → "With timing"
- [ ] Altered or synthetic content: narration is computer-generated; answer the prompt accordingly
- [ ] Optional: send the link to the source's authors
