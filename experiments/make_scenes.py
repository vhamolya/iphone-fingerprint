"""Make the real scenes that the simulated phones photograph, in data/scenes/.

The scenes are the 32 Commons photos of the post's averaging figure that experiment 03 does not use. They are listed
in data/scenes.tsv. The script takes Commons' own 960-pixel copy of each one, so the original phone's fingerprint is
gone with the resize. It crops the copy to 4:3 around its centre, shrinks it to 480 × 360, converts it to grey and
removes what grain is left with the cleaned copy of fingerprint.py. It writes the credits to data/scenes/CREDITS.md.

The scenes are committed, so the simulated experiments need no download. Readers never need to run this script.

Run: uv run experiments/make_scenes.py
"""
import io
import json
import urllib.parse

import numpy as np
from PIL import Image

import fingerprint as fp
from fetch_photos import API, DATA, get, text

WIDTH = 960          # one of the thumbnail widths that Wikimedia serves
SIZE = (480, 360)    # every scene: width and height in pixels


def main() -> None:
    titles = (DATA / 'scenes.tsv').read_text().splitlines()[1:]
    folder = DATA / 'scenes'
    folder.mkdir(exist_ok=True)
    for old in folder.glob('*.jpg'):
        old.unlink()
    credits = ['# Scene credits', '', 'The simulated phones photograph these scenes. Each one is a Commons photo, '
               f'resized by Wikimedia to {WIDTH} pixels wide, cropped to 4:3, shrunk to {SIZE[0]} × {SIZE[1]}, '
               'converted to grey and cleaned of its grain by `experiments/make_scenes.py`. Each keeps its own '
               'licence.', '',
               '| File | Photo | Author | Licence |', '|---|---|---|---|']
    for i, title in enumerate(titles, 1):
        query = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'titles': title,
                                        'iiprop': 'url|extmetadata', 'iiurlwidth': WIDTH})
        info = next(iter(json.loads(get(f'{API}?{query}'))['query']['pages'].values()))['imageinfo'][0]
        licence = text(info['extmetadata'], 'LicenseShortName')
        # A scene is an adaptation, so its licence must allow that without share-alike terms.
        assert licence in ('CC BY 4.0', 'CC0'), f'{title}: {licence!r} does not allow a plain adaptation'
        copy = Image.open(io.BytesIO(get(info['thumburl']))).convert('L')
        w, h = copy.size
        cw, ch = min(w, h * 4 // 3), min(h, w * 3 // 4)
        copy = copy.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)).resize(SIZE, Image.LANCZOS)
        grey = np.asarray(copy, np.float32)
        scene = np.clip(np.rint(fp.cleaned_copy(grey)), 0, 255).astype(np.uint8)
        Image.fromarray(scene).save(folder / f'{i:02d}.jpg', quality=92)
        name = title.removeprefix('File:')
        credits.append(f'| {i:02d}.jpg | [{name}]({info["descriptionurl"]}) | '
                       f'{text(info["extmetadata"], "Artist")} | {licence} |')
        print(f'{i:02d}.jpg  {scene.shape[1]} × {scene.shape[0]}  {name}')
    (folder / 'CREDITS.md').write_text('\n'.join(credits) + '\n')


if __name__ == '__main__':
    main()
