# 0001. A small public re-implementation, separate from the lab repo

Status: accepted, 2026-10-27.

The post [Which iPhone took this photo?](https://vhamolya.com/blog/which-iphone-took-this-photo/) comes from a
private lab repo. That repo holds 400K+ Flickr photos, overnight runs, private photo-library results and paths on one
machine. The blog has its own figure scripts. Each one repeats the denoiser and writes files for the site.

We will build a new public repo, `vhamolya/iphone-fingerprint`. It writes the method again in one small module and a
few experiment scripts (ADR 0003). It takes no code history and no data from the lab repo. The lab repo and the blog
scripts stay private and do not change.

The repo is for trying the method. It does not check every number in the post. It reproduces the parts of the post
that run on simulated phones and on public photos (ADR 0004). The 28-model results come from Flickr photos that we
cannot share, so they stay numbers in the post. The README says so in its limits.

## Considered options

- **Open the lab repo.** Rejected: it holds private data paths, private results and many dead ends. Cleaning it costs
  more than writing the method again.
- **Publish the blog's figure scripts.** Rejected: each script writes site data and repeats the same denoiser.
