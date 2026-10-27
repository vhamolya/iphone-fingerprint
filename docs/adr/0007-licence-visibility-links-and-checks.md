# 0007. MIT code, private until reviewed, linked both ways

Status: accepted, 2026-10-27.

- **Licence.** The code is MIT. A figure made from a Commons photo keeps that photo's licence (such as CC BY 4.0) and
  its credit. Downloaded photos are not part of the repo.
- **Visibility.** The repo starts private under the author's GitHub account. Only the author makes it public, after
  reading the README and running every experiment from a fresh clone.
- **Links.** The README's first lines link to the post. When the repo is public, `companionRepo` in the blog's
  `src/data/site.ts` gets its URL, and the post shows the link (the blog's ADR 0001).
- **Checks.** GitHub Actions runs on every push, on Linux and macOS, with uv: the tests, then each experiment that
  needs no download. CI does not download from Commons. The author runs the real-photo experiment by hand before each
  release.

## Considered options

- **Apache 2.0.** Rejected: it adds a patent clause and a NOTICE file that a small teaching repo does not need.
- **CC BY for the code.** Rejected: Creative Commons advises against its licences for software.
