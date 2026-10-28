"""Google-Slides-ready deck covering the whole Task 2 explainer video, one or two slides per scene

Example from the PAI Task 2 (SWAG) project: it reads that project's assets (map_val.json, images,
formula PNGs from make_assets.py), so copy its patterns rather than running it here.
"""
import json
import numpy as np
from pptx.enum.shapes import MSO_SHAPE
from pptx_kit import *
from toy import get_swag_toy, ellipse_params, contour_cov, VALLEY_ANGLE

MAP_VAL = json.load(open("assets/map_val.json"))
TOY = get_swag_toy()
deck = Deck()


def inches(emu):
    return emu / 914400


# Title
s = deck.slide(
    "Companion deck to the explainer video. Each slide's notes hold the narration; a click mark shows where the next "
    "animation step starts.",
    transition=False,
)
text(s, 0.7, 1.5, 8.6, 1.3, "When should a network say “I don't know”?", size=32, bold=True)
text(s, 0.7, 2.85, 8.6, 0.5, "Calibration and SWA-Gaussian (SWAG) for PAI Task 2", size=20, color=YELLOW)
text(s, 0.7, 3.5, 8.6, 0.8, "Companion deck to the 7-minute explainer video.\nSpeaker notes carry the narration.",
     size=14, color=GREY_B)


# S01 TaskIntro, part 1: classes and ambiguous images
s = deck.slide(
    "Task two hands you sixty by sixty satellite images, and asks what the land is used for. [click] In the training "
    "set, every image belongs to exactly one of six classes. [click] But the test set also contains ambiguous images: "
    "a forest beside a lake, unknown land types, snow, or clouds. For those, no class is right."
)
title(s, "Task 2: land use from satellite images")
side, gap = 1.25, 0.25
x0 = (10 - (6 * side + 5 * gap)) / 2
labels, amb, marks = [], [], []
for c in range(6):
    x = x0 + c * (side + gap)
    picture(s, f"assets/class{c}.png", x, 1.45, w=side, border=GREY_B)
    labels.append(text(s, x, 1.12, side, 0.28, f"class {c}", size=14, color=GREY_A, align=CENTER))
    amb.append(picture(s, f"assets/amb{c}.png", x, 3.35, w=side, border=GREY_B))
    marks.append(text(s, x, 2.95, side, 0.35, "?", size=22, color=YELLOW, bold=True, align=CENTER))
amb_label = text(s, 0.5, 4.75, 5, 0.3, "ambiguous: no class is right", size=14, color=YELLOW)
source = tag(s, "real validation images from the handout", y=4.8)
Timing().build(s, [
    appear(labels, stagger=100),
    appear(amb, stagger=150) + appear(marks, stagger=150) + [(amb_label, "fade_in", 600), (source, "fade_in", 600)],
])


# S01 TaskIntro, part 2: options, costs, total
s = deck.slide(
    "[click] So your model gets a seventh option: say “don't know”. [click] The scoring is a cost. A correct class "
    "costs nothing. “Don't know” always costs one. A wrong class, or any class on an ambiguous image, costs three. "
    "[click] On top of that, the checker measures calibration with the expected calibration error, and adds "
    "everything above zero point one as a penalty. [click] So this task is not about accuracy. It is about knowing "
    "how much you know."
)
title(s, "Seven options, three costs, one penalty")
options = text(s, 0.5, 1.1, 9, 0.5, "ŷ ∈ {0, 1, 2, 3, 4, 5}  ∪  {−1 = “don't know”}", size=22,
               align=CENTER)
rows = []
for i, (name, value, color) in enumerate([
    ("correct class", "0", GREEN),
    ("don't know", "1", YELLOW),
    ("wrong class, or any class on an ambiguous image", "3", RED),
]):
    y = 1.9 + i * 0.5
    rows += [text(s, 1.3, y, 6, 0.4, name, size=18), text(s, 7.3, y, 1.4, 0.4, f"cost {value}", size=20, color=color, bold=True)]
total_a = text(s, 1.0, 3.65, 4.5, 0.45, "cost = mean prediction cost +", size=20, align=RIGHT)
total_b = text(s, 5.6, 3.65, 2.6, 0.45, "max{ECE − 0.1, 0}", size=20)
penalty_box = rect(s, 5.48, 3.6, 2.4, 0.55, line=RED, line_w=2.25)
point = text(s, 0.5, 4.5, 9, 0.5, "Not accuracy: knowing how much you know", size=22, color=YELLOW, align=CENTER)
Timing().build(s, [
    [(options, "fade_in", 0)],
    [(sp, "fly_left", 400 * (i // 2)) for i, sp in enumerate(rows)],
    [(total_a, "fade_in", 0), (total_b, "fade_in", 0), (penalty_box, "zoom_in", 700)],
    [(point, "fade_in", 0)],
])


# S02 DecisionRule
s = deck.slide(
    "Suppose your model says its top class has probability p, and suppose that number is honest. [click] If you "
    "commit to the class, you are wrong with probability one minus p, so the expected cost is three times one minus "
    "p. [click] If you say “don't know”, you pay one, no matter what. [click] The two lines cross where three times "
    "one minus p equals one: at p equals two thirds. Above it, commit. Below it, abstain. That is exactly the default "
    "threshold in the template. [click] Here is what this does with the pretrained MAP network you are given, on the "
    "hundred and forty validation images. Always predicting the top class costs zero point seven seven. [click] With "
    "the two thirds rule, zero point six six. [click] The best threshold on this validation set would be zero point "
    "eight eight, at zero point five. But that is a hundred and forty images; a threshold tuned this finely will not "
    "transfer to the test set. [click] The real problem is the word “honest”. The two thirds rule assumes that a "
    "confidence of ninety percent really means ninety percent. Does it?"
)
title(s, "When to say “don't know”")
P = Plot(1.0, 1.75, 3.9, 2.9, (0, 1), (0, 3))
ox, oy = P(0, 0)
line(s, ox, oy, *P(1.05, 0), color=GREY_B, arrow=True)
line(s, ox, oy, *P(0, 3.25), color=GREY_B, arrow=True)
for v, t in [(0, "0"), (1, "1")]:
    x, y = P(v, 0)
    text(s, x - 0.3, y + 0.05, 0.6, 0.25, t, size=12, color=GREY_A, align=CENTER)
for v in (1, 2, 3):
    x, y = P(0, v)
    line(s, x - 0.06, y, x, y, color=GREY_B)
    text(s, x - 0.45, y - 0.13, 0.35, 0.25, str(v), size=12, color=GREY_A, align=RIGHT)
text(s, ox, oy + 0.35, 3.9, 0.3, "p = top-class probability", size=14, italic=True, align=CENTER)
text(s, ox - 0.4, 1.2, 2.5, 0.3, "expected cost", size=14)
commit = line(s, *P(0, 3), *P(1, 0), color=BLUE_C, width=3)
commit_label = text(s, *P(0.25, 2.85), 2.2, 0.3, "predict: 3(1 − p)", size=15, color=BLUE_C)
abstain = line(s, *P(0, 1), *P(1, 1), color=YELLOW, width=3)
abstain_label = text(s, *P(0.18, 1.33), 2.2, 0.3, "don't know: 1", size=15, color=YELLOW)
cx, cy = P(2 / 3, 1)
cross = dot(s, cx, cy, 0.06, WHITE)
drop = line(s, cx, cy, cx, oy, color=WHITE, width=1.5, dash=True)
third = text(s, cx - 0.3, oy + 0.05, 0.6, 0.25, "2/3", size=12, align=CENTER)
region_a = text(s, *P(0.18, 0.45), 1.2, 0.3, "abstain", size=14, color=YELLOW)
region_c = text(s, *P(0.75, 1.85), 1.2, 0.3, "commit", size=14, color=BLUE_C)
rule = text(s, 5.6, 1.15, 3.9, 0.5, "3(1 − p) < 1  ⇔  p > 2/3", size=22, align=CENTER)
rule_box = rect(s, 5.55, 1.1, 4.0, 0.6, line=YELLOW, line_w=2.25)
honest = text(s, 5.6, 1.75, 3.9, 0.35, "assumes p is honest", size=18, color=YELLOW, align=RIGHT)
cost_rows = []
for i, (name, value, color) in enumerate([
    ("always top class", MAP_VAL["cost_argmax"], GREY_A),
    ("threshold 2/3", MAP_VAL["cost_two_thirds"], BLUE_C),
    ("best val threshold 0.88", min(MAP_VAL["costs"]), RED),
]):
    y = 2.45 + i * 0.45
    cost_rows.append([text(s, 5.6, y, 2.9, 0.35, name, size=16, color=color, align=RIGHT),
                      text(s, 8.6, y, 0.9, 0.35, f"{value:.3f}", size=18, color=color, bold=True, align=RIGHT)])
source = text(s, 5.0, 3.85, 4.5, 0.25, "provided MAP weights, 140 val. images, no ECE penalty", size=11,
              color=GREY_B, align=RIGHT)
warning = text(s, 5.6, 4.15, 3.9, 0.3, "140 images: will not transfer", size=15, color=RED, align=RIGHT)
Timing().build(s, [
    [(commit, "fade_in", 0), (commit_label, "fade_in", 200)],
    [(abstain, "fade_in", 0), (abstain_label, "fade_in", 200)],
    [(cross, "zoom_in", 0), (drop, "fade_in", 0), (third, "fade_in", 0),
     (rule, "fade_in", 500), (region_a, "fade_in", 500), (region_c, "fade_in", 500)],
    appear(cost_rows[0]) + [(source, "fade_in", 0)],
    appear(cost_rows[1]),
    appear(cost_rows[2]) + [(warning, "fade_in", 400)],
    [(rule_box, "zoom_in", 0), (honest, "fade_in", 300)],
])


# S03 CalibrationCheck (real MAP validation bins)
s = deck.slide(
    "A reliability diagram answers that. [click] Sort predictions into twenty bins by confidence, and in each bin "
    "compare the average confidence with the fraction that was actually right. A perfectly calibrated model sits on "
    "the diagonal. [click] The expected calibration error is the average gap, weighted by how many predictions fall "
    "in each bin. [click] Note that ambiguous images count as wrong, whatever class you predict. [click] For the MAP "
    "network, the bars sit below the diagonal: it is overconfident. Its validation error is about zero point one "
    "nine, which alone would add almost zero point one to your cost. And no threshold can fix that: the error is "
    "computed from the probabilities, not from your decisions. [click] And on the twenty ambiguous images, its "
    "average confidence is still eighty seven percent. It is sure exactly where it should not be. [click] The reason "
    "is that MAP keeps one single network. It has no way to express that other, equally good weights would answer "
    "differently."
)
title(s, "Is 90% really 90%?")
P = Plot(1.0, 1.55, 3.2, 3.2, (0, 1), (0, 1))
ox, oy = P(0, 0)
line(s, ox, oy, *P(1.04, 0), color=GREY_B, arrow=True)
line(s, ox, oy, *P(0, 1.04), color=GREY_B, arrow=True)
for v, t in [(0, "0"), (0.5, "0.5"), (1, "1")]:
    x, y = P(v, 0)
    text(s, x - 0.3, y + 0.05, 0.6, 0.25, t, size=12, color=GREY_A, align=CENTER)
for v, t in [(0.5, "0.5"), (1, "1")]:
    x, y = P(0, v)
    text(s, x - 0.45, y - 0.13, 0.35, 0.25, t, size=12, color=GREY_A, align=RIGHT)
text(s, ox, oy + 0.32, 3.2, 0.3, "confidence", size=14, align=CENTER)
acc_title = text(s, ox - 1.4, 3.0, 1.6, 0.3, "accuracy", size=14, align=CENTER)
acc_title.rotation = 270
tag(s, "provided MAP weights, 140 validation images, 20 bins", x=ox - 0.1, y=1.2, w=4.5, align=LEFT)
diagonal = line(s, ox, oy, *P(1, 1), color=GREY_A, width=1.5, dash=True)
bin_w = P.w / 20
bars, gaps = [], []
for row in MAP_VAL["bins"]:
    x_left = P(row["lo"], 0)[0] + bin_w * 0.05
    top = P(0, row["acc"])[1]
    bars.append(rect(s, x_left, top, bin_w * 0.9, max(oy - top, 0.01), fill=BLUE_C, alpha=0.7, line=WHITE, line_w=0.5))
    low, high = sorted([row["acc"], row["conf"]])
    gap_top, gap_bottom = P(0, high)[1], P(0, low)[1]
    gaps.append(rect(s, x_left, gap_top, bin_w * 0.9, max(gap_bottom - gap_top, 0.01), fill=RED, alpha=0.35,
                     line=RED, line_w=0.5))
legend = []
for i, (label, kind) in enumerate([("accuracy in bin", "bar"), ("gap to confidence", "gap"), ("perfect calibration", "diag")]):
    y = 1.75 + i * 0.27
    if kind == "bar":
        mark = rect(s, ox + 0.1, y + 0.03, 0.16, 0.16, fill=BLUE_C, alpha=0.7, line=WHITE, line_w=0.5)
    elif kind == "gap":
        mark = rect(s, ox + 0.1, y + 0.03, 0.16, 0.16, fill=RED, alpha=0.35, line=RED, line_w=0.5)
    else:
        mark = line(s, ox + 0.08, y + 0.11, ox + 0.3, y + 0.11, color=GREY_A, width=1.5, dash=True)
    legend.append((mark, text(s, ox + 0.38, y, 1.6, 0.22, label, size=11, color=GREY_A)))
ece = formula(s, "ece", 5.0, 1.15)
amb_note = text(s, 5.0, 2.15, 4.6, 0.3, "ambiguous image: always counted as wrong", size=15, color=YELLOW)
value = text(s, 5.0, 2.65, 4.6, 0.35,
             f"ECE(MAP) ≈ {MAP_VAL['ece']:.3f}  ⇒  penalty ≈ {MAP_VAL['ece'] - 0.1:.3f}", size=18,
             color=RED, bold=True)
over = text(s, 5.0, 3.05, 4.6, 0.3, "overconfident: bars below the diagonal", size=15)
amb_conf = text(s, 5.0, 3.6, 4.6, 0.3, f"20 ambiguous images: mean confidence {MAP_VAL['conf_amb']:.2f}",
                size=15, color=YELLOW)
single = text(s, 5.0, 4.25, 4.6, 0.4, "MAP keeps a single network", size=20)
Timing().build(s, [
    [(diagonal, "fade_in", 0)] + appear(bars, "fly_up", stagger=60)
    + appear([legend[0][0], legend[0][1], legend[2][0], legend[2][1]])
    + appear(gaps, delay=1200) + appear(legend[1], delay=1200),
    [(ece, "fade_in", 0)],
    [(amb_note, "fade_in", 0)],
    [(value, "fade_in", 0), (over, "fade_in", 300)],
    [(amb_conf, "fly_up", 0)],
    [(single, "fade_in", 0)],
])


# S04 BayesianAveraging (illustrative probabilities, as in the video)
AGREE = np.array([
    [0.02, 0.03, 0.88, 0.03, 0.02, 0.02],
    [0.03, 0.02, 0.85, 0.05, 0.03, 0.02],
    [0.02, 0.04, 0.90, 0.02, 0.01, 0.01],
])
DISAGREE = np.array([
    [0.05, 0.03, 0.80, 0.04, 0.05, 0.03],
    [0.04, 0.03, 0.06, 0.04, 0.79, 0.04],
    [0.70, 0.05, 0.10, 0.05, 0.06, 0.04],
])


def bars(slide, probs, x, base_y, width, height, color):
    slot = width / 6
    shapes = [
        rect(slide, x + i * slot + slot * 0.1, base_y - max(height * p, 0.01), slot * 0.8, max(height * p, 0.01), fill=color)
        for i, p in enumerate(probs)
    ]
    return shapes, line(slide, x - 0.05, base_y, x + width + 0.05, base_y, color=GREY_B, width=1)


def panel(slide, probs, x0, heading):
    """Three networks' bars and their average; returns the effects for one click"""
    single_w, gap, single_h, top = 1.2, 0.2, 0.75, 2.65
    effects = [(text(slide, x0, 2.27, 3 * single_w + 2 * gap, 0.3, heading, size=16, color=GREY_A, align=CENTER), "fade_in", 0)]
    for i, p in enumerate(probs):
        x = x0 + i * (single_w + gap)
        shapes, base = bars(slide, p, x, top + single_h, single_w, single_h, BLUE_B)
        label = text(slide, x, top + single_h + 0.04, single_w, 0.25, f"θ{chr(0x2081 + i)}", size=14, color=GREY_A,
                     align=CENTER)
        effects += [(base, "fade_in", 300 * i), (label, "fade_in", 300 * i)] + appear(shapes, "fly_up", 300 * i)
    avg_w, avg_h = 1.8, 0.8
    avg_x = x0 + (3 * single_w + 2 * gap - avg_w) / 2 + 0.3
    shapes, base = bars(slide, probs.mean(0), avg_x, 4.55, avg_w, avg_h, YELLOW)
    label = text(slide, avg_x - 1.0, 4.25, 0.9, 0.3, "average", size=14, color=YELLOW, align=RIGHT)
    return effects + [(base, "fade_in", 1100), (label, "fade_in", 1100)] + appear(shapes, "fly_up", 1100)


s = deck.slide(
    "The Bayesian answer is to keep all of them. [click] The posterior predictive averages the prediction of every "
    "weight vector, weighted by its posterior probability. [click] We cannot do that integral, but we can sample: "
    "draw S networks from an approximate posterior, and average their predicted probabilities. [click] Where the "
    "networks agree, the average stays confident. [click] Where they disagree, as on an ambiguous image, the average "
    "spreads out, and its top probability drops below your threshold. [click] Average the probabilities themselves, "
    "after the softmax. Averaging weights would just give you one network again. So the whole question becomes: "
    "where do we get a cheap, decent approximate posterior for a neural network?"
)
title(s, "Average over many networks")
integral = formula(s, "integral", 5.0, 0.95, align=CENTER, scale=0.85)
mc = formula(s, "mc", 5.0, 1.47, align=CENTER, scale=0.85)
agree = panel(s, AGREE, 0.5, "networks agree")
disagree = panel(s, DISAGREE, 5.4, "networks disagree")
verdict = text(s, 5.4, 4.72, 4.0, 0.35, f"max = {DISAGREE.mean(0).max():.2f} < 2/3  ⇒  don't know", size=16,
               color=YELLOW, align=CENTER)
rule = text(s, 0.5, 4.72, 4.6, 0.35, "average probabilities (after softmax), not weights", size=15, color=YELLOW,
            align=CENTER)
tag(s, "illustration: made-up probabilities")
Timing().build(s, [
    [(integral, "fade_in", 0)],
    [(mc, "fade_in", 0)],
    agree,
    disagree + [(verdict, "zoom_in", 1800)],
    [(rule, "fade_in", 0)],
])


# S05 SwagDiagonal, part 1: SGD exploration (GIF) and the running moments
s = deck.slide(
    "SWAG's idea is that SGD already explores it for you. [click] Start from the pretrained weights and keep running "
    "SGD with a fairly high, constant learning rate. It never settles; it keeps bouncing around the bottom of the "
    "valley. [click] Those iterates trace out the region of good weights. So treat them as samples, and fit a "
    "Gaussian to them. [click] Once per epoch, update two running averages for every weight: the mean, and the mean "
    "of the square. [click] The variance of each weight is the mean of the square minus the square of the mean. In "
    "floating point this can come out slightly negative, so clamp it at zero before taking a square root."
)
title(s, "SWAG: let SGD explore the valley")
picture(s, "assets/sgd.gif", 0.4, 1.05, w=5.2)
lr = text(s, 5.9, 1.1, 3.8, 0.35, "constant, fairly high learning rate", size=16, color=PINK)
samples_note = text(s, 5.9, 1.55, 3.8, 0.55, "kept iterates ≈ samples from the\nregion of good weights", size=14,
                    color=GREY_A, anchor=MSO_ANCHOR.TOP)
mean_f = formula(s, "mean", 5.9, 2.25)
sq_f = formula(s, "sq", 7.4, 2.22)
when = text(s, 5.9, 2.75, 3.8, 0.28, "once per epoch, elementwise", size=12, color=GREY_B)
var_f = formula(s, "variance", 5.9, 3.25)
var_box = rect(s, 5.85, 3.2, inches(var_f.width) + 0.1, inches(var_f.height) + 0.1, line=RED, line_w=2)
clamp = text(s, 5.9, 3.8, 3.8, 0.28, "clamp: float error can go negative", size=13, color=RED)
Timing().build(s, [
    [(lr, "fade_in", 0)],
    [(samples_note, "fade_in", 0)],
    [(mean_f, "fade_in", 0), (sq_f, "fade_in", 300), (when, "fade_in", 300)],
    [(var_f, "fade_in", 0), (var_box, "zoom_in", 600), (clamp, "fade_in", 600)],
])


# Toy plot shared by the SWAG slides: native contours, kept iterates, mean, ellipses
TP = Plot(0.4, 1.0, 5.2, 4.2, (-3.1, 3.1), (-2.5, 2.5))


def toy_ellipse(slide, center, Sigma, k, color, width=2.25, alpha=None):
    w, h, a = ellipse_params(Sigma, k)
    a = (a + 90) % 180 - 90
    cx, cy = TP(*center)
    W, H = w * TP.scale(), h * TP.scale()
    sp = shape(slide, MSO_SHAPE.OVAL, cx - W / 2, cy - H / 2, W, H, line=color, line_w=width, rot=-a)
    if alpha is not None:
        set_alpha(sp.line._get_or_add_ln().find(qn("a:solidFill")), alpha)
    return sp


def toy_background(slide, dot_alpha=None):
    ox, oy = TP(0, 0)
    line(slide, *TP(-3.0, 0), *TP(3.0, 0), color=GREY_D, width=1, arrow=True)
    line(slide, *TP(0, -2.4), *TP(0, 2.4), color=GREY_D, width=1, arrow=True)
    text(slide, *TP(3.0, -0.05), 0.35, 0.25, "θ₁", size=12, color=GREY_B)
    x, y = TP(0.08, 2.45)
    text(slide, x, y, 0.35, 0.25, "θ₂", size=12, color=GREY_B)
    for level in (0.2, 0.7, 1.5):
        toy_ellipse(slide, np.zeros(2), contour_cov(level), 1, GREY_C, 1)
    return [dot(slide, *TP(*p), 0.035, BLUE_B, alpha=dot_alpha) for p in TOY["collected"]]


def samples(Sigma, n, seed):
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(TOY["mean"], Sigma, size=n)


# S05 SwagDiagonal, part 2: diagonal Gaussian, sampling, mismatch
s = deck.slide(
    "[click] That is SWAG diagonal: a Gaussian centred at the average weights, with one independent variance per "
    "weight. [click] To sample a network, take the mean and add the standard deviation times fresh standard normal "
    "noise. [click] But look at the shape. The valley is tilted, and an axis-aligned ellipse cannot follow it."
)
title(s, "SWAG-diagonal: one variance per weight")
dots = toy_background(s)
mean = dot(s, *TP(*TOY["mean"]), 0.08, YELLOW, outline="000000")
diag = [toy_ellipse(s, TOY["mean"], TOY["Sigma_diag"], k, TEAL) for k in (1, 2)]
gaussian = formula(s, "gaussian", 6.0, 1.3)
sample_f = formula(s, "sample_diag", 6.0, 1.95)
diag_samples = [dot(s, *TP(*p), 0.025, TEAL) for p in samples(TOY["Sigma_diag"], 150, 3)]
ux, uy = np.cos(VALLEY_ANGLE), np.sin(VALLEY_ANGLE)
valley = line(s, *TP(-2.6 * ux, -2.6 * uy), *TP(2.6 * ux, 2.6 * uy), color=RED, width=2.25, dash=True)
mismatch = text(s, 6.0, 2.75, 3.6, 0.35, "axis-aligned: cannot tilt", size=16, color=RED)
legend = [
    text(s, 6.0, 3.6, 3.6, 0.28, "kept SGD iterates", size=13, color=BLUE_B),
    text(s, 6.0, 3.9, 3.6, 0.28, "SWA mean", size=13, color=YELLOW),
    text(s, 6.0, 4.2, 3.6, 0.28, "SWAG-diagonal: 1σ and 2σ, samples", size=13, color=TEAL),
]
tag(s, "illustration: toy 2-D loss, noisy constant-step SGD")
Timing().build(s, [
    appear(diag, stagger=300) + [(gaussian, "fade_in", 0), (legend[2], "fade_in", 0)],
    [(sample_f, "fade_in", 0)] + appear(diag_samples, "zoom_in", 400, stagger=8),
    [(valley, "fade_in", 0), (mismatch, "fade_in", 300)],
])


# S06 SwagFull
s = deck.slide(
    "Full SWAG adds a low rank part. [click] Besides the moments, keep the last K deviations, each one the current "
    "weights minus the running mean. Stack them as the columns of a matrix D hat. The template uses K equals "
    "fifteen. [click] The covariance is one half of the diagonal part, plus D hat D hat transpose over K minus one. "
    "[click] You never build that matrix. To sample, add two noise terms: the diagonal one, scaled by one over root "
    "two, and D hat times a K dimensional standard normal, scaled by one over the root of two times K minus one. "
    "Draw that K dimensional noise once per sampled network, and share it across all layers; otherwise the layers "
    "lose their correlations. [click] Now the ellipse tilts with the valley. [click] One more step from the paper's "
    "algorithm: after setting new weights, recompute the batch normalization statistics on the training data. Their "
    "stored averages belong to the old weights, not to the sampled network."
)
title(s, "Full SWAG: low rank plus diagonal")
toy_background(s, dot_alpha=0.5)
toy_ellipse(s, TOY["mean"], TOY["Sigma_diag"], 2, TEAL, width=1.5, alpha=0.5)
dot(s, *TP(*TOY["mean"]), 0.08, YELLOW, outline="000000")
K = len(TOY["deviations"])
arrows = [
    line(s, *TP(*m), *TP(*p), color=PINK, width=1.5, arrow=True)
    for m, p in zip(TOY["means"][-K:], TOY["collected"][-K:])
]
dev_f = formula(s, "deviation", 5.9, 1.0)
matrix_f = formula(s, "matrix", 5.9, 1.38)
k_note = text(s, 5.9, 1.75, 3.8, 0.25, "K = 15 in the template", size=12, color=GREY_B)
cov_f = formula(s, "covariance", 5.9, 2.1)
sample_f = formula(s, "sample_full", 5.9, 2.6)
dims_f = formula(s, "dims", 5.9, 3.1)
shared = text(s, 5.9, 3.4, 3.8, 0.28, "one z₂ per network, shared by all layers", size=13, color=YELLOW)
full = [toy_ellipse(s, TOY["mean"], TOY["Sigma_full"], k, PINK) for k in (1, 2)]
full_samples = [dot(s, *TP(*p), 0.025, PINK) for p in samples(TOY["Sigma_full"], 150, 5)]
bn_box = box(s, 5.9, 3.9, 3.7, 0.95, color=YELLOW)
bn_text = text(s, 6.05, 3.95, 3.45, 0.85, "after every sample:\nrecompute BatchNorm statistics\non the training data",
               size=14)
tag(s, "illustration: toy 2-D loss, K = 15")
Timing().build(s, [
    [(dev_f, "fade_in", 0)] + appear(arrows, stagger=60) + [(matrix_f, "fade_in", 900), (k_note, "fade_in", 900)],
    [(cov_f, "fade_in", 0)],
    [(sample_f, "fade_in", 0), (dims_f, "fade_in", 500), (shared, "fade_in", 500)],
    appear(full, stagger=300) + appear(full_samples, "zoom_in", 700, stagger=8),
    [(bn_box, "zoom_in", 0), (bn_text, "fade_in", 200)],
])


# S07 FullRecipe
s = deck.slide(
    "Here is the whole pipeline. [click] Load the pretrained MAP weights. [click] Run SGD at a constant learning "
    "rate, thirty epochs in the template, updating the SWAG statistics as you go. [click] Draw thirty networks; for "
    "each, refresh batch norm and predict probabilities for all images. [click] Average them, then decide: a class, "
    "or “don't know”. [click] To get the cost down further, the task and the template point to three levers: the "
    "learning rate schedule, post hoc calibration such as temperature scaling, and a smarter mapping from "
    "probabilities to decisions. [click] Use the validation set for calibration only, and remember how small it is. "
    "[click] Finally, the rules: AI tools are allowed, but you must understand and justify every line, and disclose "
    "what you used. The exercises that come with this video help you check exactly that. Good luck."
)
title(s, "The whole pipeline")
steps = []
for i, (head, detail, color) in enumerate([
    ("MAP weights", "map_weights.pt", WHITE),
    ("SGD + moments", "30 epochs, lr 0.045\nconstant", BLUE_B),
    ("sample S = 30", "refresh BatchNorm,\npredict probabilities", PINK),
    ("average + decide", "class, or\n“don't know”", YELLOW),
]):
    x = 0.45 + i * 2.35
    frame = box(s, x, 1.1, 1.95, 1.15, color=color, width=2)
    label = text(s, x + 0.05, 1.2, 1.85, 0.35, head, size=14, color=color, bold=True, align=CENTER)
    sub = text(s, x + 0.1, 1.55, 1.75, 0.6, detail, size=12, color=GREY_A, align=CENTER)
    steps.append([frame, label, sub])
arrows = [line(s, 0.45 + i * 2.35 + 1.98, 1.675, 0.45 + (i + 1) * 2.35 - 0.03, 1.675, color=GREY_B, width=2, arrow=True)
          for i in range(3)]
source = tag(s, "defaults from the handout's solution.py", y=2.35, x=4.0, w=5.6)
levers_title = text(s, 0.5, 2.9, 5.2, 0.35, "Levers from the task and template", size=18, bold=True)
levers = [
    text(s, 0.7, 3.35 + i * 0.35, 5.2, 0.3, "•  " + t, size=14)
    for i, t in enumerate([
        "learning-rate schedule (SWAGScheduler)",
        "post-hoc calibration, e.g. temperature scaling",
        "smarter mapping from probabilities to decisions",
    ])
]
validation = text(s, 0.5, 4.55, 5.2, 0.35, "validation: 140 images, calibration only", size=15, color=RED)
rules_box = box(s, 6.3, 3.0, 3.2, 1.25, color=YELLOW)
rules = text(s, 6.45, 3.05, 2.95, 1.15, "AI tools allowed:\nunderstand every line,\ndisclose what you used", size=14)
Timing().build(s, [
    appear(steps[0], "fly_left") + [(source, "fade_in", 0)],
    [(arrows[0], "fade_in", 0)] + appear(steps[1], "fly_left", 200),
    [(arrows[1], "fade_in", 0)] + appear(steps[2], "fly_left", 200),
    [(arrows[2], "fade_in", 0)] + appear(steps[3], "fly_left", 200),
    [(levers_title, "fade_in", 0)] + appear(levers, "fly_left", 300, stagger=300),
    [(validation, "fade_in", 0)],
    [(rules_box, "zoom_in", 0), (rules, "fade_in", 200)],
])


# Sources
s = deck.slide("Sources and notes for this deck.")
title(s, "Sources and notes")
text(s, 0.5, 1.1, 9, 3.9, "\n".join([
    "Maddox, Garipov, Izmailov, Vetrov, Wilson. A Simple Baseline for Bayesian Uncertainty in Deep Learning. "
    "NeurIPS 2019, arXiv:1902.02476.",
    "Guo, Pleiss, Sun, Weinberger. On Calibration of Modern Neural Networks. ICML 2017, arXiv:1706.04599.",
    "ETH Zürich, Probabilistic Artificial Intelligence, Task 2 description and handout (2026).",
    "",
    "Validation numbers: computed from the handout's provided MAP weights on the 140 validation images.",
    "SWAG plots: toy 2-D loss with noisy constant-step SGD; illustrations, not the real network.",
    "Bar charts on the averaging slide: made-up probabilities.",
]), size=14, color=GREY_A, anchor=MSO_ANCHOR.TOP)

deck.save("pai_task2_swag.pptx")
print("saved", len(deck.prs.slides._sldIdLst), "slides")
