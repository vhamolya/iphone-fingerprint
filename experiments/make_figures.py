"""Rebuild every figure and animation of the README, in docs/img/.

Experiments 01 and 02 need no download. Experiments 03 and 04 need the Commons photos (199 MB):
uv run experiments/fetch_photos.py. Without them, this script rebuilds the rest and names what it skipped.

Run: uv run experiments/make_figures.py   (about 2 minutes with the photos)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = [
    (False, ['01_simulated_phones.py']),
    (False, ['02_averaging.py']),
    (True, ['03_real_iphones.py']),
    (True, ['04_your_photos.py', 'data/fingerprint', 'data/same', 'data/other', '--figure', 'docs/img/04_your_photos.png']),
]

have_photos = [len(list((ROOT / 'data' / g).glob('*.jpg'))) for g in ('fingerprint', 'same', 'other')] == [40, 10, 10]
skipped = []
for needs_photos, (script, *args) in RUNS:
    if needs_photos and not have_photos:
        skipped.append(script)
        continue
    print(f'\n== {script}', flush=True)
    subprocess.run([sys.executable, ROOT / 'experiments' / script, *args], cwd=ROOT, check=True)

if skipped:
    sys.exit(f'\nSkipped {", ".join(skipped)}: the photos are missing. Run uv run experiments/fetch_photos.py first.')
