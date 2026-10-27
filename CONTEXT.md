# iPhone fingerprint

Code that shows how a photo can name the phone that took it. The words here match the post
[Which iPhone took this photo?](https://vhamolya.com/blog/which-iphone-took-this-photo/), so the code, the README and
the post say the same thing.

## Language

**Phone**:
One physical device. Two iPhone 11s are two phones of one model.
_Avoid_: camera, device, sensor (when you mean the whole phone)

**Model**:
A product, such as the iPhone 11. All its phones share one design and one processing pipeline.

**Photo**:
One full-size file from a phone, not cropped, resized or zoomed, so its pixels line up with the sensor's.
_Avoid_: image (for a photo from a phone), frame (except for RAW wall frames)

**Cleaned copy**:
The photo after the denoiser, F(I).
_Avoid_: denoised image, smooth image

**Noise**:
The photo minus its cleaned copy, W. Forensics papers call it the noise residual.
_Avoid_: residual, grain

**Fingerprint**:
A phone's map of pixel gains, K̂, estimated from the noise of many of its photos. Forensics calls the pattern PRNU.
_Avoid_: PRNU (in code names), camera signature

**Shared pattern**:
The part of a fingerprint that every phone of one model carries. It comes from the model's design and processing, so
it says nothing about one phone.
_Avoid_: stamp (the post's informal word), artefact

**Clean-up**:
The step that removes the shared pattern from a fingerprint before scoring.

**Score**:
How well a photo's noise matches a fingerprint, as a PCE (peak-to-correlation energy). Unrelated noise scores near 1.
_Avoid_: similarity, confidence

**Simulated phone**:
A phone made in code: a real scene times (1 + K), plus fresh noise. Always labelled as a simulation.
_Avoid_: fake phone, synthetic camera
