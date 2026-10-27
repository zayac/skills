"""Formula PNGs (matplotlib mathtext, natural size at 300 dpi) and the SGD GIF for the deck"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Ellipse
from toy import get_swag_toy, ellipse_params, contour_cov

BG = "#1C1C1C"
WHITE, SGD, SWA, GREY = "#FFFFFF", "#9CDCEB", "#FFFF00", "#888888"
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "STIXGeneral"  # the deck's text font

# name: (tex, font size in pt as it will appear on the slide, colour)
FORMULAS = {
    "ece": (r"$\mathrm{ECE} = \sum_{m=1}^{20} \frac{|B_m|}{n}\, \left|\mathrm{acc}(B_m) - \mathrm{conf}(B_m)\right|$", 20, WHITE),
    "integral": (r"$p(y \mid x, D) = \int\ \, p(y \mid x, \theta)\, p(\theta \mid D)\, d\theta$", 20, WHITE),
    "mc": (r"$\approx \frac{1}{S} \sum_{s=1}^{S}\, p(y \mid x, \theta_s), \qquad \theta_s \sim q(\theta)$", 20, WHITE),
    "mean": (r"$\bar\theta \leftarrow \frac{n\,\bar\theta + \theta}{n + 1}$", 18, WHITE),
    "sq": (r"$\overline{\theta^2} \leftarrow \frac{n\,\overline{\theta^2} + \theta^2}{n + 1}$", 18, WHITE),
    "variance": (r"$\sigma^2 = \max\left(\overline{\theta^2} - \bar\theta^{\,2},\ 0\right)$", 18, WHITE),
    "gaussian": (r"$\mathcal{N}\left(\bar\theta,\ \mathrm{diag}(\sigma^2)\right)$", 18, WHITE),
    "sample_diag": (r"$\tilde\theta = \bar\theta + \sigma \odot z, \quad z \sim \mathcal{N}(0, I)$", 18, WHITE),
    "deviation": (r"$D_i = \theta_i - \bar\theta_i$", 16, WHITE),
    "matrix": (r"$\hat D = [\,D_{T-K+1}\ \cdots\ D_T\,] \in \mathbb{R}^{d \times K}$", 16, WHITE),
    "covariance": (r"$\Sigma \approx \frac{1}{2}\left(\Sigma_{\mathrm{diag}} + \frac{\hat D \hat D^\top}{K - 1}\right)$", 16, WHITE),
    "sample_full": (r"$\tilde\theta = \bar\theta + \frac{1}{\sqrt{2}}\,\sigma \odot z_1 + \frac{1}{\sqrt{2(K - 1)}}\,\hat D z_2$", 16, WHITE),
    "dims": (r"$z_1 \sim \mathcal{N}(0, I_d), \quad z_2 \sim \mathcal{N}(0, I_K)$", 14, WHITE),
}


def formula(name, tex, size, color):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, tex, fontsize=size, color=color)
    fig.savefig(f"assets/{name}.png", dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def sgd_gif():
    """MAP start, constant-step SGD bouncing in the valley, then the kept iterates and their running mean"""
    toy = get_swag_toy()
    path, burn_in, every = toy["path"], 100, 20
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(-2.45, 2.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    for level in (0.2, 0.7, 1.5):
        w, h, a = ellipse_params(contour_cov(level), k=1)
        ax.add_patch(Ellipse((0, 0), w, h, angle=a, fill=False, ec=GREY, lw=1))
    ax.plot(*path[0], "o", color=WHITE, ms=7)
    ax.text(path[0, 0], path[0, 1] + 0.18, "MAP weights", color=WHITE, fontsize=10, ha="center")
    ax.text(3.2, -2.4, "illustration: toy 2-D loss", color="#BBBBBB", fontsize=9, ha="right", va="bottom")
    trail, = ax.plot([], [], color=SGD, lw=1.2, alpha=0.7)
    head, = ax.plot([], [], "o", color=SGD, ms=5)
    kept = ax.scatter([], [], s=16, color=SGD)
    mean_dot, = ax.plot([], [], "o", color=SWA, ms=9, mec="black")
    caption = ax.text(-3.2, 2.45, "", color=WHITE, fontsize=12, va="top")

    walk_frames, steps_per_frame = 40, 10  # 400 steps of SGD, as in the video
    n = len(toy["collected"])
    keep_frames, kept_per_frame = 31, 2
    hold = 24

    def update(f):
        if f < walk_frames:
            step = (f + 1) * steps_per_frame
            trail.set_data(path[:step + 1, 0], path[:step + 1, 1])
            head.set_data([path[step, 0]], [path[step, 1]])
            caption.set_text("constant learning rate: SGD keeps bouncing")
            kept.set_offsets(np.empty((0, 2)))
            mean_dot.set_data([], [])
        else:
            trail.set_alpha(0.15)
            head.set_data([], [])
            k = min((f - walk_frames + 1) * kept_per_frame, n)
            kept.set_offsets(toy["collected"][:k])
            m = toy["means"][k - 1]
            mean_dot.set_data([m[0]], [m[1]])
            caption.set_text(f"one iterate per epoch: {k} kept; yellow = running mean")
        if f == 0:
            trail.set_alpha(0.7)
        return trail, head, kept, mean_dot, caption

    anim = FuncAnimation(fig, update, frames=walk_frames + keep_frames + hold)
    anim.save("assets/sgd.gif", writer=PillowWriter(fps=10), savefig_kwargs={"facecolor": BG})


if __name__ == "__main__":
    for name, spec in FORMULAS.items():
        formula(name, *spec)
    sgd_gif()
