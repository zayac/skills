import json
from pathlib import Path

from manimlib import *
from manimlib.logger import log

# One color per concept, used consistently in every scene. Rename/extend per topic, then keep fixed.
KEY_COLOR = BLUE
VALUE_COLOR = YELLOW
QUERY_COLOR = RED_B
STATE_COLOR = TEAL
LABEL_COLOR = GREEN
ERROR_COLOR = RED
PARAM_COLOR = PINK  # learning rates, step sizes, hyperparameters
CONTEXT_COLOR = GREY_B

# Synthetic table contents are deterministic so re-renders match
RNG = np.random.default_rng(0)


def value_to_color(value, low=-1.0, high=1.0):
    # Diverging map: negative -> blue, zero -> dark grey, positive -> yellow
    alpha = clip((value - low) / (high - low), 0, 1)
    if alpha < 0.5:
        return interpolate_color(BLUE, GREY_E, 2 * alpha)
    return interpolate_color(GREY_E, YELLOW, 2 * alpha - 1)


def number_color_for(value, vmax):
    # Dark text on bright yellow cells, light text everywhere else
    return BLACK if value > 0.6 * vmax else WHITE


def merge_into(sources, target):
    """Animations that morph copies of each source into one target, leaving no stray copies behind"""
    return [FadeTransform(source.copy(), target) for source in sources]


class AnimatedValuesMixin:
    """Animate numeric contents frame by frame, so digits never cross-fade into ghosts"""
    def animate_values(self, new_values, **kwargs):
        start = np.array(self.values, dtype=float)
        end = np.array(new_values, dtype=float)
        return UpdateFromAlphaFunc(
            self,
            lambda mob, alpha: mob.set_values(interpolate(start, end, alpha)),
            **kwargs
        )


class TableRow(VGroup):
    """One row of a tabular dataset: m feature cells plus a label cell"""
    def __init__(
        self,
        features,
        label=None,
        cell_size=0.35,
        label_colors=(LABEL_COLOR, PURPLE_B, ORANGE),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.features = VGroup(*(
            Square(cell_size).set_stroke(GREY_C, 1).set_fill(value_to_color(f), 0.9)
            for f in features
        ))
        self.features.arrange(RIGHT, buff=0)
        self.label = Square(cell_size).set_stroke(WHITE, 1.5)
        if label is None:
            self.label.set_fill(BLACK, 1)
            self.label.add(Text("?", font_size=24).move_to(self.label))
        else:
            self.label.set_fill(label_colors[label % len(label_colors)], 1)
        self.label.next_to(self.features, RIGHT, buff=0.1)
        self.add(self.features, self.label)


class Table(VGroup):
    """A stack of rows: labelled context rows followed by unlabelled query rows"""
    def __init__(self, n_context=6, n_query=2, n_features=5, n_classes=3, **kwargs):
        super().__init__(**kwargs)
        self.context_rows = VGroup(*(
            TableRow(RNG.uniform(-1, 1, n_features), RNG.integers(n_classes))
            for _ in range(n_context)
        ))
        self.query_rows = VGroup(*(
            TableRow(RNG.uniform(-1, 1, n_features), None)
            for _ in range(n_query)
        ))
        for rows in (self.context_rows, self.query_rows):
            rows.arrange(DOWN, buff=0.05)
        self.add(self.context_rows, self.query_rows)
        self.arrange(DOWN, buff=0.25)


class VectorColumn(AnimatedValuesMixin, VGroup):
    """A small vector drawn as a column of heat-coloured cells with their values written inside"""
    def __init__(
        self,
        values,
        frame_color=WHITE,
        cell_size=0.55,
        vmax=1.0,
        show_numbers=True,
        num_decimal_places=1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vmax = vmax
        self.cells = VGroup(*(
            Square(cell_size).set_stroke(GREY_D, 0.5)
            for _ in values
        ))
        self.cells.arrange(DOWN, buff=0)
        self.frame_rect = SurroundingRectangle(self.cells, buff=0).set_stroke(frame_color, 3)
        self.numbers = VGroup(*(
            DecimalNumber(0, num_decimal_places=num_decimal_places, font_size=20)
            for _ in values
        ))
        self.add(self.cells, self.frame_rect)
        if show_numbers:
            self.add(self.numbers)
        self.set_values(values)

    def set_values(self, values):
        self.values = np.array(values, dtype=float)
        for cell, number, value in zip(self.cells, self.numbers, self.values):
            cell.set_fill(value_to_color(value, -self.vmax, self.vmax), 1)
            number.set_value(value).set_max_width(0.8 * cell.get_width()).move_to(cell)
            number.set_fill(number_color_for(value, self.vmax))
        return self

    def as_row(self):
        """Lay the vector out horizontally, e.g. for a transpose"""
        self.cells.arrange(RIGHT, buff=0)
        self.frame_rect.surround(self.cells, buff=0)
        for cell, number in zip(self.cells, self.numbers):
            number.move_to(cell)
        return self


class StateMatrix(AnimatedValuesMixin, VGroup):
    """Heatmap of a recurrent state S (d_v x d_qk), optionally with its entries written in"""
    def __init__(self, values, cell_size=0.3, vmax=1.0, show_numbers=False, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = cell_size
        self.vmax = vmax
        n_rows, n_cols = values.shape
        self.cells = VGroup(*(
            Square(cell_size).set_stroke(GREY_D, 0.5)
            for _ in range(n_rows * n_cols)
        ))
        self.cells.arrange_in_grid(n_rows, n_cols, buff=0)
        self.frame_rect = SurroundingRectangle(self.cells, buff=0).set_stroke(STATE_COLOR, 3)
        self.numbers = VGroup(*(
            DecimalNumber(0, num_decimal_places=2, font_size=16)
            for _ in range(n_rows * n_cols)
        ))
        self.add(self.cells, self.frame_rect)
        if show_numbers:
            self.add(self.numbers)
        self.set_values(values)

    def set_values(self, values):
        self.values = np.array(values, dtype=float)
        for cell, number, value in zip(self.cells, self.numbers, self.values.flatten()):
            cell.set_fill(value_to_color(value, -self.vmax, self.vmax), 1)
            number.set_value(value).set_max_width(0.85 * cell.get_width()).move_to(cell)
            number.set_fill(number_color_for(value, self.vmax))
        return self


class AttentionGrid(VGroup):
    """n x n grid of pairwise interactions, optionally causally masked"""
    def __init__(self, n, cell_size=0.2, causal=False, **kwargs):
        super().__init__(**kwargs)
        weights = RNG.uniform(0, 1, (n, n))
        self.cells = VGroup(*(
            Square(cell_size).set_stroke(GREY_D, 0.5).set_fill(
                BLUE if not (causal and j > i) else BLACK,
                weights[i, j] if not (causal and j > i) else 1,
            )
            for i in range(n)
            for j in range(n)
        ))
        self.cells.arrange_in_grid(n, n, buff=0)
        self.add(self.cells)


class BuildingBlocksGallery(Scene):
    """Gallery of the shared building blocks; also the setup smoke test"""
    def construct(self):
        table = Table()
        state = StateMatrix(RNG.normal(0, 0.5, (6, 6)))
        grid = AttentionGrid(12, causal=True)
        VGroup(table, state, grid).arrange(RIGHT, buff=1.2)
        titles = VGroup(
            Text("Table", font_size=36).next_to(table, UP),
            Text("State S", font_size=36, fill_color=STATE_COLOR).next_to(state, UP),
            Text("Causal attention", font_size=36).next_to(grid, UP),
        )
        self.play(
            LaggedStartMap(FadeIn, table.context_rows, shift=0.2 * DOWN, lag_ratio=0.1),
            FadeIn(table.query_rows),
            FadeIn(state),
            ShowCreation(grid.cells, lag_ratio=0.01),
            Write(titles),
        )
        self.play(state.animate.set_values(RNG.normal(0, 0.5, (6, 6))))
        self.wait()


ASSET_DIR = Path(__file__).parent.parent / "assets"
# Shown in the credit line under every PaperFigure. Set per project.
PAPER_CITATION = "Author et al. YEAR, arXiv:XXXX.XXXXX (<licence, e.g. CC BY 4.0>)"


class PaperFigure(Group):
    """A figure cropped from the paper, on a white card, with a credit line underneath.

    Annotations are placed with point(px, py), using pixel coordinates measured on the cropped png.
    """
    def __init__(self, file_name, figure_label, width=12, **kwargs):
        super().__init__(**kwargs)
        self.image = ImageMobject(str(ASSET_DIR / "raster" / file_name))
        self.pixel_width, self.pixel_height = self.image.image.size
        self.image.set_width(width)
        self.card = SurroundingRectangle(self.image, buff=0.15)
        self.card.set_stroke(width=0).set_fill(WHITE, 1)
        self.credit = Text(f"{figure_label}, {PAPER_CITATION}", font_size=20, fill_color=GREY_B)
        self.credit.next_to(self.card, DOWN, buff=0.15)
        self.add(self.card, self.image, self.credit)

    def point(self, px, py):
        corner = self.image.get_corner(UL)
        return corner + (px / self.pixel_width) * self.image.get_width() * RIGHT \
            + (py / self.pixel_height) * self.image.get_height() * DOWN

    def get_reveal_mask(self, px_left, px_right, py_top, py_bottom, color):
        """A rectangle in the plot's background colour; shrink it rightwards to 'draw' the curves"""
        ul = self.point(px_left, py_top)
        dr = self.point(px_right, py_bottom)
        mask = Rectangle(dr[0] - ul[0], ul[1] - dr[1])
        mask.set_stroke(width=0).set_fill(color, 1)
        mask.move_to((ul + dr) / 2)
        return mask


class NarratedScene(InteractiveScene):
    """A scene timed to its narration.

    Loads audio/final/<Scene>.wav (or audio/placeholder/<Scene>.wav) with its timings json, embeds the
    audio, and lets construct() call self.cue() to wait for the next [cue] mark in the narration.
    Without narration files, cue() does nothing and the scene keeps its own pacing.
    """
    audio_dir = ASSET_DIR.parent / "audio"

    def setup(self):
        super().setup()
        self.cue_times = []
        self.cue_index = 0
        self.narration_length = 0.0
        name = type(self).__name__
        for folder in ("final", "placeholder"):
            wav = self.audio_dir / folder / f"{name}.wav"
            timings = self.audio_dir / folder / f"{name}.json"
            if wav.exists() and timings.exists():
                data = json.loads(timings.read_text())
                self.cue_times = data["cues"]
                self.narration_length = data["duration"]
                self.add_sound(str(wav))
                break

    def cue(self):
        """Wait until the narration reaches the next [cue] mark"""
        if self.cue_index >= len(self.cue_times):
            return
        target = self.cue_times[self.cue_index]
        if self.time > target + 0.05:
            log.warning(f"{type(self).__name__}: cue {self.cue_index} is {self.time - target:.1f}s late")
        elif target > self.time:
            self.wait(target - self.time)
        self.cue_index += 1

    def tear_down(self):
        if self.cue_index < len(self.cue_times):
            log.warning(f"{type(self).__name__}: {len(self.cue_times) - self.cue_index} cues never used")
        if self.narration_length > self.time:
            self.wait(self.narration_length - self.time + 1.0)
        super().tear_down()


class ResultsTable(VGroup):
    """A small table of numbers from the paper. rows: list of (name, value, value, ...)"""
    def __init__(self, headers, rows, font_size=28, decimals=4, **kwargs):
        super().__init__(**kwargs)
        n_cols = len(headers)
        self.header = VGroup(*(Text(h, font_size=font_size, fill_color=GREY_B) for h in headers))
        self.body = VGroup(*(
            VGroup(Text(row[0], font_size=font_size), *(
                Text(f"{value:.{decimals}f}", font_size=font_size) for value in row[1:]
            ))
            for row in rows
        ))
        grid = VGroup(*self.header, *(cell for row in self.body for cell in row))
        grid.arrange_in_grid(len(rows) + 1, n_cols, h_buff=0.8, v_buff=0.3, aligned_edge=LEFT)
        self.rule = Line(LEFT, RIGHT).set_width(grid.get_width() + 0.4).set_stroke(GREY_C, 1)
        self.rule.next_to(self.header, DOWN, buff=0.15).set_x(grid.get_x())
        self.add(self.header, self.rule, self.body)

    def get_row_highlight(self, index, color):
        return SurroundingRectangle(self.body[index], buff=0.1).set_stroke(color, 3)

    def get_column(self, index):
        return VGroup(self.header[index], *(row[index] for row in self.body))
