"""Analytic contracts for the observed-only contextual shape baseline."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np

from sequence_conditioning_v1 import request
from sequence_shape_conditioning_v1 import build


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
OUT = HERE.parent / "results/sequence-shape-conditioning-v4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(frames=33):
    times = np.linspace(-1 / 30, 1 + 1 / 30, frames)
    values = np.full((frames, 17, 9), np.nan)
    mask = np.zeros((frames, 17, 2), dtype=bool)
    ids = np.array([0, 1, frames - 2, frames - 1])
    mask[ids] = True
    phase = np.array([-0.08, 0.0, 1.0, 1.12])
    for row, u in zip(ids, phase):
        values[row, :, 0] = u + np.arange(17) * 0.01
        values[row, :, 1] = u * u * 0.2
        values[row, :, 2] = np.sin(u) * 0.1
        angle = u * 0.4
        values[row, :, 3:9] = np.array([np.cos(angle), np.sin(angle), 0, -np.sin(angle), np.cos(angle), 0])
    return times, values, mask, np.zeros((17, 3))


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    times, values, mask, rest = fixture()
    shaped = build(times, values, mask, rest)["request"]
    linear = request(times, values, mask, rest)
    assert shaped["condition"].shape == linear["condition"].shape == (33, 394)
    known = shaped["mask"]
    assert np.array_equal(shaped["baseline"][known], linear["baseline"][known])
    assert np.array_equal(shaped["baseline"][known], shaped["observed"][known].astype(np.float32))
    assert np.max(np.abs(shaped["baseline"][2:-2] - linear["baseline"][2:-2])) > 1e-4
    assert np.isfinite(shaped["baseline"]).all()

    # Hidden payloads cannot influence the request.
    alternate = values.copy()
    rng = np.random.default_rng(20260909)
    alternate[~np.repeat(mask, [3, 6], axis=-1)] = rng.normal(size=np.count_nonzero(~np.repeat(mask, [3, 6], axis=-1)))
    other = build(times, alternate, mask, rest)["request"]
    assert np.array_equal(shaped["condition"], other["condition"])
    assert np.array_equal(shaped["baseline"], other["baseline"])

    # Without exterior or interior observations, shape reduces to linear/SLERP.
    plain_mask = np.zeros_like(mask)
    plain_mask[[1, -2]] = True
    plain = build(times[1:-1], values[1:-1], plain_mask[1:-1], rest)["request"]
    plain_linear = request(times[1:-1], values[1:-1], plain_mask[1:-1], rest)
    assert np.allclose(plain["baseline"], plain_linear["baseline"], atol=2e-6, rtol=0)

    invalid = 0
    for mutate in ("time", "mask", "rotation"):
        t, y, m, r = fixture()
        if mutate == "time":
            t[4] = t[3]
        elif mutate == "mask":
            m[0] = False
        else:
            y[1, 0, 3:9] = 0
        try:
            build(t, y, m, r)
        except ValueError:
            invalid += 1
    assert invalid == 3
    report = {
        "complete": True,
        "contracts": 7,
        "known_values_exact": True,
        "hidden_payload_invariant": True,
        "two_sample_equivalent": True,
        "context_changes_baseline": True,
        "invalid_cases": invalid,
        "seconds": time.perf_counter() - started,
        "script_sha256": sha(HERE),
        "module_sha256": sha(HERE.with_name("sequence_shape_conditioning_v1.py")),
        "training": False,
        "validation_read": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
