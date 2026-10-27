"""Download the 60 iPhone 11 photos of experiment 03 from Wikimedia Commons into data/.

The list is data/photos.tsv. Each photo is a full-size 4032 × 3024 original, because a resized copy loses the
fingerprint. The script reads each photo's author and licence from the Commons API, checks the file's SHA-1 and
writes the credits to data/CREDITS.md. Photos already in data/ are not downloaded again.

Run: uv run experiments/fetch_photos.py
"""
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
API = 'https://commons.wikimedia.org/w/api.php'
# Wikimedia asks every script to name itself and give a contact.
AGENT = {'User-Agent': 'iphone-fingerprint/0.1 (https://vhamolya.com/blog/which-iphone-took-this-photo/)'}


def photos():
    """(number, group, title) for each photo in data/photos.tsv. The file names are the numbers: 01.jpg to 60.jpg."""
    rows = [line.split('\t') for line in (DATA / 'photos.tsv').read_text().splitlines()[1:] if line]
    return [(i, group, title) for i, (group, title) in enumerate(rows, 1)]


def path(i: int, group: str) -> Path:
    return DATA / group / f'{i:02d}.jpg'


def get(url: str) -> bytes:
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=60) as r:
                return r.read()
        except OSError:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def info(title: str) -> dict:
    query = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'titles': title,
                                    'iiprop': 'url|size|sha1|extmetadata'})
    page = next(iter(json.loads(get(f'{API}?{query}'))['query']['pages'].values()))
    return page['imageinfo'][0]


def text(meta: dict, key: str) -> str:
    """One field of the API's extmetadata, without its HTML."""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', meta.get(key, {}).get('value', ''))).strip()


def main() -> None:
    credits = ['# Credits', '', 'The 60 iPhone 11 photos of experiment 03 come from Wikimedia Commons. Each keeps its '
               'own licence. `uv run experiments/fetch_photos.py` downloads them into `data/`.', '',
               '| File | Group | Photo | Author | Licence |', '|---|---|---|---|---|']
    total = 0
    for i, group, title in photos():
        meta = info(title)
        licence = text(meta['extmetadata'], 'LicenseShortName')
        assert licence.startswith(('CC', 'Public domain')), f'{title}: unexpected licence {licence!r}'
        author = text(meta['extmetadata'], 'Artist') or 'unknown'
        name = title.removeprefix('File:')
        credits.append(f'| {group}/{i:02d}.jpg | {group} | [{name}]({meta["descriptionurl"]}) | {author} | {licence} |')
        total += meta['size']
        target = path(i, group)
        if target.exists() and hashlib.sha1(target.read_bytes()).hexdigest() == meta['sha1']:
            continue
        print(f'{i:2d}/60  {meta["size"] / 1e6:4.1f} MB  {name}', flush=True)
        body = get(meta['url'])
        assert hashlib.sha1(body).hexdigest() == meta['sha1'], f'{title}: the download is damaged'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        time.sleep(0.5)   # be gentle with the servers
    (DATA / 'CREDITS.md').write_text('\n'.join(credits) + '\n')
    print(f'60 photos, {total / 1e6:.0f} MB, in {DATA}. Credits: {DATA / "CREDITS.md"}')


if __name__ == '__main__':
    main()
