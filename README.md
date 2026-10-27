# Which iPhone took this photo?

> **This is the code of my post
> [Every iPhone has a fingerprint. Can one photo give you away? ↗](https://vhamolya.com/blog/which-iphone-took-this-photo/)**
> The post explains each step with interactive figures. Here you run the same steps yourself, on simulated phones,
> on real iPhone 11 photos, and on your own photos.

![A simulated phone photographs 32 real scenes. Its noise looks like static, but the average of the noise forms a ring after about ten photos.](docs/img/02_averaging.gif)

## In one minute

| 01 · Hypothesis | 02 · Method | 03 · Result |
|---|---|---|
| No two camera sensors are made alike. Some pixels catch a little more light than others, in every photo. That fixed pattern is a fingerprint of the phone. | Subtract a cleaned copy from each photo to get its noise. Average the noise of many photos from one phone. Score a new photo against that average. | On 20 real iPhone 11 photos, 9 of the 10 from the same phone score above every photo from 10 other iPhone 11s. A clean-up step makes the difference. |

## Quick start

1. Install [uv ↗](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone the repo and run the first experiment. It needs no download.

   ```bash
   git clone https://github.com/vhamolya/iphone-fingerprint
   cd iphone-fingerprint
   uv run experiments/01_simulated_phones.py
   ```

3. For real photos, download the 60 iPhone 11 photos (199 MB) and run experiment 3:

   ```bash
   uv run experiments/fetch_photos.py
   uv run experiments/03_real_iphones.py
   ```

The first `uv run` makes an environment with the locked versions of NumPy, SciPy, PyWavelets, Pillow and Matplotlib.
It needs Python 3.11 or newer, and uv downloads one if you have none. Each script prints its numbers and saves its
figure to `docs/img/`.

| Script | What it shows | Download |
|---|---|---|
| [`01_simulated_phones.py`](experiments/01_simulated_phones.py) | The noise follows the phone, not the scene | none |
| [`02_averaging.py`](experiments/02_averaging.py) | Averaging N photos leaves 1/√N of the fresh noise | none |
| [`03_real_iphones.py`](experiments/03_real_iphones.py) | Real iPhone 11s: the same phone, other phones, and the clean-up | 199 MB |
| [`04_your_photos.py`](experiments/04_your_photos.py) | A fingerprint from your own photos, and scores for new ones | your photos |
| [`make_figures.py`](experiments/make_figures.py) | Rebuilds every figure and animation on this page | 199 MB |

<sub>PART 1 · THE IDEA</sub>

## The noise follows the phone

![Two scatter plots of noise values. Two photos from one phone line up with r = 0.79. Photos from two phones do not, r = 0.01.](docs/img/01_simulated_phones.png)

Two simulated phones photograph real scenes. Phone A takes a church and a sculpture against the sky, and phone B
takes the church too. I take the noise out of each photo and compare the photos pixel by pixel. Phone A's two photos
line up (r = 0.79), though their scenes differ. Phone A and phone B do not (r = 0.01), even on the same church.

The comparison uses only pixels that are plain in both scenes, as in the post. At an edge, the scene leaks into the
noise, and two photos of one scene line up there whatever the phone.

The simulation exaggerates: its pattern is 3% of the light. Two real photos from one iPhone 11 give r = 0.0004
(experiment 3). One photo is not enough, so the method averages many.

<sub>PART 2 · THE METHOD</sub>

## From noise to fingerprint

![A log-log chart: the fresh noise left in the fingerprint falls along the 1/√N line from 1 to 32 photos.](docs/img/02_averaging.png)

A simulated phone photographs 32 real scenes. The average of their noise is the phone's fingerprint. The fixed part
adds up, and the fresh part cancels: it shrinks as N^-0.51, close to the 1/√N of pure averaging. So four times the
photos halve it. The same run makes the animation at the top of this page.

```mermaid
flowchart LR
    I["Photo I"] --> F["Cleaned copy F(I)"]
    I --> W["Noise W = I − F(I)"]
    F --> W
    W -->|"many photos of one phone"| K["Fingerprint K̂"]
    K --> C["Clean-up"]
    C --> S["Score: PCE of a new photo's W against I·K̂"]
```

All of it lives in [`fingerprint.py`](fingerprint.py), in about 140 lines. Its defaults match the post.

<details>
<summary><b>Under the hood:</b> the method in formulas (2 min)</summary>

<br>

The standard model (Chen and others, 2008) writes a photo $I$ as the scene $I^{(0)}$ seen through the pixel gains
$K$, plus fresh noise $\Theta$:

```math
I = I^{(0)} + I^{(0)} K + \Theta
```

**Noise.** Subtract the cleaned copy $F(I)$. What is left is the pattern times the brightness, plus everything else,
$\Xi$:

```math
W = I - F(I) \approx I K + \Xi
```

**Cleaned copy.** The filter of Lukáš, Fridrich and Goljan (2006) splits the photo into Daubechies (db4) wavelets over
four levels. For each detail $c$, it takes the mean of $c^2$ in windows of 3, 5, 7 and 9 pixels and keeps the
smallest. It estimates the scene's share $\hat\sigma^2$ and hands the rest to the noise, with $\sigma = 5$ on the 0
to 255 scale:

```math
\hat\sigma^2 = \max\left(0,\ \overline{c^2} - \sigma^2\right), \qquad c_\text{noise} = c \, \frac{\sigma^2}{\hat\sigma^2 + \sigma^2}
```

**Fingerprint.** Bright photos carry more of the pattern, so each photo counts by its brightness:

```math
\hat K = \frac{\sum_i W_i I_i}{\sum_i I_i^2}
```

**Clean-up.** Every phone of a model shares part of its fingerprint. The clean-up zero-means each of the four 2 × 2
sub-grids by rows and by columns. Then it flattens sharp peaks in the fingerprint's spectrum (above 3 times their
local mean).

**Score.** Correlate a new photo's noise $W$ with the pattern it should carry, $I \hat K$, shifted by every $s$.
$\rho(s)$ is the correlation at shift $s$. PCE compares the peak at $s = 0$ with the rest:

```math
\mathrm{PCE} = \frac{\rho(0)^2}{\frac{1}{|S|} \sum_{s \in S} \rho(s)^2}
```

$S$ holds every shift outside an 11 × 11 window around the peak. Unrelated noise scores near 1. A score above about
60 usually means the same phone (Goljan and others, 2009).

To try a better denoiser or score, add a new experiment that compares itself with these defaults.

</details>

<sub>PART 3 · THE RESULTS</sub>

## Real iPhone 11s

![Two strip plots of scores. Without the clean-up, all 20 photos score 985 or more. With it, other iPhone 11s score near 0, and the same phone has a median of 58.](docs/img/03_real_iphones.png)

These are 60 full-size photos from Wikimedia Commons. 40 photos make the fingerprint of one iPhone 11. I score 10 more
photos from that phone and 10 photos from 10 other iPhone 11s against it. The run takes one to a few minutes and
about 2.5 GB of memory.

| Score (PCE) against the fingerprint | Same phone | 10 other iPhone 11s |
|---|---|---|
| Without the clean-up | 2,508 to 11,685 | 985 to 12,454 |
| With the clean-up | −0.1 to 368, median 58 | −1.6 to 4.6 |

Without the clean-up, every iPhone 11 matches. All of them carry a pattern from the model's design and processing.
The clean-up removes it, and then other phones score between −2 and 5, as unrelated noise should. 9 of the 10 photos
from the same phone score above every other phone. Only 5 of them clear the usual threshold of 60, so one photo is a
hint, not proof.

Single photos, compared pixel by pixel, give a median r of 0.0004 for one phone (45 pairs) and 0.0001 for two phones
(100 pairs). Those are the numbers in Part 1 of the post.

## Try it on your photos

![Bars of scores for 20 photos against one fingerprint. Five photos from the same phone pass 60, and no photo from another phone does.](docs/img/04_your_photos.png)

Give the script a folder of photos from one phone, and new photos or folders to score:

```bash
uv run experiments/04_your_photos.py ~/Pictures/my-phone ~/Pictures/new-photo.jpg
```

The figure above is its output on the Commons photos, with `data/fingerprint data/same data/other --figure out/scores.png`.
The script reads your photos on your computer and sends them nowhere. It saves nothing unless you pass `--figure`,
and git ignores `out/`.

- Use originals straight from the phone: not cropped, resized or edited, and not sent through a messenger.
- Use 20 or more photos for the fingerprint. Bright, plain photos (sky, walls) hold more of the pattern than dark or
  busy ones.
- Use the main camera at 1×, so that every photo has the same size. The script leaves out photos of another size.
- Score photos of other scenes. A second shot of a scene in the fingerprint can match through the scene's edges.
- Pillow reads JPEG and PNG. For HEIC, run `uv run --with pillow-heif experiments/04_your_photos.py ...`.

From the iPhone 16 on, Apple's processing adds a pattern that every phone of the model shares. The clean-up removes
only part of it, so a stranger's photo can still score above 60. Part 4 of the post covers it.

## Limits

- The repo reproduces the parts of the post that run on simulated phones and public photos. The line-ups of 28 iPhone
  models, the quality chart and the iPhone 16 results come from Flickr photos and from my own phone. I cannot share
  them, so they stay numbers in the post.
- Experiment 3 is one phone, 40 photos and 20 test photos. It shows the method. It does not measure its error rates.
- Simulated phones exaggerate. Their pattern is 2.5 to 3% of the light, far stronger than a real one. Their scenes
  are real photos, but the pattern and the fresh noise are added in code.
- The post also used DRUNet, a neural denoiser, which gave the same results. It needs PyTorch, so the repo leaves it
  out.

## Other public data sets

The repo ships and downloads only Wikimedia Commons photos, because each one carries a clear licence. These forensic
sets are good next steps. I checked their terms on October 27, 2026. Read each source before you use it.

| Data set | What it holds | Terms | Use here |
|---|---|---|---|
| [VISION ↗](https://lesc.dinfo.unifi.it/VISION/) (Shullani and others, 2017) | Photos and videos from 35 devices | CC BY-SA 4.0 | A fetch script would fit. Crops would need CC BY-SA. |
| [iRAW ↗](https://ieee-dataport.org/documents/iraw-multi-lens-uncompressed-iphone-camera-dataset-ai-driven-multimedia-forensics) | RAW frames from iPhone 16 Pro Max, 17 Pro and 17 Pro Max | IEEE DataPort subscription, no licence stated | Link only |
| [FODB ↗](https://arxiv.org/abs/2011.02241) (Hadwiger and Riess, 2021) | 23,106 photos from 27 devices | No licence stated | Link only |
| [Dresden ↗](http://forensics.inf.tu-dresden.de/ddimgdb/) (Gloe and Böhme, 2010) | About 17,000 photos from compact cameras and DSLRs | Site unreachable, terms unknown | Link only |
| [SCMI30 ↗](https://github.com/IPSA-Lab/scmi30-iitrpr) | 9,937 photos from 30 phone models | GPL-3.0, and "research and education purposes only" | Link only |
| [LAION-Mobile ↗](https://arxiv.org/abs/2609.11134) | About a million web photos from phones | Lists and scores only, no images | Link only |

Flickr photos each carry their owner's licence, and the post's Flickr set stays private (ADR 0004).

## Credits, licence and citation

- **Experiment 3.** 60 photos from Wikimedia Commons: 50 by -wuppertaler (CC BY 4.0) and 10 by ten other
  photographers (CC BY 4.0, CC BY-SA 4.0, CC BY 2.0, CC BY 2.5 and CC0).
  [`docs/img/CREDITS.md`](docs/img/CREDITS.md) lists each photo with its author, licence and link. The repo holds
  only their titles, in [`data/photos.tsv`](data/photos.tsv).
- **Simulated phones.** 32 more Commons photos by -wuppertaler (CC BY 4.0), as small grey copies in
  [`data/scenes/`](data/scenes/), cleaned of their own grain. [`data/scenes/CREDITS.md`](data/scenes/CREDITS.md)
  lists them, and `experiments/make_scenes.py` made them.
- **Code.** [MIT licence](LICENSE). Figures made from Commons photos keep the photos' credit.
- **Font.** The figures use [Inter ↗](https://rsms.me/inter/), under the SIL Open Font License
  ([`experiments/fonts/OFL.txt`](experiments/fonts/OFL.txt)).

The method comes from these papers:

1. J. Lukáš, J. Fridrich and M. Goljan, "Digital camera identification from sensor pattern noise", *IEEE
   Transactions on Information Forensics and Security* 1(2), 2006.
2. M. Chen, J. Fridrich, M. Goljan and J. Lukáš, "Determining image origin and integrity using sensor noise", *IEEE
   Transactions on Information Forensics and Security* 3(1), 2008.
3. M. Goljan, J. Fridrich and T. Filler, "Large scale test of sensor fingerprint camera identification", *Proc. SPIE*
   7254, Media Forensics and Security, 2009.

To cite the post:

```bibtex
@misc{hamolia2026iphone,
  author = {Vladyslav Hamolia},
  title  = {Every iPhone has a fingerprint. Can one photo give you away?},
  year   = {2026},
  url    = {https://vhamolya.com/blog/which-iphone-took-this-photo/}
}
```
