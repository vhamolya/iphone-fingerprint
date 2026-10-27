"""The look of every figure, after vhamolya.com: a figure plate, the site's palette, and Inter.

A plate is a paper-2 frame with the title (the finding) and a subtitle (how to read it), centred over a white card
that holds the chart. Under the plate stand the figure number and the source line. Inter ships in experiments/fonts/
under the SIL Open Font License, so the figures look the same on every computer.
"""
import os
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

IMG = Path(__file__).resolve().parent.parent / 'docs/img'
FONTS = Path(__file__).resolve().parent / 'fonts'
PAPER, PAPER_2, LINE, WHITE = '#f8f7f3', '#eeece5', '#e0ddd4', '#ffffff'
INK, BODY, GREY, LIGHT = '#18181b', '#3f3f46', '#52525b', '#a1a1aa'   # zinc 900, 700, 600; 400 for marks only
ACCENT, ACCENT_2, ACCENT_LINE = '#1d4ed8', '#93c5fd', '#bfdbfe'      # the key data, secondary data, context
SCENES = 'Scenes: 32 photos by -wuppertaler, Wikimedia Commons, CC BY 4.0. List: data/scenes/CREDITS.md'

for font in FONTS.glob('*.ttf'):
    font_manager.fontManager.addfont(str(font))
plt.rcParams.update({
    'font.family': 'Inter', 'font.size': 8.5, 'text.color': INK, 'axes.labelcolor': GREY, 'axes.labelsize': 8.5,
    'axes.edgecolor': LINE, 'axes.facecolor': WHITE, 'figure.facecolor': PAPER, 'axes.spines.top': False,
    'axes.spines.right': False, 'xtick.color': GREY, 'ytick.color': GREY, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.titlesize': 9, 'axes.titleweight': 'semibold', 'axes.titlelocation': 'left', 'axes.titlecolor': INK,
    'grid.color': LINE, 'grid.linewidth': 0.8, 'axes.unicode_minus': True,
})


def plate(n: int, title: str, subtitle: str, source: str, size: tuple[float, float] = (8, 6)):
    """A figure plate. Returns the figure and the card's (left, bottom, right, top) in figure fractions."""
    fig = plt.figure(figsize=size)
    w, h = size
    pad, foot, radius = 0.12, 0.42, 0.14                   # in inches
    head = 0.78 + 0.2 * (subtitle.count('\n') + 1)          # title, subtitle lines and a gap
    fig.patches.append(FancyBboxPatch((pad, foot), w - 2 * pad, h - foot - pad, transform=fig.dpi_scale_trans,
                                      boxstyle=f'round,pad=0,rounding_size={radius}', fc=PAPER_2, ec='none',
                                      zorder=-2))
    card = (pad + 0.18, foot + 0.18, w - pad - 0.18, h - pad - head)
    fig.patches.append(FancyBboxPatch(card[:2], card[2] - card[0], card[3] - card[1], transform=fig.dpi_scale_trans,
                                      boxstyle=f'round,pad=0,rounding_size={radius / 2}', fc=WHITE, ec='none',
                                      zorder=-1))
    fig.text(0.5, 1 - (pad + 0.2) / h, title, ha='center', va='top', fontsize=12, fontweight='semibold')
    fig.text(0.5, 1 - (pad + 0.5) / h, subtitle, ha='center', va='top', fontsize=9.5, color=GREY,
             linespacing=1.45)
    fig.text(pad / w, 0.16 / h, f'FIGURE {n}', fontsize=7.5, color=GREY, family='DejaVu Sans Mono', va='baseline')
    fig.text((pad + 0.72) / w, 0.16 / h, source, fontsize=7.5, color=GREY, va='baseline')
    return fig, (card[0] / w, card[1] / h, card[2] / w, card[3] / h)


def inside(card, left=0.07, bottom=0.12, right=0.03, top=0.08) -> dict:
    """Margins for a grid of axes inside the card, as fractions of the card."""
    l, b, r, t = card
    return {'left': l + left * (r - l), 'right': r - right * (r - l),
            'bottom': b + bottom * (t - b), 'top': t - top * (t - b)}


def save(fig, path: str | Path) -> Path:
    """Save to docs/img/ when given a name, or to the given path."""
    path = IMG / path if isinstance(path, str) else path
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, metadata={'Software': None})
    plt.close(fig)
    print(f'saved {os.path.relpath(path)}')
    return path


def grey(a, spread: float = 3.0):
    """An array as a grey image: mid-grey is zero, and white and black are `spread` standard deviations."""
    return (0.5 + a / (2 * spread * a.std())).clip(0, 1)
