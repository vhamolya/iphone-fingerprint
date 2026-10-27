"""Which iPhone took this photo? The method of the post, in one module.

A photo I is the scene I⁰ seen through the pixel gains K, plus fresh noise Θ: I = I⁰ + I⁰K + Θ.
K is the phone's fingerprint. The method has three steps:

1. noise: subtract a cleaned copy of the photo, W = I − F(I) ≈ IK + Ξ;
2. fingerprint: average the noise of many photos of one phone, K̂ = Σ WᵢIᵢ / Σ Iᵢ²;
3. score: compare a new photo's noise with the pattern it should carry, I·K̂, as a PCE.

Before the score, the clean-up removes the shared pattern: the part of a fingerprint that every phone of one
model carries. Post: https://vhamolya.com/blog/which-iphone-took-this-photo/
"""
from functools import cache
from os import PathLike
from pathlib import Path

import numpy as np
import pywt
from PIL import Image
from scipy.ndimage import uniform_filter

# The post's defaults ("The method in formulas"). Try a change in a new experiment, not here.
WAVELET = 'db4'           # Daubechies wavelets for the cleaned copy
LEVELS = 4                # over four levels
SIGMA = 5.0               # σ: the grain the filter expects, on the 0 to 255 scale
WINDOWS = (3, 5, 7, 9)    # window sizes for the spread of the details, in pixels
PEAK = 11                 # the score leaves out an 11 × 11 window around the peak
SPIKE = 3.0               # the clean-up flattens spectrum peaks above 3 times their local mean
SPIKE_WINDOW = 9          # local mean over 9 × 9 frequencies
THRESHOLD = 60            # a score above about 60 usually means the same phone (Goljan and others, 2009)


def load(path: str | PathLike) -> np.ndarray:
    """A photo as grey levels from 0 to 255. It ignores the EXIF rotation, so the pixels stay in the sensor's order."""
    return np.asarray(Image.open(path).convert('L'), np.float32)


def _grain(c: np.ndarray, var: float) -> np.ndarray:
    """The share of each wavelet detail c that looks like grain: c σ² / (σ̂² + σ²), with σ̂² = max(0, mean c² − σ²).
    The mean of c² is taken in windows of 3 to 9 pixels, and the smallest one is kept."""
    spread = np.min([uniform_filter(c * c, w, mode='constant') for w in WINDOWS], axis=0)
    return c * var / (np.maximum(spread - var, 0) + var)


def _grain_image(photo: np.ndarray, sigma: float) -> np.ndarray:
    coeffs = pywt.wavedec2(photo, WAVELET, level=LEVELS)
    kept = [np.zeros_like(coeffs[0])] + [tuple(_grain(c, sigma ** 2) for c in bands) for bands in coeffs[1:]]
    return pywt.waverec2(kept, WAVELET)[:photo.shape[0], :photo.shape[1]]


def cleaned_copy(photo: np.ndarray, sigma: float = SIGMA) -> np.ndarray:
    """F(I): the photo without its fine grain. Mihcak's wavelet filter, as in Lukáš, Fridrich and Goljan (2006)."""
    return photo - _grain_image(photo, sigma)


def noise(photo: np.ndarray, sigma: float = SIGMA) -> np.ndarray:
    """W = I − F(I), less its row and column means. Those come from the readout, not from one pixel's gain."""
    w = _grain_image(photo, sigma)
    return (w - w.mean(1, keepdims=True) - w.mean(0, keepdims=True)).astype(np.float32)


def fingerprint(photos) -> np.ndarray:
    """K̂ = Σ WᵢIᵢ / Σ Iᵢ², from photos of one phone (paths or arrays). Bright photos carry more of the pattern,
    so they weigh more. The 1 in the bottom only keeps black pixels from dividing by zero."""
    top = bottom = 0
    for p in photos:
        photo = p if isinstance(p, np.ndarray) else load(p)
        top, bottom = top + noise(photo) * photo, bottom + photo * photo
    return top / (bottom + 1)


def zero_mean(x: np.ndarray) -> np.ndarray:
    """Zero-mean each of the four 2 × 2 sub-grids by rows and by columns. Patterns that repeat along whole rows or
    columns, such as the colour filter's grid, are the same in every phone of a model."""
    x = x.copy()
    for dy in (0, 1):
        for dx in (0, 1):
            s = x[dy::2, dx::2]
            s -= s.mean(1, keepdims=True)
            s -= s.mean(0, keepdims=True)
    return x


def flatten(k: np.ndarray) -> np.ndarray:
    """Flatten sharp peaks in the spectrum: a pattern that repeats across the frame is processing, not one pixel."""
    f = np.fft.fft2(k)
    m = np.abs(f)
    local = uniform_filter(m, SPIKE_WINDOW)
    return np.real(np.fft.ifft2(np.where(m > SPIKE * local, f * local / np.maximum(m, 1e-9), f))).astype(np.float32)


def clean_up(k: np.ndarray) -> np.ndarray:
    """Remove the shared pattern from a fingerprint before scoring."""
    return flatten(zero_mean(k))


def correlation(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson's r over all pixels: 0 means no relation, 1 means the same pattern."""
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def pce(w: np.ndarray, pattern: np.ndarray, window: int = PEAK) -> float:
    """Peak-to-correlation energy: ρ(0)² over the mean ρ(s)² of every shift s outside a window around the peak.
    It keeps the sign of the peak, so a match below zero stays below zero. Unrelated noise scores near 1."""
    c = np.real(np.fft.ifft2(np.fft.fft2(w - w.mean()) * np.conj(np.fft.fft2(pattern - pattern.mean()))))
    near = np.r_[0:window // 2 + 1, -(window // 2):0]
    far = np.ones(c.shape, bool)
    far[np.ix_(near, near)] = False
    return float(np.sign(c[0, 0]) * c[0, 0] ** 2 / np.mean(c[far] ** 2))


def score(photo, k: np.ndarray) -> float:
    """The score of one photo (a path or an array) against a cleaned fingerprint k = clean_up(fingerprint(...))."""
    photo = photo if isinstance(photo, np.ndarray) else load(photo)
    return pce(zero_mean(noise(photo)), photo * k)


# Simulated phones, for the experiments and the tests. They exaggerate: a real K is far fainter.

SCENES = Path(__file__).resolve().parent / 'data' / 'scenes'


@cache
def _scenes() -> list[np.ndarray]:
    return [load(p) for p in sorted(SCENES.glob('*.jpg'))]


def scene(rng: np.random.Generator, size: int = 512) -> np.ndarray:
    """A real scene: a random crop of one of 8 Commons photos in data/scenes/, cleaned of their own grain.
    Their credits are in data/scenes/CREDITS.md."""
    pool = _scenes()
    s = pool[rng.integers(len(pool))]
    y, x = (rng.integers(0, n - size + 1) for n in s.shape)
    return s[y:y + size, x:x + size].copy()


class SimulatedPhone:
    """A phone made in code: photo = scene × (1 + K) + fresh noise. Each photo gets new fresh noise."""

    def __init__(self, seed: int, size: int = 512, strength: float = 0.02, fresh: float = 2.0):
        self.rng = np.random.default_rng(seed)
        self.k = (strength * self.rng.standard_normal((size, size))).astype(np.float32)
        self.fresh = fresh

    def photo(self, scene: np.ndarray) -> np.ndarray:
        shot = scene * (1 + self.k) + self.fresh * self.rng.standard_normal(scene.shape)
        return np.clip(shot, 0, 255).astype(np.float32)
