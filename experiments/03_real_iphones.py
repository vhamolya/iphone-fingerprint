"""03. Real iPhone 11s: the same phone, other phones, and the clean-up.

The photos are 60 full-size originals from Wikimedia Commons, listed in data/photos.tsv:
  fingerprint  40 photos that make the fingerprint of one iPhone 11;
  same         10 more photos from that phone;
  other        10 photos from 10 other iPhone 11s.

The script scores each test photo against the fingerprint twice. Without the clean-up, every iPhone 11 matches,
because every phone of the model carries the shared pattern. With the clean-up, only the same phone matches.

It also compares single photos pixel by pixel, as Part 1 of the post does. One photo holds very little of the pattern.

First download the photos (199 MB): uv run experiments/fetch_photos.py
Run: uv run experiments/03_real_iphones.py   (a few minutes)
"""
import shutil
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import fingerprint as fp
from plots import ACCENT, GREY, IMG, INK, LIGHT, save, title

DATA = Path(__file__).resolve().parent.parent / 'data'
photos = {group: sorted((DATA / group).glob('*.jpg')) for group in ('fingerprint', 'same', 'other')}
if [len(p) for p in photos.values()] != [40, 10, 10]:
    sys.exit('The photos are missing. Download them first (199 MB): uv run experiments/fetch_photos.py')

start = time.time()
k = fp.fingerprint(photos['fingerprint'])
k_clean = fp.clean_up(k)
print(f'The fingerprint of 40 photos took {time.time() - start:.0f} s.\n')

print('photo            without clean-up   with clean-up')
scores = {(group, clean): [] for group in ('same', 'other') for clean in (False, True)}
same_noise, r = [], {'same': [], 'other': []}
for group in ('same', 'other'):
    for path in photos[group]:
        photo = fp.load(path)
        w = fp.noise(photo)
        w_clean = fp.zero_mean(w)
        scores[group, False].append(fp.pce(w, photo * k))
        scores[group, True].append(fp.pce(w_clean, photo * k_clean))
        print(f'{group:>5}/{path.name}   {scores[group, False][-1]:16.1f}   {scores[group, True][-1]:13.1f}')
        # Single photos against each other: every pair from the same phone, and each other phone against them.
        r[group] += [fp.correlation(w_clean, v) for v in same_noise]
        if group == 'same':
            same_noise.append(w_clean)

for clean in (False, True):
    same, other = np.array(scores['same', clean]), np.array(scores['other', clean])
    print(f'\n{"With" if clean else "Without"} the clean-up: same phone {same.min():.1f} to {same.max():.1f} '
          f'(median {np.median(same):.1f}), other phones {other.min():.1f} to {other.max():.1f}. '
          f'Above {fp.THRESHOLD}: {(same > fp.THRESHOLD).sum()} of 10 and {(other > fp.THRESHOLD).sum()} of 10.')
print(f'\nSingle photos, pixel by pixel: median r = {np.median(r["same"]):.4f} for one phone '
      f'({len(r["same"])} pairs) and {np.median(r["other"]):.4f} for two phones ({len(r["other"])} pairs).')
print('The post reports 0.0004 and 0.0001.')

fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), sharey=True)
fig.subplots_adjust(top=0.72, bottom=0.2, left=0.13, right=0.97, wspace=0.12)
title(fig, 'After the clean-up, other iPhone 11s stop matching',
      'Scores (PCE) of 20 real photos against the fingerprint of one iPhone 11. Without the clean-up, the pattern\n'
      'that every iPhone 11 shares makes every phone match. The dashed line is the usual threshold, 60.')
for ax, clean in zip(axes, (False, True)):
    for row, (group, colour) in enumerate((('other', LIGHT), ('same', ACCENT))):
        values = np.array(scores[group, clean])
        jitter = np.random.default_rng(row).uniform(-0.12, 0.12, values.size)
        ax.scatter(values, row + jitter, s=36, color=colour, alpha=0.85, linewidths=0, zorder=3)
        median = np.median(values)
        ax.plot([median, median], [row - 0.25, row + 0.25], color=INK, lw=2, zorder=4)
        ax.text(median, row + 0.3, f'{median:,.0f}', ha='center', fontsize=9, color=INK)
    ax.axvline(fp.THRESHOLD, color=LIGHT, ls='--', lw=1)
    ax.set_xscale('symlog', linthresh=10)
    ax.set(xlim=(-4, 30000), ylim=(-0.6, 1.7), xticks=[0, 10, 100, 1000, 10000],
           xticklabels=['0', '10', '100', '1,000', '10,000'], xlabel='Score (PCE)')
    ax.set_title('With the clean-up' if clean else 'Without the clean-up', color=INK if clean else GREY)
    ax.grid(axis='x')
    ax.minorticks_off()
axes[0].set(yticks=[0, 1], yticklabels=['10 other\niPhone 11s', 'The same\niPhone 11'])
fig.text(0.02, 0.03, 'Photos: Wikimedia Commons, 50 by -wuppertaler and 10 by other photographers, under CC BY 4.0 and '
         'other licences. List: docs/img/CREDITS.md', fontsize=8, color=GREY)
save(fig, '03_real_iphones.png')
shutil.copy(DATA / 'CREDITS.md', IMG / 'CREDITS.md')
