# 0006. The defaults are the post's method; a change goes in a new experiment

Status: accepted, 2026-10-27.

The repo shows how the post got its results, so its defaults match the post's "The method in formulas" block:

- cleaned copy: Daubechies db4 wavelets over 4 levels, σ = 5 on the 0 to 255 scale, windows of 3, 5, 7 and 9 pixels;
- fingerprint: K̂ = Σ WᵢIᵢ / Σ Iᵢ²;
- score: PCE, with an 11 × 11 window around the peak left out;
- clean-up: zero-mean each 2 × 2 sub-grid by rows and by columns, then flatten sharp peaks in the fingerprint's
  spectrum.

These values sit in one place at the top of `fingerprint.py`, with the names the post uses. On the Commons photos, the
real-photo experiment must give the post's numbers to the precision the post shows.

A better denoiser or score is welcome as a new experiment that compares itself with the defaults. It does not replace
them. If the post changes its method, the repo changes too, and the commit names the change in the post.
