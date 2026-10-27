"""Scene patterns for one study day; copy to scenes/sNN_<name>.py and fill in.

Video A: TitleCard → one scene per concept → recap. Video B: PracticeIntro → examples → PauseAndSolve → WrapUp.
Every scene is narrated: one self.cue() per [cue] in its block in script/narration.md.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from kit import *

COURSE = "Course name"
DAY = 1
TOPIC = "Topic of the day"
PAPERS_LEGEND = "8 papers: Jan 2021, Feb 2022, …"


class TitleCard(NarratedScene):
    """Course, topic, day; then the plan of the video"""
    plan = ["First concept", "Second concept", "Recap: exam traps"]
    subtitle = f"Day {DAY} — Theory"

    def construct(self):
        course = Text(COURSE, font_size=36, fill_color=GREY_B)
        title = Text(TOPIC, font_size=72)
        day = Text(self.subtitle, font_size=40, fill_color=GREY_B)
        card = VGroup(course, title, day).arrange(DOWN, buff=0.5)
        fit(title)
        self.play(FadeIn(course, shift=0.2 * DOWN), Write(title), FadeIn(day))

        self.cue()
        self.play(card.animate.scale(0.6).to_edge(UP, buff=0.4))
        plan = get_bullets(self.plan, font_size=32).next_to(card, DOWN, buff=0.6)
        self.plan_mob = plan
        self.play(LaggedStartMap(FadeIn, plan, shift=0.2 * RIGHT, lag_ratio=0.5, run_time=4))


class PracticeIntro(TitleCard):
    """Video B title card, list of examples, badge legend, pause sign"""
    plan = ["1. First example", "2. Second example", "Pause and solve: three questions"]
    subtitle = f"Day {DAY} — Worked examples & practice"

    def construct(self):
        super().construct()
        self.cue()
        self.play(FadeOut(self.plan_mob))
        badges = VGroup(
            get_frequency_badge(PAPERS - 2, note="example: a high-frequency type"),
            get_frequency_badge(max(1, PAPERS // 4), note="example: a medium-frequency type"),
            get_frequency_badge(1, note="example: a rare type"),
        ).arrange(DOWN, buff=0.35).shift(0.5 * DOWN)
        legend = get_tag(PAPERS_LEGEND, font_size=26).next_to(badges, DOWN, buff=0.4)
        self.play(LaggedStartMap(FadeIn, badges, lag_ratio=0.4), FadeIn(legend))

        self.cue()
        self.play(FadeOut(VGroup(badges, legend)))
        self.play(FadeIn(get_pause_sign().shift(0.5 * DOWN), scale=0.8))


class ExampleTrueFalse(NarratedScene):
    """One worked example: header + badge, statement, reasoning steps, verdict"""
    def construct(self):
        header = get_header("Example 1 · Statement to check")
        badge = get_badge_below(header, 3, "Feb 2022 Q3, Aug 2022 Q3, Jan 2025 Q3")
        self.play(FadeIn(header), FadeIn(badge))
        statement = fit(Tex(R"\text{Statement with } a^2 + b^2 = c^2", font_size=40))
        statement.next_to(badge, DOWN, buff=0.4).set_x(0)
        self.play(Write(statement))

        self.cue()
        steps = VGroup(
            Tex(R"\text{step one}", font_size=36),
            Tex(R"\text{step two}", font_size=36),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(statement, DOWN, buff=0.6)
        self.play(LaggedStartMap(FadeIn, steps, shift=0.2 * DOWN, lag_ratio=0.6))

        self.cue()
        verdict = get_verdict(True).next_to(steps, DOWN, buff=0.6)
        self.play(FadeIn(verdict, scale=1.2))


class PauseAndSolve(NarratedScene):
    """Questions with a pause sign, then answers. Narration: [cue] question, [cue] answer, per question"""
    questions = [
        (6, "where it appeared", R"\text{Question as Tex: } x^2 = ?", [R"\text{answer line 1}", R"\text{answer line 2}"]),
    ]

    def construct(self):
        header = get_header("Pause and solve")
        self.play(FadeIn(header))
        for i, (count, note, tex, answers) in enumerate(self.questions):
            self.cue()
            label = Text(f"Question {i + 1}", font_size=34, fill_color=HIGHLIGHT_COLOR)
            label.next_to(header, DOWN, buff=0.4).to_edge(LEFT, buff=0.8)
            badge = get_badge_below(header, count, note)
            question = fit(Tex(tex, font_size=40)).next_to(label, DOWN, buff=0.6).set_x(0)
            sign = get_pause_sign().scale(0.7).next_to(question, DOWN, buff=0.7)
            self.play(FadeIn(label), FadeIn(badge), Write(question))
            self.play(FadeIn(sign, scale=0.8))
            self.cue()
            answer = VGroup(*(Tex(a, font_size=38) for a in answers)).arrange(DOWN, buff=0.3)
            answer.next_to(question, DOWN, buff=0.7)
            self.play(FadeOut(sign))
            self.play(LaggedStartMap(FadeIn, answer, shift=0.2 * DOWN, lag_ratio=0.6, run_time=3))
            if i < len(self.questions) - 1:
                if self.cue_index < len(self.cue_times):
                    self.wait(max(0, self.cue_times[self.cue_index] - self.time - 1.0))
                self.play(FadeOut(VGroup(label, badge, question, answer)))


class WrapUp(NarratedScene):
    """Summary, pointer to the practice sheet, preview of the next day"""
    summary = ["Point one", "Point two", "Point three"]
    next_day = "Day 2: next topic"

    def construct(self):
        header = get_header(f"Day {DAY} done")
        self.play(FadeIn(header))
        summary = get_bullets(self.summary, font_size=34).next_to(header, DOWN, buff=0.7)
        self.play(LaggedStartMap(FadeIn, summary, lag_ratio=0.4))

        self.cue()
        sheet = VGroup(
            Text(f"Next: Day {DAY} practice sheet (PDF)", font_size=36, fill_color=HIGHLIGHT_COLOR),
            Text("45 minutes, no notes → answer key → solutions with lecture timestamps", font_size=30, fill_color=GREY_A),
        ).arrange(DOWN, buff=0.3).next_to(summary, DOWN, buff=0.9)
        self.play(FadeIn(sheet, lag_ratio=0.3))

        self.cue()
        self.play(FadeIn(Text(self.next_day, font_size=40).next_to(sheet, DOWN, buff=0.8), shift=0.2 * UP))
