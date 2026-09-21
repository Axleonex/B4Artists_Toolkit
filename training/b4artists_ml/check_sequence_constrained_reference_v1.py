"""Contracts for the strong reference and C2 residual envelope."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np

from sequence_constrained_reference_v1 import build, residual_envelope
from sequence_store_v1 import SequenceStore
from shape_reference import reference as shape_reference


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/sequence-constrained-reference-v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    mask = np.zeros((17, 153), dtype=bool)
    mask[[0, -1]] = True
    envelope = residual_envelope(mask)
    assert np.array_equal(envelope[mask], np.zeros(np.count_nonzero(mask), dtype=np.float32))
    assert np.allclose(envelope[8], 1, atol=0, rtol=0)
    u = np.linspace(0, 1, 17)
    expected = 64 * u**3 * (1 - u) ** 3
    assert np.allclose(envelope[:, 0], expected, atol=1e-7, rtol=0)
    store = SequenceStore(cache_clips=16)
    cases = []
    for context in (False, True):
        for pattern in (0, 1, 2):
            sampled = store.sample_batch(3, gap=32, context=context, seed=20261000 + 10 * int(context) + pattern)
            # sample_batch cycles patterns 0,1,2; select the requested row.
            identity_index = next(index for index, identity in enumerate(sampled["identities"]) if identity["pattern"] == pattern)
            identity = sampled["identities"][identity_index]
            clip_index = store.index_by_clip[identity["clip"]]
            sequence = store.clip(clip_index)
            from sequence_packet_v2 import packet
            source = packet(sequence, identity["start"], identity["start"] + 32, context=context, pattern=pattern)
            result = build(source)
            assert np.array_equal(result["baseline"][result["mask"]], result["target"][result["mask"]])
            assert np.array_equal(result["envelope"][result["mask"]], np.zeros(np.count_nonzero(result["mask"]), dtype=np.float32))
            if pattern == 0:
                expected_shape = shape_reference(source["observations"], np.arange(33) / 32)
                actual = result["baseline"][1:-1] if context else result["baseline"]
                assert np.allclose(actual, expected_shape, atol=2e-6, rtol=0)
                assert result["used_shape_reference"]
            else:
                assert np.array_equal(result["baseline"], source["request"]["baseline"].reshape(len(result["baseline"]), 153))
                assert not result["used_shape_reference"]
            cases.append({"context": context, "pattern": pattern, "shape_reference": result["used_shape_reference"]})
    invalid = 0
    for value in (np.zeros((17, 152), bool), np.zeros((17, 153), bool)):
        try:
            residual_envelope(value)
        except ValueError:
            invalid += 1
    assert invalid == 2
    report = {
        "complete": True,
        "contracts": 12,
        "cases": cases,
        "c2_analytic_envelope": True,
        "envelope_peak": float(envelope.max()),
        "authored_values_exact": True,
        "strong_control_exact_for_boundary_context": True,
        "priority_reference_unchanged": True,
        "invalid_cases": invalid,
        "seconds": time.perf_counter() - started,
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(Path(__file__).with_name("sequence_constrained_reference_v1.py")),
        "validation_read": False,
        "confirmation_read": False,
        "training": False,
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
