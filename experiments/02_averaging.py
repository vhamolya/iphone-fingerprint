"""02. From noise to fingerprint: average the noise of many photos.

One simulated phone photographs 32 real scenes. The script averages their noise into a fingerprint, K̂, after 1, 2,
4 and up to 32 photos. The fixed part adds up, and the fresh part cancels. The fresh part left in K̂ shrinks as 1/√N,
so four times the photos halve it.

So that the eye can see the fingerprint form, this phone's pattern sits in a ring, as in the post. A real fingerprint
has no shape: it looks like plain static. The script also saves the animation at the top of the README: each photo,
its noise, and the fingerprint so far.

Run: uv run experiments/02_averaging.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import fingerprint as fp
from plots import (ACCENT, ACCENT_LINE, FONTS, GREY, IMG, INK, LIGHT, PAPER, PAPER_2, SCENES, WHITE, grey, inside,
                   plate, save)

H, W = 174, 232                  # the simulated sensor, and each panel of the animation
STEPS = [1, 2, 4, 8, 16, 32]
FRAMES = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32]

rng = np.random.default_rng(7)
phone = fp.SimulatedPhone(seed=8, shape=(H, W), strength=0.025, fresh=2.5)
y, x = np.mgrid[:H, :W]
phone.k *= np.clip(1 - np.abs(np.hypot(x - W / 2, y - H / 2) / H - 0.3) / 0.07, 0, 1) ** 0.6   # the ring
photos = [phone.photo(fp.scenes((H, W))[i]) for i in rng.permutation(32)]

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

fig, card = plate(2, 'Four times the photos halve the fresh noise',
                  'A simulated phone photographs real scenes. Each dot is the fresh noise left in its fingerprint '
                  'after N photos.\nThe dashed line falls as 1/√N.', SCENES, size=(8, 4.8))
m = inside(card, left=0.1, bottom=0.2, right=0.08, top=0.08)
ax = fig.add_axes([m['left'], m['bottom'], m['right'] - m['left'], m['top'] - m['bottom']])
guide = np.exp(np.mean(np.log(left * np.sqrt(n)))) / np.sqrt(n)   # 1/√N, fitted to the dots' level
ax.loglog(n, guide, '--', color=LIGHT, lw=1)
ax.loglog(n, left, 'o-', color=ACCENT, lw=2, ms=6)
ax.text(n[3], guide[3] * 1.2, '1/√N', color=GREY, ha='left', va='bottom')
ax.set(xticks=STEPS, xticklabels=STEPS, yticks=[0.003, 0.01, 0.03], yticklabels=['0.003', '0.01', '0.03'],
       xlabel='Photos in the fingerprint, N', ylabel='Fresh noise left in K̂')
ax.minorticks_off()
ax.grid(axis='y')
save(fig, '02_averaging.png')

# The animation, drawn as a figure plate: photo n, its noise, and the fingerprint of the first n photos.
inter = {w: str(FONTS / f'Inter-{w}.ttf') for w in ('Regular', 'SemiBold')}
title_font, subtitle_font = ImageFont.truetype(inter['SemiBold'], 17), ImageFont.truetype(inter['Regular'], 13)
label_font, source_font = ImageFont.truetype(inter['SemiBold'], 13), ImageFont.truetype(inter['Regular'], 11)
GAP, TOP = 12, 106                               # gap between panels, and the panels' top edge
WIDTH, HEIGHT = 3 * W + 4 * GAP + 40, TOP + H + 66
palette = Image.new('P', (1, 1))                 # 40 greys and the site's colours, shared by every frame
colours = [(v, v, v) for v in np.linspace(0, 255, 40).astype(int)] + [
    tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (ACCENT, ACCENT_LINE, PAPER, PAPER_2, INK, GREY)]
palette.putpalette([v for c in colours for v in c] + [0] * 3 * (256 - len(colours)))
frames = []
for n in FRAMES:
    photo = photos[n - 1]
    panels = [(f'Photo {n}', photo / 255), ('Its noise', grey(fp.noise(photo))),
              (f'Fingerprint of {n} photo' + 's' * (n > 1), grey(fp.fingerprint(photos[:n])))]
    frame = Image.new('RGB', (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((8, 8, WIDTH - 9, HEIGHT - 33), 14, fill=PAPER_2)
    draw.text((WIDTH // 2, 36), 'The fingerprint appears as photos are added', fill=INK, font=title_font,
              anchor='ms')
    draw.text((WIDTH // 2, 58), 'A simulated phone photographs real scenes. Its pattern sits in a ring, so you '
              'can see it.', fill=GREY, font=subtitle_font, anchor='ms')
    draw.rounded_rectangle((20, 72, WIDTH - 21, HEIGHT - 45), 7, fill=WHITE)
    for i, (text, image) in enumerate(panels):
        x0 = 20 + GAP + i * (W + GAP)
        frame.paste(Image.fromarray((image * 255).astype(np.uint8)).convert('RGB'), (x0, TOP))
        draw.text((x0, TOP - 9), text, fill=INK, font=label_font, anchor='ls')
    bar = (20 + GAP, TOP + H + 10, WIDTH - 21 - GAP, TOP + H + 13)          # how many of the 32 photos are in
    draw.rectangle(bar, fill=ACCENT_LINE)
    draw.rectangle((bar[0], bar[1], bar[0] + (bar[2] - bar[0]) * n // 32, bar[3]), fill=ACCENT)
    draw.text((12, HEIGHT - 12), 'ANIMATION', fill=GREY, font=source_font, anchor='ls')
    draw.text((92, HEIGHT - 12), SCENES.split('. List')[0], fill=GREY, font=source_font, anchor='ls')
    frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
gif = IMG / '02_averaging.gif'
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=[700] * (len(frames) - 1) + [2500], loop=0)
print(f'saved docs/img/{gif.name} ({WIDTH} × {HEIGHT}, {gif.stat().st_size / 1e6:.1f} MB)')
