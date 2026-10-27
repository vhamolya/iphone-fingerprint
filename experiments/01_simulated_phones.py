"""01. The noise follows the phone.

Two simulated phones photograph real scenes. Phone A takes two different scenes, and phone B takes the first scene
too. The script takes the noise out of each photo and compares the photos pixel by pixel, with Pearson's r. Phone A's
two photos line up, though their scenes differ. Phone A and phone B do not, even on the same scene.

As in the post, it compares only pixels that are plain in both scenes. At edges the scene leaks into the noise, and
two photos of one scene would line up there whatever the phone.

A simulation: each phone's K is 3% of the light, far stronger than in a real phone. Two real photos from one iPhone 11
give r = 0.0004 (experiment 03), so one photo is not enough. Experiment 02 shows how many photos make up for it.

Run: uv run experiments/01_simulated_phones.py
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import uniform_filter

import fingerprint as fp
from plots import ACCENT, GREY, LIGHT, SCENES, save, source, title

rng = np.random.default_rng(25)
scenes = [fp.scene(rng), fp.scene(rng)]
a = fp.SimulatedPhone(seed=2, strength=0.03, fresh=1.5)
b = fp.SimulatedPhone(seed=3, strength=0.03, fresh=1.5)
photos = {'Phone A, scene 1': a.photo(scenes[0]), 'Phone A, scene 2': a.photo(scenes[1]),
          'Phone B, scene 1': b.photo(scenes[0])}
noise = {name: fp.noise(photo) for name, photo in photos.items()}


def plain(s: np.ndarray) -> np.ndarray:
    """Pixels with no edge nearby: the spread of a 7 × 7 window is under 2 grey levels, and nothing is clipped."""
    spread = uniform_filter(s * s, 7) - uniform_filter(s, 7) ** 2
    return (spread < 4) & (s > 20) & (s < 240)


mask = plain(scenes[0]) & plain(scenes[1])
noise = {name: w[mask] for name, w in noise.items()}
print(f'{mask.mean():.0%} of the pixels are plain in both scenes.')

pairs = [('Phone A, scene 1', 'Phone A, scene 2'), ('Phone A, scene 1', 'Phone B, scene 1')]
r = {pair: fp.correlation(noise[pair[0]], noise[pair[1]]) for pair in pairs}
for (p, q), value in r.items():
    print(f'{p} against {q}: r = {value:.2f}')

fig = plt.figure(figsize=(8, 6.6))
title(fig, 'The noise follows the phone, not the scene',
      'Simulated phones on real scenes. Each dot is one plain pixel in the noise of two photos.\n'
      'The pattern is 3% of the light, far stronger than in a real phone.')
grid = fig.add_gridspec(2, 6, top=0.82, bottom=0.1, left=0.08, right=0.97, hspace=0.25, wspace=0.9)
for i, (name, photo) in enumerate(photos.items()):
    ax = fig.add_subplot(grid[0, 2 * i:2 * i + 2])
    ax.imshow(photo, cmap='gray', vmin=0, vmax=255)
    ax.set_title(name)
    ax.set_axis_off()

pick = rng.choice(noise['Phone A, scene 1'].size, 2500, replace=False)
for i, (p, q) in enumerate(pairs):
    ax = fig.add_subplot(grid[1, 3 * i:3 * i + 3])
    x, y = (noise[n][pick] / noise[n].std() for n in (p, q))
    same = p[:7] == q[:7]
    ax.scatter(x, y, s=3, color=ACCENT if same else LIGHT, alpha=0.5, linewidths=0)
    ax.set(xlim=(-4, 4), ylim=(-4, 4), aspect='equal', xticks=[-4, 0, 4], yticks=[-4, 0, 4])
    ax.set_xlabel(f'Noise: {p}', fontsize=9)
    ax.set_ylabel(f'Noise: {q}', fontsize=9)
    ax.set_title(('One phone' if same else 'Two phones') + f':  r = {r[(p, q)]:.2f}',
                 color=ACCENT if same else GREY)
source(fig, SCENES)
save(fig, '01_simulated_phones.png')
