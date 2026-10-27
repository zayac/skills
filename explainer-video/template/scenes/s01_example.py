import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from style import *

T2C = {"W": STATE_COLOR, "x": KEY_COLOR, "y": VALUE_COLOR}


class ExampleIntro(NarratedScene):
    """Template example: one scene timed to its narration with three cues. Replace it."""
    def construct(self):
        title = Text("Example scene", font_size=48).to_edge(UP, buff=0.6)
        self.play(Write(title))

        equation = Tex(R"y = W x", t2c=T2C, font_size=72).next_to(title, DOWN, buff=0.8)
        self.cue()
        self.play(Write(equation))

        weights = StateMatrix(RNG.normal(0, 0.5, (4, 4)), cell_size=0.45, show_numbers=True)
        x = VectorColumn(RNG.normal(0, 0.5, 4), frame_color=KEY_COLOR, cell_size=0.45)
        y = VectorColumn(np.zeros(4), frame_color=VALUE_COLOR, cell_size=0.45)
        product = VGroup(weights, x, Tex("=", font_size=60), y).arrange(RIGHT, buff=0.4).next_to(equation, DOWN, buff=0.7)
        self.cue()
        self.play(FadeIn(product, lag_ratio=0.2))
        self.play(y.animate_values(weights.values @ x.values))

        replace = Text("Replace this scene with your story", font_size=36, fill_color=GREY_B)
        replace.to_edge(DOWN, buff=0.6)
        self.cue()
        self.play(FadeIn(replace, shift=0.2 * UP))
