# 0005. The README shows figures and animations that the code makes

Status: accepted, 2026-10-27.

Most readers see only the README, so it shows the result before the instructions. Every image and animation in it
comes from an experiment script, from simulated phones or Commons photos, and is saved in `docs/img/`.
`uv run experiments/make_figures.py` rebuilds all of them. A figure that the code cannot rebuild does not go in.

- Still figures are PNG. Animations are short looping GIFs made with Pillow, at most 800 px wide and 3 MB each. The
  first one shows the fingerprint appear as photos are added.
- The pipeline (photo, cleaned copy, noise, fingerprint, score) is a Mermaid diagram. GitHub draws it from text, so it
  needs no image file.
- Formulas use GitHub's math syntax and match the post's "The method in formulas" block.
- Figures made from Commons photos carry those photos' credit and licence.

The README has this order:

1. One figure and two sentences on what the repo shows, with a link to the post.
2. Quick start: install uv, clone, run the first experiment.
3. The experiments, one figure each.
4. The method in brief, with the formulas.
5. Your own photos.
6. Limits: what the repo does not reproduce (ADR 0001).
7. Credits, licence and how to cite the post.

## Considered options

- **Screenshots of the post.** Rejected: they go out of date, and the reader cannot rebuild them.
- **Video.** Rejected: GitHub plays a video in a README only after an upload through its web editor, so the code
  cannot rebuild it.
