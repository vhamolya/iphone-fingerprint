"""02. From noise to fingerprint: average the noise of many photos.

One simulated phone takes 64 photos of new scenes. The script averages their noise into a fingerprint, K̂, after 1, 2,
4 and up to 64 photos. The fixed part adds up, and the fresh part cancels. The fresh part left in K̂ shrinks as 1/√N,
so four times the photos halve it.

So that the eye can see the fingerprint form, this phone's pattern sits in a ring, as in the post. A real fingerprint
has no shape: it looks like plain static. The script also saves the animation at the top of the README: each photo,
its noise, and the fingerprint so far.

Run: uv run experiments/02_averaging.py
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

import fingerprint as fp
from plots import ACCENT, GREY, IMG, LIGHT, grey, save, title

SIZE, GAP, TOP = 240, 16, 40     # the animation: panel side, gap and label height, in pixels
STEPS = [1, 2, 4, 8, 16, 32, 64]
FRAMES = [1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 64]

rng = np.random.default_rng(7)
phone = fp.SimulatedPhone(seed=8, size=SIZE, strength=0.012, fresh=2.5)
y, x = np.mgrid[:SIZE, :SIZE] / SIZE
phone.k *= np.clip(1 - np.abs(np.hypot(x - 0.5, y - 0.5) - 0.3) / 0.07, 0, 1) ** 0.6   # the ring
photos = [phone.photo(fp.scene(rng, SIZE)) for _ in range(STEPS[-1])]

print(' photos   match with K   fresh part left')
rows = []
for n in STEPS:
    k = fp.fingerprint(photos[:n])
    share = (k * phone.k).sum() / (phone.k ** 2).sum()   # how much of K the fingerprint holds
    fresh = k - share * phone.k
    # A robust spread: with one photo, K̂ = W / I, and a few dark pixels would swamp the standard deviation.
    rows.append((n, fp.correlation(k, phone.k), 1.4826 * np.median(np.abs(fresh - np.median(fresh)))))
    print(f'{n:7d}   {rows[-1][1]:11.2f}   {rows[-1][2]:15.5f}')
n, _, left = np.array(rows).T
slope = np.polyfit(np.log(n), np.log(left), 1)[0]
print(f'The fresh part shrinks as N^{slope:.2f}. Pure averaging gives N^-0.50.')

fig, ax = plt.subplots(figsize=(8, 4.6))
fig.subplots_adjust(top=0.78, bottom=0.13, left=0.1, right=0.96)
title(fig, 'Four times the photos halve the fresh noise',
      'A simulated phone. Each dot is the fresh noise left in the fingerprint after N photos.\n'
      'The dashed line falls as 1/√N.')
guide = np.exp(np.mean(np.log(left * np.sqrt(n)))) / np.sqrt(n)   # 1/√N, fitted to the dots' level
ax.loglog(n, guide, '--', color=LIGHT, lw=1.2)
ax.loglog(n, left, 'o-', color=ACCENT, lw=2, ms=6)
ax.text(n[-1], guide[-1], '  1/√N', color=GREY, va='center')
ax.set(xticks=STEPS, xticklabels=STEPS, yticks=[0.003, 0.01, 0.03], yticklabels=['0.003', '0.01', '0.03'],
       xlabel='Photos in the fingerprint, N', ylabel='Fresh noise left in K̂')
ax.minorticks_off()
ax.grid(axis='y')
save(fig, '02_averaging.png')

# The animation: photo n, its noise, and the fingerprint of the first n photos.
font = ImageFont.truetype(font_manager.findfont('DejaVu Sans'), 15)
frames = []
for n in FRAMES:
    photo = photos[n - 1]
    panels = [(f'Photo {n}', photo / 255), ('Its noise', grey(fp.noise(photo))),
              (f'Fingerprint of {n} photo' + 's' * (n > 1), grey(fp.fingerprint(photos[:n])))]
    frame = Image.new('L', (3 * SIZE + 4 * GAP, TOP + SIZE + GAP), 248)
    draw = ImageDraw.Draw(frame)
    for i, (label, image) in enumerate(panels):
        left = GAP + i * (SIZE + GAP)
        frame.paste(Image.fromarray((np.round(image * 31) * 255 / 31).astype(np.uint8)), (left, TOP))
        draw.text((left, TOP - 8), label, fill=24, font=font, anchor='ls')
    frames.append(frame)
gif = IMG / '02_averaging.gif'
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=[700] * (len(frames) - 1) + [2500], loop=0)
print(f'saved docs/img/{gif.name} ({gif.stat().st_size / 1e6:.1f} MB)')
