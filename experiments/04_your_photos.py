"""04. Your photos: build a fingerprint from a folder, then score new photos against it.

Give it a folder of photos from one phone, and new photos or folders to test. It prints each new photo's score. A score
above about 60 usually means the same phone.

What works best:
  - originals straight from the phone: not cropped, resized or edited, and not sent through a messenger;
  - 20 or more photos for the fingerprint, bright and plain ones (sky, walls) rather than dark or busy ones;
  - the main camera at 1×, so that every photo has the same size.

From the iPhone 16 on, Apple's processing adds a pattern that every phone of the model shares. The clean-up removes
part of it, so a stranger's photo can still score above 60 (Part 4 of the post).

Pillow reads JPEG and PNG. For HEIC, add pillow-heif: uv run --with pillow-heif experiments/04_your_photos.py ...
The script reads your photos on your computer and sends them nowhere. It saves nothing unless you ask for a figure.

Run: uv run experiments/04_your_photos.py <folder> <photo or folder> [...] [--figure out/scores.png]
Try: uv run experiments/04_your_photos.py data/fingerprint data/same data/other
"""
import argparse
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import fingerprint as fp
from plots import ACCENT, GREY, LIGHT, save, title

try:
    from pillow_heif import register_heif_opener   # only with `uv run --with pillow-heif`
    register_heif_opener()
except ImportError:
    pass

TYPES = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.heic', '.heif'}


def files(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if p.suffix.lower() in TYPES) if path.is_dir() else [path]


parser = argparse.ArgumentParser(description='Score photos against the fingerprint of a folder of photos.')
parser.add_argument('folder', type=Path, help='photos from one phone')
parser.add_argument('tests', type=Path, nargs='+', help='new photos, or folders of them')
parser.add_argument('--figure', type=Path, help='save a chart of the scores to this file')
args = parser.parse_args()

refs = files(args.folder)
sizes = {p: Image.open(p).size for p in refs}
size, _ = Counter(sizes.values()).most_common(1)[0]
skipped = [p for p in refs if sizes[p] != size]
refs = [p for p in refs if sizes[p] == size]
if skipped:
    print(f'Left out {len(skipped)} photos that are not {size[0]} × {size[1]}: {", ".join(p.name for p in skipped)}')
if len(refs) < 10:
    print(f'Only {len(refs)} photos for the fingerprint. Scores get more reliable with 20 or more.')

start = time.time()
k = fp.clean_up(fp.fingerprint(refs))
print(f'The fingerprint of {len(refs)} photos ({size[0]} × {size[1]}) took {time.time() - start:.0f} s.\n')

results = []
for path in (p for t in args.tests for p in files(t)):
    if Image.open(path).size != size:
        print(f'{path}: not {size[0]} × {size[1]}, so its pixels do not line up with the fingerprint. Skipped.')
        continue
    results.append((path, fp.score(path, k)))
    verdict = 'likely the same phone' if results[-1][1] > fp.THRESHOLD else 'no clear match'
    print(f'{str(path):40} {results[-1][1]:9.1f}   {verdict}')

if args.figure and results:
    results.sort(key=lambda r: r[1])
    above = sum(s > fp.THRESHOLD for _, s in results)
    fig, ax = plt.subplots(figsize=(8, 1.6 + 0.26 * len(results)))
    fig.subplots_adjust(top=1 - 1.25 / fig.get_figheight(), bottom=0.6 / fig.get_figheight(), left=0.2, right=0.97)
    title(fig, f'{above} of {len(results)} photos score above {fp.THRESHOLD}',
          f'Scores (PCE) of new photos against the fingerprint of {len(refs)} photos in {args.folder}/.\n'
          'Above the dashed line, a photo most likely comes from the same phone.')
    names = [f'{p.parent.name}/{p.name}' for p, _ in results]
    values = [s for _, s in results]
    ax.barh(names, values, color=[ACCENT if s > fp.THRESHOLD else LIGHT for s in values], height=0.7)
    ax.axvline(fp.THRESHOLD, color=GREY, ls='--', lw=1)
    ax.set_xscale('symlog', linthresh=10)
    ax.set(xlim=(min(-4, 2 * min(values)), max(1000, 2 * max(values))), xticks=[0, 10, 100, 1000], xticklabels=['0', '10', '100', '1,000'],
           xlabel='Score (PCE)')
    ax.tick_params(axis='y', labelsize=8, length=0)
    ax.grid(axis='x')
    ax.minorticks_off()
    save(fig, args.figure)
