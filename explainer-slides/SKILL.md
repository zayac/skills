---
name: explainer-slides
description: Turn an explainer video (an explainer-video / ManimGL project, or any storyboard plus narration) into a Google Slides or PowerPoint deck built from native, editable shapes with click-by-click animations, the narration in the speaker notes, and GIFs only where something moves. Use this skill whenever the user wants slides, a deck, a presentation, a Google Slides version or a "companion deck" of a video, scene, lecture explanation or manim animation, or asks to recreate animations in Google Slides or PowerPoint without embedding the video, even if they don't say "skill". Also use it to continue or rebuild a deck made with it (a folder with `build_deck.py` and `pptx_kit.py`).
---

# Explainer slides

Rebuild an explainer video as a deck that still teaches step by step: every visual is a native
shape (bars, lines, axes, dots, rotated ellipses, boxes, text), each narration beat is one click,
and the narration sits in the speaker notes. The result can be edited in Google Slides or
PowerPoint, unlike an embedded video.

The pipeline is python-pptx plus hand-written OOXML animation timing, then a .pptx → Google Slides
conversion. Google's converter keeps far more than its API exposes (the Slides API cannot create
animations at all), which is why the deck is built as a .pptx first.

## Files

| Path | What it is |
|---|---|
| `scripts/pptx_kit.py` | Deck, text (with a maths-symbol font per character), shapes with alpha and dashes, formula images at natural size, `Plot` (data → slide inches), `Timing` (click animations), `appear` |
| `scripts/check_deck.py` | Clicks vs `[click]` marks per slide, and fonts that may not survive conversion |
| `scripts/preview.py` | Rough local render of every slide's final state, for layout checks without LibreOffice |
| `example/` | The deck that motivated this skill (PAI Task 2, SWAG): `make_assets.py` (formula PNGs, GIF), `build_deck.py` (11 slides, all seven scenes), `toy.py`. Reads that project's data, so it is a pattern to copy, not something to run |

## 1. Inputs

From an explainer-video project read `script/narration.md` (scene headers, `[cue]` marks),
`script/storyboard.md`, every `scenes/*.py` (what appears at each cue, colours, real data) and the
data in `assets/`. For anything else, get the storyboard and narration first; a deck without them
has nothing to time to.

Ask only what is missing: Google Slides (default) or .pptx only, and where to put the deck folder
(default: `slides/` next to the video project).

## 2. Plan the slides

- **One scene → one slide, or two when it has more than about 7 beats or two different visuals.**
  Splitting is better than shrinking.
- **Each `[cue]` becomes one click.** Copy the scene's narration into the notes with `[click]` in
  place of `[cue]`. Whatever the scene shows before its first cue is on the slide from the start.
- **Choose each visual's form in this order:**
  1. Native shapes and text, computed from the same data and maths as the scene. Positions come
     from a `Plot`; an ellipse from a covariance is an oval rotated by minus its angle (slide y
     points down).
  2. Formula images only for what text cannot do: fractions, sums, integrals, bars and hats.
     Short formulas such as `3(1 − p) < 1 ⇔ p > 2/3` stay native text.
  3. A GIF only where motion is the point: a trajectory, points piling up, something morphing.
     Keep the GIF on its own region, with static native text next to it, about 0.5–1 MB.
  4. Real images (data samples) as pictures with a thin border.
- **No "fade out and replace".** The editor shows every object at once, so replaced objects
  overlap there. Put the new object in its own space instead.
- **Keep the honesty labels:** "illustration", "made-up probabilities", data sources, exactly as
  the video has them, and a sources slide at the end.

## 3. Build

```bash
python -m venv <scratch>/venv && <scratch>/venv/bin/pip install python-pptx matplotlib numpy pillow lxml
cp <skills-dir>/explainer-slides/scripts/{pptx_kit,check_deck,preview}.py slides/
```

Write `slides/make_assets.py` (formulas via matplotlib mathtext with `mathtext.fontset = "cm"` to
match ManimGL's TeX; GIFs via `FuncAnimation` + `PillowWriter`) and `slides/build_deck.py`
following `example/`. Per slide: `deck.slide(notes)`, `title(...)`, the shapes, then
`Timing().build(slide, clicks)`, where each click is a list of `(shape, effect, delay_ms)`:

- Effects: `fade_in`, `fade_out`, `fly_up`, `fly_left`, `zoom_in`.
- The first effect of a click starts on click and the rest start with it. Stagger with delays
  (`appear(shapes, stagger=100)`): the delays play in Google Slides even though its Motion panel
  cannot show or edit them.

Layout: 10 × 5.625 in; titles 28 pt at (0.5, 0.3); body text at least 12 pt and footnote tags
11 pt at the bottom right; keep 0.3 in between blocks.

## 4. Check locally

```bash
python make_assets.py && python build_deck.py
python check_deck.py deck.pptx          # clicks vs notes, fonts
python preview.py deck.pptx <scratch>/prev_   # then look at the PNGs
```

If the `pptx` skill is available, also run its `validate.py`. `preview.py` only approximates fonts
and does not wrap text, so treat it as an overlap check; the real check is in Google Slides (§6).

## 5. Publish to Google Slides

- **Fonts first.** Google keeps a font only if its editors offer it; anything else silently
  becomes Arial. Confirmed: STIX Two Text and STIX Two Math, a serif pair that matches the
  Computer Modern formulas. ManimGL's usual Noto Serif is not offered (only its script variants)
  and fell back to Arial. `check_deck.py` flags the rest.
- **Upload.** Use the first of these that your tools allow:
  1. **A Drive API upload that streams the file from disk**, with the target type set to
     `application/vnd.google-apps.presentation`. Drive then converts it directly, and the Convert
     step below is not needed.
  2. **A browser-automation tool that can set files on a file input**, through Drive's own upload
     control:
     1. Open drive.google.com.
     2. Run JavaScript that wraps `HTMLInputElement.prototype.click`: when it is called for a file
        input, keep that input in `window.__captured`, label it, make it visible, and don't open
        the native picker.
     3. Click New → File upload, locate the captured input, and set the .pptx on it.
     4. Restore the original `click` right away.
     5. If Drive asks about a file with the same name, choose "Replace existing file"; Drive keeps
        the old one in version history.

     Synthetic drag-and-drop events don't work: Drive ignores them.
  3. **Otherwise, ask the user** to upload the .pptx to Drive and share the link.

  Avoid Drive tools that take the file content inline in the call: they are impractical above a
  few hundred KB.
- **Convert.** Open the .pptx (`docs.google.com/presentation/d/<id>/edit`), then File → Save as
  Google Slides. The converted deck opens in a new tab. Find it with a Drive search by title
  rather than relying on that tab, then rename it.
- **Every rebuild creates a new Google file and link.** Without a tool that edits Slides in place,
  the deck can't be updated. Rename the older copies "– superseded …" and offer to move them to the
  bin; never delete them without asking. Fix one-off issues directly in the converted deck when
  that is cheaper: drag a handle, retype a title. Then make the same change in `build_deck.py`.

## 6. Check in Google Slides

- Look at every slide in the editor; it shows each slide's final state. Check for text overflow,
  boxes that no longer fit (a narrower font shrinks text but not the boxes around it) and overlaps.
- Confirm the font: click into a title and read the toolbar's font box.
- Step through one or two busy slides in present mode (`/present?slide=id.pN`, Right arrow) to see
  the build-up. Screenshots of slides with hundreds of shapes can time out; wait a few seconds and
  retry.
- Confirm the speaker notes came through (the editor's Speaker notes box).

What Google keeps from the .pptx: Fade in/out, Fly in, Zoom in; On click / With previous; delays
(they play but can't be edited); animated GIFs; rotated ovals; alpha fills; dashed lines; speaker
notes; per-run fonts in its catalogue.

## 7. Hand-off

Link the deck by name. Then say:
- How it maps to the video's scenes.
- Which visuals are GIFs and formula images, as opposed to editable shapes.
- That the editor shows the final state while the slideshow builds it up.
- Which superseded copies and uploaded .pptx files are now in Drive.
- Where `build_deck.py` lives.

Add a `README.md` in the deck folder with the slide → scene table and the rebuild commands.
