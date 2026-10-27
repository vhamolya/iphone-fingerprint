# 0002. Python with uv and one lock file

Status: accepted, 2026-10-27.

A reader must run any experiment with one command, on macOS, Linux or Windows, without making an environment first.

The repo is a [uv](https://docs.astral.sh/uv/) project. `pyproject.toml` and `uv.lock` are committed.
`uv run experiments/01_simulated_phones.py` makes the environment, installs the locked versions and runs the script.
The first run takes seconds.

The dependencies stay few: NumPy, SciPy, PyWavelets, Pillow and Matplotlib. The tests use pytest, in a dev group.
Python 3.11 or newer.

## Considered options

- **pip and requirements.txt.** Rejected: the reader makes a venv first, and nothing pins the versions below the top
  level.
- **A PEP 723 header in each script.** Rejected: every script repeats the dependency list, and each script gets its
  own lock.
- **conda.** Rejected: a large install for five packages that pip has.
- **PyTorch, for the DRUNet denoiser.** Left out. The post says DRUNet gave the same results as the wavelet filter,
  and PyTorch is a download of gigabytes.
