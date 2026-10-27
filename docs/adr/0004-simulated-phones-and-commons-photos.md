# 0004. Simulated phones by default, real photos from Wikimedia Commons on demand

Status: accepted, 2026-10-27.

Every experiment except the real-photo one runs with no download. They use simulated phones: a real scene times
(1 + K), plus fresh noise. As in the post, each one is labelled as a simulation and says what it exaggerates.

The real-photo experiment uses the same 60 Wikimedia Commons photos as the post's "Shared or unique" figure:

- 40 photos make the fingerprint of one iPhone 11;
- 10 more photos come from that phone;
- 10 photos come from 10 other iPhone 11s.

They are full-size 4032 × 3024 originals, because a resized copy loses the pattern. The repo commits only the list of
file titles. A fetch command downloads the originals from the Commons API into `data/`, which git ignores. It reads
each photo's author and licence from the API and writes them to `data/CREDITS.md`. The README gives the download size.

A reader can also point an experiment at a folder of their own photos. The code reads them on the reader's computer
and sends them nowhere.

These never go into the repo, its figures or its tests:

- the author's own photos and RAW wall frames, because full-size frames would publish the fingerprint of the author's
  phone;
- photos from other phones in the author's household;
- Flickr photos, and research-only sets such as LAION-Mobile, FODB and SCMI30;
- GPS or other metadata.

## Considered options

- **Commit the photos.** Rejected: 60 large files stay in the history forever, with a licence to track for each.
- **Git LFS.** Rejected: it has bandwidth quotas, and the reader must install it.
- **VISION or Dresden.** Rejected for now: they hold few recent iPhones, under research terms, and the post does not
  use them.
- **The author's wall frames.** Rejected, for the privacy reason above.
