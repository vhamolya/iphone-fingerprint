# 0003. One module and plain scripts, not notebooks

Status: accepted, 2026-10-27.

The method lives in one file, `fingerprint.py`, of about 150 lines: the cleaned copy, the noise, the fingerprint,
the clean-up and the score. Each experiment is one numbered script in `experiments/`, under 100 lines, and tests one
claim of the post. It prints its numbers and saves its figure to `docs/img/`. A reader can read any script from top to
bottom in a few minutes.

Planned experiments, in the order of the post:

1. `01_simulated_phones.py`: two simulated phones. Noise lines up for one phone and not for two. No download.
2. `02_averaging.py`: the fingerprint appears as photos are added, and the noise left shrinks as 1/√N. No download.
3. `03_real_iphones.py`: the real iPhone 11 photos of ADR 0004. Scores for the same phone and for other phones,
   without and with the clean-up.
4. `04_your_photos.py`: build a fingerprint from a folder of your photos and score a new photo against it.

## Considered options

- **Jupyter notebooks.** Rejected: outputs bloat the git history, diffs are hard to review, and CI needs extra tools
  to run them.
- **marimo notebooks.** Rejected for now: they are plain Python and reactive, but they add one more tool to learn. A
  script can become one later.
- **A package on PyPI.** Rejected: the code is for reading and trying, not for import into other projects.
