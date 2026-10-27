"""Make the real scenes that the simulated phones photograph, in data/scenes/.

The scenes are 8 photos from Wikimedia Commons, listed in data/scenes.tsv. The script takes Commons' own 960-pixel
copy of each one, so the original phone's fingerprint is gone with the resize. It converts the copy to grey, removes
what grain is left with the cleaned copy of fingerprint.py, and writes the credits to data/scenes/CREDITS.md.

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

WIDTH = 960   # one of the thumbnail widths that Wikimedia serves


def main() -> None:
    titles = (DATA / 'scenes.tsv').read_text().splitlines()[1:]
    folder = DATA / 'scenes'
    folder.mkdir(exist_ok=True)
    credits = ['# Scene credits', '', 'The simulated phones photograph these scenes. Each one is a Commons photo, '
               f'resized by Wikimedia to {WIDTH} pixels wide, converted to grey and cleaned of its grain by '
               '`experiments/make_scenes.py`. Each keeps its own licence.', '',
               '| File | Photo | Author | Licence |', '|---|---|---|---|']
    for i, title in enumerate(titles, 1):
        query = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'titles': title,
                                        'iiprop': 'url|extmetadata', 'iiurlwidth': WIDTH})
        info = next(iter(json.loads(get(f'{API}?{query}'))['query']['pages'].values()))['imageinfo'][0]
        licence = text(info['extmetadata'], 'LicenseShortName')
        # A scene is an adaptation, so its licence must allow that without share-alike terms.
        assert licence in ('CC BY 4.0', 'CC0'), f'{title}: {licence!r} does not allow a plain adaptation'
        grey = np.asarray(Image.open(io.BytesIO(get(info['thumburl']))).convert('L'), np.float32)
        scene = np.clip(np.rint(fp.cleaned_copy(grey)), 0, 255).astype(np.uint8)
        Image.fromarray(scene).save(folder / f'{i:02d}.jpg', quality=92)
        name = title.removeprefix('File:')
        credits.append(f'| {i:02d}.jpg | [{name}]({info["descriptionurl"]}) | '
                       f'{text(info["extmetadata"], "Artist")} | {licence} |')
        print(f'{i:02d}.jpg  {scene.shape[1]} × {scene.shape[0]}  {name}')
    (folder / 'CREDITS.md').write_text('\n'.join(credits) + '\n')


if __name__ == '__main__':
    main()
