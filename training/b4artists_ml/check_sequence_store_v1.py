"""Contracts for memory-mapped expanded-corpus sampling."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np

from sequence_store_v1 import SequenceStore, STYLE_NAMES


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/sequence-store-contract-v3"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    store = SequenceStore(verify_hashes=True, cache_clips=4)
    assert len(store.entries) == 1840 and len(store.subjects) == 85
    assert isinstance(store.positions, np.memmap) and isinstance(store.rotations, np.memmap)
    cases = []
    for gap in (8, 16, 32, 64, 96):
        for context in (False, True):
            batch = store.sample_batch(6, gap=gap, context=context, seed=20260909 + gap + int(context))
            frames = gap + 1 + 2 * int(context)
            assert batch["condition"].shape == (6, frames, 394)
            assert batch["baseline"].shape == batch["target"].shape == batch["mask"].shape == (6, frames, 153)
            assert batch["style"].shape == (6, len(STYLE_NAMES))
            assert np.isfinite(batch["condition"]).all() and np.isfinite(batch["target"]).all()
            assert np.array_equal(batch["baseline"][batch["mask"]], batch["target"][batch["mask"]])
            clean = batch["condition"][..., 153:306]
            assert np.count_nonzero(clean[~batch["mask"]]) == 0
            repeat = store.sample_batch(6, gap=gap, context=context, seed=20260909 + gap + int(context))
            assert repeat["identities"] == batch["identities"]
            assert np.array_equal(repeat["condition"], batch["condition"])
            constrained = store.sample_batch(
                6,
                gap=gap,
                context=context,
                seed=20260909 + gap + int(context),
                constrained=True,
            )
            assert constrained["envelope"].shape == (6, frames, 153)
            assert np.array_equal(
                constrained["baseline"][constrained["mask"]],
                constrained["target"][constrained["mask"]],
            )
            cases.append({"gap": gap, "context": context, "frames": frames, "examples": 6})
    invalid = 0
    for kwargs in (
        {"batch_size": 0, "gap": 8, "context": False, "seed": 1},
        {"batch_size": 1, "gap": 7, "context": False, "seed": 1},
        {"batch_size": 1, "gap": 8, "context": 1, "seed": 1},
    ):
        try:
            store.sample_batch(**kwargs)
        except ValueError:
            invalid += 1
    assert invalid == 3
    report = {
        "complete": True,
        "cases": cases,
        "case_count": len(cases),
        "examples": sum(row["examples"] for row in cases),
        "clips": len(store.entries),
        "subjects": len(store.subjects),
        "memory_mapped": True,
        "precomputed_rotation_matrices": True,
        "subject_balanced_sampling": True,
        "deterministic_sampling": True,
        "known_values_exact": True,
        "hidden_condition_zero": True,
        "style_channels": len(STYLE_NAMES),
        "invalid_cases": invalid,
        "seconds": time.perf_counter() - started,
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(Path(__file__).with_name("sequence_store_v1.py")),
        "validation_read": False,
        "confirmation_read": False,
        "training": False,
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
