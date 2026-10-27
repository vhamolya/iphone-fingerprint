"""Tests on simulated phones. They need no download."""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import fingerprint as fp

ROOT = Path(__file__).resolve().parent.parent
SIZE = 256


def photos(phone, n, seed):
    rng = np.random.default_rng(seed)
    return [phone.photo(fp.scene(rng, SIZE)) for _ in range(n)]


def test_cleaned_copy_keeps_the_scene_and_drops_the_grain():
    """A smooth gradient with one sharp edge: the cleaned copy keeps both and drops most of the grain."""
    y, x = np.mgrid[:SIZE, :SIZE]
    scene = (60 + 0.3 * x + 0.1 * y + 80 * (x > SIZE // 2)).astype(np.float32)
    grainy = scene + 3 * np.random.default_rng(0).standard_normal(scene.shape).astype(np.float32)
    assert (fp.cleaned_copy(grainy) - scene).std() < 0.5 * (grainy - scene).std()


def test_noise_is_the_photo_minus_its_cleaned_copy():
    photo = photos(fp.SimulatedPhone(1, SIZE), 1, seed=0)[0]
    w = photo - fp.cleaned_copy(photo)
    w = w - w.mean(1, keepdims=True) - w.mean(0, keepdims=True)
    np.testing.assert_allclose(fp.noise(photo), w, atol=1e-3)


def test_noise_follows_the_phone():
    """Two scenes from one phone line up. Scenes from two phones do not."""
    a, b = fp.SimulatedPhone(1, SIZE, strength=0.03), fp.SimulatedPhone(2, SIZE, strength=0.03)
    rng = np.random.default_rng(2)
    scenes = [fp.scene(rng, SIZE) for _ in range(2)]
    a1, a2, b2 = fp.noise(a.photo(scenes[0])), fp.noise(a.photo(scenes[1])), fp.noise(b.photo(scenes[1]))
    assert fp.correlation(a1, a2) > 0.2
    assert abs(fp.correlation(a1, b2)) < 0.02


def test_fingerprint_gets_closer_to_k_with_more_photos():
    phone = fp.SimulatedPhone(1, SIZE, strength=0.01, fresh=3.0)
    shots = photos(phone, 32, seed=0)
    match = [fp.correlation(fp.fingerprint(shots[:n]), phone.k) for n in (2, 8, 32)]
    assert match[0] < match[1] < match[2]
    assert match[2] > 0.5


def test_fingerprint_reads_files(tmp_path):
    shots = photos(fp.SimulatedPhone(1, SIZE), 3, seed=0)
    paths = []
    for i, shot in enumerate(shots):
        paths.append(tmp_path / f'{i}.png')
        Image.fromarray(np.round(shot).astype(np.uint8)).save(paths[-1])
    np.testing.assert_allclose(fp.fingerprint(paths), fp.fingerprint([np.round(s) for s in shots]), atol=1e-6)


def test_score_tells_the_phones_apart():
    a, b = fp.SimulatedPhone(1, SIZE), fp.SimulatedPhone(2, SIZE)
    k = fp.clean_up(fp.fingerprint(photos(a, 12, seed=0)))
    assert fp.score(photos(a, 1, seed=1)[0], k) > 10 * fp.THRESHOLD
    assert abs(fp.score(photos(b, 1, seed=1)[0], k)) < 20


def test_unrelated_noise_scores_near_one():
    rng = np.random.default_rng(0)
    scores = [fp.pce(rng.standard_normal((128, 128)), rng.standard_normal((128, 128))) for _ in range(200)]
    assert 0.6 < np.mean(np.abs(scores)) < 1.5


def test_zero_mean_removes_row_and_column_patterns():
    rng = np.random.default_rng(0)
    stripes = rng.standard_normal((1, SIZE)) + rng.standard_normal((SIZE, 1))
    grid = np.tile([[1.0, -1.0], [-0.5, 0.5]], (SIZE // 2, SIZE // 2))
    x = fp.zero_mean(stripes + grid)
    np.testing.assert_allclose(x, 0, atol=1e-9)
    y = fp.zero_mean(rng.standard_normal((SIZE, SIZE)))
    np.testing.assert_allclose(fp.zero_mean(y), y, atol=1e-9)
    for dy in (0, 1):
        for dx in (0, 1):
            np.testing.assert_allclose(y[dy::2, dx::2].mean(0), 0, atol=1e-9)
            np.testing.assert_allclose(y[dy::2, dx::2].mean(1), 0, atol=1e-9)


def test_clean_up_removes_a_shared_pattern():
    """Two phones of one model share row and column offsets in each 2 × 2 sub-grid. The clean-up removes them."""
    rng = np.random.default_rng(0)
    shared = np.zeros((SIZE, SIZE))
    for dy in (0, 1):
        for dx in (0, 1):
            shared[dy::2, dx::2] = 0.01 * (rng.standard_normal((SIZE // 2, 1)) + rng.standard_normal((1, SIZE // 2)))
    a, b = fp.SimulatedPhone(1, SIZE), fp.SimulatedPhone(2, SIZE)
    a.k, b.k = a.k + shared, b.k + shared
    k = fp.fingerprint(photos(a, 12, seed=0))
    other = photos(b, 1, seed=1)[0]
    assert fp.pce(fp.noise(other), other * k) > fp.THRESHOLD
    assert abs(fp.score(other, fp.clean_up(k))) < 20
    assert fp.score(photos(a, 1, seed=1)[0], fp.clean_up(k)) > 10 * fp.THRESHOLD


def test_flatten_removes_a_repeating_pattern():
    y, x = np.mgrid[:SIZE, :SIZE]
    wave = np.cos(np.pi * (x + 2 * y) / 8)
    k = np.random.default_rng(0).standard_normal((SIZE, SIZE)) + wave
    flat = fp.flatten(k)
    assert abs(fp.correlation(flat, wave)) < 0.1 * abs(fp.correlation(k, wave))
    assert fp.correlation(flat, k - wave) > 0.95


def test_photo_list():
    rows = [line.split('\t') for line in (ROOT / 'data/photos.tsv').read_text().splitlines()[1:]]
    groups = [g for g, _ in rows]
    titles = [t for _, t in rows]
    assert [groups.count(g) for g in ('fingerprint', 'same', 'other')] == [40, 10, 10]
    assert len(set(titles)) == 60
    assert all(t.startswith('File:') and t.lower().endswith('.jpg') for t in titles)


def test_your_photos_script(tmp_path):
    a, b = fp.SimulatedPhone(1, SIZE), fp.SimulatedPhone(2, SIZE)
    (tmp_path / 'mine').mkdir()
    for i, shot in enumerate(photos(a, 10, seed=0)):
        Image.fromarray(np.round(shot).astype(np.uint8)).save(tmp_path / 'mine' / f'{i}.png')
    for name, phone in (('a.png', a), ('b.png', b)):
        Image.fromarray(np.round(photos(phone, 1, seed=1)[0]).astype(np.uint8)).save(tmp_path / name)
    Image.new('L', (SIZE, SIZE // 2)).save(tmp_path / 'small.png')
    figure = tmp_path / 'scores.png'
    out = subprocess.run([sys.executable, ROOT / 'experiments/04_your_photos.py', tmp_path / 'mine', tmp_path / 'a.png',
                          tmp_path / 'b.png', tmp_path / 'small.png', '--figure', figure],
                         capture_output=True, text=True, check=True).stdout
    lines = {line.split()[0]: line for line in out.splitlines() if line.startswith(str(tmp_path))}
    assert 'likely the same phone' in lines[str(tmp_path / 'a.png')]
    assert 'no clear match' in lines[str(tmp_path / 'b.png')]
    assert 'Skipped' in lines[str(tmp_path / 'small.png') + ':']
    assert figure.exists()
