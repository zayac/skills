"""Shared pieces for exam-prep videos: colours, headers, bullets, verdicts, tables, frequency badges.

Add course-specific building blocks (plots, diagrams) below the generic ones.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from style import *

# Number of distinct past exam papers counted in script/frequencies.md
PAPERS = 8

# One colour per concept, fixed across all videos of the course
TRAP_COLOR = RED
GOOD_COLOR = GREEN
HIGHLIGHT_COLOR = YELLOW

T2C = {}


def fit(mob, width=13.0):
    """Shrink a wide mobject (usually Tex) to fit the frame"""
    if mob.get_width() > width:
        mob.set_width(width)
    return mob


def get_badge_below(header, count, note=None):
    badge = get_frequency_badge(count, note=note, font_size=26)
    badge.next_to(header, DOWN, buff=0.15).to_edge(RIGHT, buff=0.3)
    return badge


def get_header(text, font_size=44):
    title = Text(text, font_size=font_size)
    title.to_edge(UP, buff=0.35)
    rule = Underline(title, buff=0.12).set_stroke(GREY_B, 2)
    rule.set_width(FRAME_WIDTH - 1.0)
    rule.set_x(0)
    return VGroup(title, rule)


def get_tag(text, color=GREY_B, font_size=24):
    """Small label, e.g. "Exam 2025, Q5" or "illustration\""""
    return Text(text, font_size=font_size, fill_color=color)


def get_bullet(content, font_size=34, color=WHITE):
    """One bullet line; content is a Text-able string or a ready mobject"""
    if isinstance(content, str):
        content = Text(content, font_size=font_size, fill_color=color)
    dot = Dot(radius=0.06, fill_color=GREY_B)
    dot.next_to(content, LEFT, buff=0.25)
    dot.match_y(content[0] if len(content) > 0 else content)
    return VGroup(dot, content)


def get_bullets(items, font_size=34, buff=0.35):
    bullets = VGroup(*(get_bullet(item, font_size) for item in items))
    bullets.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return bullets


def get_box(mob, color=YELLOW, buff=0.2):
    return SurroundingRectangle(mob, buff=buff).set_stroke(color, 3)


def get_verdict(is_true, font_size=40):
    word = "TRUE" if is_true else "FALSE"
    color = GOOD_COLOR if is_true else TRAP_COLOR
    text = Text(word, font_size=font_size, fill_color=color, weight=BOLD)
    return VGroup(SurroundingRectangle(text, buff=0.15).set_stroke(color, 3), text)


def get_pause_sign():
    bars = VGroup(Rectangle(0.25, 1.0), Rectangle(0.25, 1.0)).arrange(RIGHT, buff=0.25)
    bars.set_stroke(width=0).set_fill(WHITE, 1)
    circle = Circle(radius=1.0).set_stroke(WHITE, 4)
    label = Text("Pause and solve", font_size=36)
    sign = VGroup(circle, bars)
    label.next_to(sign, DOWN, buff=0.3)
    return VGroup(sign, label)


class ProbTable(VGroup):
    """A grid of probabilities with row and column labels"""
    def __init__(self, values, row_labels, col_labels, cell_width=1.6, cell_height=0.8,
                 font_size=32, decimals=3, **kwargs):
        super().__init__(**kwargs)
        n_rows, n_cols = len(values), len(values[0])
        self.cells = VGroup(*(
            VGroup(*(
                Rectangle(cell_width, cell_height).set_stroke(GREY_B, 1.5)
                for _ in range(n_cols)
            )).arrange(RIGHT, buff=0)
            for _ in range(n_rows)
        )).arrange(DOWN, buff=0)
        self.numbers = VGroup(*(
            VGroup(*(
                DecimalNumber(values[i][j], num_decimal_places=decimals, font_size=font_size).move_to(self.cells[i][j])
                for j in range(n_cols)
            ))
            for i in range(n_rows)
        ))
        self.row_labels = VGroup(*(
            Tex(label, font_size=font_size).next_to(self.cells[i], LEFT, buff=0.3)
            for i, label in enumerate(row_labels)
        ))
        self.col_labels = VGroup(*(
            Tex(label, font_size=font_size).next_to(self.cells[0][j], UP, buff=0.2)
            for j, label in enumerate(col_labels)
        ))
        self.add(self.cells, self.numbers, self.row_labels, self.col_labels)

    def get_row(self, i):
        return VGroup(self.cells[i], self.numbers[i])

    def get_col(self, j):
        return VGroup(*(VGroup(row[j], nums[j]) for row, nums in zip(self.cells, self.numbers)))

    def get_cell_highlight(self, i, j, color=YELLOW):
        return self.cells[i][j].copy().set_stroke(color, 4).set_fill(color, 0.2)


def get_frequency_level(count, total=None):
    """high: at least half the papers, medium: at least a quarter, low: fewer"""
    total = total or PAPERS
    if 2 * count >= total:
        return "high"
    if 4 * count >= total:
        return "medium"
    return "low"


def get_frequency_badge(count, total=None, note=None, font_size=30):
    """How often this question type appeared in the past exam papers, e.g. "In exams: 3/8 papers\""""
    total = total or PAPERS
    level = get_frequency_level(count, total)
    if level == "high":
        color = RED_B
    elif level == "medium":
        color = ORANGE
    else:
        color = GREY_B
    dots = VGroup(*(
        Dot(radius=0.09).set_fill(color if i < count else GREY_D, 1)
        for i in range(total)
    )).arrange(RIGHT, buff=0.06)
    text = Text(f"In exams: {count}/{total} papers · {level}", font_size=font_size, fill_color=color)
    row = VGroup(text, dots).arrange(RIGHT, buff=0.2)
    if note:
        row = VGroup(row, Text(note, font_size=font_size - 4, fill_color=GREY_B)).arrange(DOWN, buff=0.08, aligned_edge=RIGHT)
    frame = SurroundingRectangle(row, buff=0.12).set_stroke(color, 1.5).set_fill(BLACK, 0.85)
    return VGroup(frame, row)
