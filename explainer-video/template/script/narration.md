# Narration

Spoken text, grouped by storyboard section and the scene it plays over. A header names the scene
class it belongs to (CamelCase, e.g. `### ExampleIntro`); headers containing TODO are skipped.
`[cue]` marks where the scene's next `self.cue()` beat starts (counts must match). `[pause]` is an
extra silence. *Italics*, `<!-- notes -->` (e.g. fact-check sources) and `---` rules are stripped before synthesis. Target pace ≈ 150 words/min.

Every factual claim must be traceable to the source in `paper/`.

---

## S01 Example — ExampleIntro

This is the example scene that ships with the template. [cue] Here's a matrix times a vector, the
most common operation in machine learning. [cue] Each entry of the output mixes every entry of the
input, weighted by one row of the matrix.

[cue] Replace this section, and the scene, with your own story.
