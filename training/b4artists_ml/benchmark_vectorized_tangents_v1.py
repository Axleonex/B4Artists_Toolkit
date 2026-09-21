"""Bit-exact research benchmark for vectorized scalar-curve tangents."""
from pathlib import Path
import hashlib
import json
import statistics
import sys
import time

import numpy as np


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
OUT = HERE.parent / "results/vectorized-tangents-v1"
sys.path.insert(0, str(ROOT))
from b4artists_ml.curve_smoothing import tangents as reference_tangents


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_tangents(times, values):
    x = np.asarray(times, dtype=float)
    y = np.asarray(values, dtype=float)
    if (x.ndim != 1 or len(x) < 2 or y.ndim < 1 or y.shape[0] != len(x) or
            not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(np.diff(x) <= 0)):
        raise ValueError('Increasing finite samples required')
    h = np.diff(x)
    shape = (len(h),) + (1,) * (y.ndim - 1)
    d = np.diff(y, axis=0) / h.reshape(shape)
    m = np.empty_like(y)
    m[0] = d[0]
    m[-1] = d[-1]
    left, right = d[:-1], d[1:]
    hleft = np.broadcast_to(h[:-1].reshape((len(h)-1,) + (1,) * (y.ndim-1)), left.shape)
    hright = np.broadcast_to(h[1:].reshape((len(h)-1,) + (1,) * (y.ndim-1)), left.shape)
    interior = np.zeros_like(left)
    same = (np.sign(left) == np.sign(right)) & (left != 0) & (right != 0)
    w1 = 2 * hright + hleft
    w2 = hright + 2 * hleft
    interior[same] = (w1[same] + w2[same]) / (w1[same] / left[same] + w2[same] / right[same])
    m[1:-1] = interior
    if not np.isfinite(m).all():
        raise ValueError('Nonfinite tangent')
    return m


def handles(function, x, y):
    m = function(x, y)
    h = np.diff(x)
    left = np.c_[x, y]
    right = left.copy()
    left[1:, 0] -= h / 3
    left[1:, 1] -= h * m[1:] / 3
    right[:-1, 0] += h / 3
    right[:-1, 1] += h * m[:-1] / 3
    return left, right


def main():
    OUT.mkdir(exist_ok=False)
    rng = np.random.default_rng(1904)
    cases = []
    for index in range(2000):
        count = int(rng.integers(2, 241))
        x = np.cumsum(rng.uniform(.001, 20., count))
        mode = index % 5
        if mode == 0:
            y = np.cumsum(rng.uniform(0., 5., count))
        elif mode == 1:
            y = -np.cumsum(rng.uniform(0., 5., count))
        elif mode == 2:
            y = rng.normal(size=count)
        elif mode == 3:
            y = np.repeat(rng.normal(size=(count + 3) // 4), 4)[:count]
        else:
            y = np.zeros(count)
        expected = reference_tangents(x, y)
        actual = candidate_tangents(x, y)
        assert np.array_equal(actual, expected)
        expected_handles = handles(reference_tangents, x, y)
        actual_handles = handles(candidate_tangents, x, y)
        assert all(np.array_equal(a, b) for a, b in zip(expected_handles, actual_handles))
        cases.append((x, y))

    invalid = [([0.], [1.]), ([0., 0.], [1., 2.]), ([1., 0.], [1., 2.]),
               ([0., 1.], [1., np.nan]), ([0., np.inf], [1., 2.]), ([0., 1.], [1.])]
    invalid_results = []
    for x, y in invalid:
        row = []
        for function in (reference_tangents, candidate_tangents):
            try:
                function(x, y)
            except ValueError as exc:
                row.append((type(exc).__name__, str(exc)))
            else:
                row.append(None)
        assert row[0] == row[1]
        invalid_results.append(row[0])

    workload = cases[:300]
    timings = {"reference": [], "candidate": []}
    for variant in ("reference", "candidate", "candidate", "reference") * 10:
        function = reference_tangents if variant == "reference" else candidate_tangents
        started = time.perf_counter()
        for x, y in workload:
            function(x, y)
        timings[variant].append(time.perf_counter() - started)
    medians = {name: statistics.median(values) for name, values in timings.items()}
    ratio = medians["candidate"] / medians["reference"]
    report = {
        "schema": 1,
        "complete": True,
        "qualified": ratio <= .50,
        "random_cases": len(cases),
        "invalid_cases": len(invalid),
        "bit_exact_tangents": True,
        "bit_exact_handles": True,
        "identical_invalid_contract": True,
        "benchmark_curves_per_run": len(workload),
        "timing_runs_per_variant": len(timings["reference"]),
        "median_seconds": medians,
        "candidate_to_reference_ratio": ratio,
        "reduction_percent": (1 - ratio) * 100,
        "script_sha256": sha(HERE),
        "production_changed": False,
        "method_promoted": False,
        "full_goal_complete": False,
        "limitations": "Plain-Python NumPy microbenchmark; native integrated publication remains required before promotion.",
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
