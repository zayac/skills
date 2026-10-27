"""Toy SWAG valley, copied from video/scenes/common.py without the ManimGL import"""
import numpy as np

VALLEY_ANGLE = np.deg2rad(35)
VALLEY_CURVATURES = np.array([0.35, 4.0])


def get_valley_hessian():
    c, s = np.cos(VALLEY_ANGLE), np.sin(VALLEY_ANGLE)
    R = np.array([[c, -s], [s, c]])
    return R @ np.diag(VALLEY_CURVATURES) @ R.T


def get_sgd_iterates(n_steps=600, lr=0.12, noise=1.6, start=(-2.6, 1.6), seed=4):
    rng = np.random.default_rng(seed)
    H = get_valley_hessian()
    theta = np.array(start, dtype=float)
    path = [theta.copy()]
    for _ in range(n_steps):
        grad = H @ theta + noise * rng.normal(size=2)
        theta = theta - lr * grad
        path.append(theta.copy())
    return np.array(path)


def get_swag_toy(burn_in=100, every=20, K=15, n_epochs=60, seed=2):
    path = get_sgd_iterates(n_steps=burn_in + every * n_epochs, seed=seed)
    collected = path[burn_in::every]
    n = len(collected)
    means = np.cumsum(collected, axis=0) / np.arange(1, n + 1)[:, None]
    mean = means[-1]
    sq_mean = (collected ** 2).mean(0)
    var = np.clip(sq_mean - mean ** 2, 0, None)
    deviations = (collected - means)[-K:]
    Sigma_diag = np.diag(var)
    Sigma_low = deviations.T @ deviations / (K - 1)
    return dict(path=path, collected=collected, mean=mean, var=var, deviations=deviations,
                means=means, Sigma_diag=Sigma_diag, Sigma_full=0.5 * (Sigma_diag + Sigma_low))


def ellipse_params(Sigma, k=2.0):
    """Full width, full height and counter-clockwise angle (degrees) of the k-sigma ellipse"""
    vals, vecs = np.linalg.eigh(Sigma)
    major = vecs[:, 1]
    angle = np.degrees(np.arctan2(major[1], major[0]))
    return 2 * k * np.sqrt(vals[1]), 2 * k * np.sqrt(vals[0]), angle


def contour_cov(level):
    """Covariance whose 1-sigma ellipse is the level set 0.5 theta^T H theta = level"""
    return np.linalg.inv(get_valley_hessian()) * 2 * level
