"""The look of every figure: the palette of vhamolya.com, and the folder the figures go to."""
import os
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

IMG = Path(__file__).resolve().parent.parent / 'docs/img'
PAPER, LINE, INK, GREY, LIGHT = '#f8f7f3', '#e0ddd4', '#18181b', '#52525b', '#a1a1aa'
ACCENT, ACCENT_LINE = '#1d4ed8', '#bfdbfe'   # the key data, and the context

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK, 'axes.labelcolor': GREY,
    'axes.edgecolor': LINE, 'axes.facecolor': PAPER, 'figure.facecolor': PAPER, 'axes.spines.top': False,
    'axes.spines.right': False, 'xtick.color': GREY, 'ytick.color': GREY, 'axes.titlesize': 10,
    'axes.titleweight': 'bold', 'axes.titlelocation': 'left', 'grid.color': LINE, 'grid.linewidth': 0.8,
})


def title(fig, text: str, subtitle: str) -> None:
    """The title states the finding. The subtitle says how to read the figure."""
    fig.text(0.02, 0.97, text, fontsize=14, fontweight='bold', va='top')
    fig.text(0.02, 0.91, subtitle, fontsize=10, color=GREY, va='top')


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
