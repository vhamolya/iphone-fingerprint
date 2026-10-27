# 0008. Simulated phones photograph real scenes, committed as small grey copies

Status: accepted, 2026-10-27.

The first simulated phones photographed scenes made up in code: soft blobs and boxes. They looked nothing like photos,
and the post's own simulations use real Commons scenes. The reader asked for real photos where the licence allows.

The simulated phones now photograph 32 Commons photos by -wuppertaler, all CC BY 4.0, listed in `data/scenes.tsv`.
They are the photos of the post's averaging figure that experiment 03 does not use. `experiments/make_scenes.py` takes
Commons' own 960-pixel copy of each, crops it to 4:3 around its centre and shrinks it to 480 × 360. It converts the
copy to grey and removes what grain is left with the cleaned copy of `fingerprint.py`. The resize already destroys the
original phone's fingerprint. The 32 files take 1.7 MB, and git keeps them in `data/scenes/` with their credits. So
experiments 01 and 02, the tests and CI still need no download (ADR 0004). The figures and the animation show whole
photos, not crops, so a reader sees real scenes.

This amends ADR 0004, which commits only the list of titles. The 60 originals of experiment 03 stay out of the repo.
A scene is an adaptation, so the script accepts only CC BY 4.0 and CC0: no share-alike terms. None of the scenes is
among those 60 photos.

Real scenes have edges, and an edge leaks into the noise of every phone that photographs it. So experiment 01 compares
only pixels that are plain in both scenes, as the post's hypothesis figure does. The tests build fingerprints and test
photos from different scenes: a new photo of a scene in the fingerprint matches through its edges, whatever the phone.

## Considered options

- **Keep made-up scenes.** Rejected: the README's first figures looked synthetic, and they hid the edge leak that the
  method must handle.
- **Download the scenes on demand.** Rejected: experiments 01 and 02 and CI must run with no network.
- **Crops of the 60 originals.** Rejected: a crop at full size keeps that phone's fingerprint, and experiment 03 scores
  those very photos.
