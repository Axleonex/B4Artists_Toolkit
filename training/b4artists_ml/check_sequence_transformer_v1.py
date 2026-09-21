"""Deterministic contracts for velocity conditioning and Transformer export."""
from pathlib import Path
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve()
TR = HERE.parent
sys.path.insert(0, str(TR))

import numpy as np
import torch

from sequence_store_v1 import SequenceStore
from sequence_transformer_model_v1 import SequenceTransformer
from sequence_transformer_numpy_v1 import forward, residual
from sequence_velocity_conditioning_v1 import augment


BASE = TR / "results/sequence-transformer-contract-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    BASE.mkdir(exist_ok=False)
    started = time.perf_counter()
    store = SequenceStore(cache_clips=4)
    batch = store.sample_batch(4, gap=32, context=True, seed=20260909, constrained=True)
    condition = augment(batch["condition"])
    assert condition.shape == (4, 35, 547) and not condition.flags.writeable
    assert np.array_equal(condition[..., :394], batch["condition"])
    assert np.isfinite(condition).all()

    torch.manual_seed(20260909)
    model = SequenceTransformer().eval()
    torch.nn.init.normal_(model.output.weight, mean=0.0, std=0.02)
    weights = {name: value.detach().numpy().copy() for name, value in model.state_dict().items()}
    with torch.no_grad():
        expected = model(torch.from_numpy(np.array(condition, copy=True))).numpy()
    actual = forward(weights, condition)
    max_abs = float(np.max(np.abs(expected - actual)))
    assert max_abs < 5e-5

    correction = residual(actual, batch["envelope"])
    assert np.array_equal(correction[batch["mask"]], np.zeros_like(correction[batch["mask"]]))
    assert np.isfinite(correction).all()

    invalid = 0
    for function, value in (
        (augment, np.zeros((1, 394), dtype=np.float32)),
        (augment, np.zeros((4, 35, 393), dtype=np.float32)),
        (forward, np.zeros((4, 35, 546), dtype=np.float32)),
    ):
        try:
            function(weights, value) if function is forward else function(value)
        except ValueError:
            invalid += 1
    bad_time = np.array(batch["condition"], copy=True)
    bad_time[:, 2, -2] = bad_time[:, 1, -2]
    try:
        augment(bad_time)
    except ValueError:
        invalid += 1
    assert invalid == 4

    report = {
        "complete": True,
        "contracts": 8,
        "source_examples": 4,
        "condition_shape": list(condition.shape),
        "output_shape": list(actual.shape),
        "torch_numpy_max_abs_error": max_abs,
        "authored_residual_exact": True,
        "original_condition_exact": True,
        "invalid_cases": invalid,
        "parameters": sum(value.size for value in weights.values()),
        "parameter_bytes": sum(value.nbytes for value in weights.values()),
        "validation_read": False,
        "confirmation_read": False,
        "runtime_promoted": False,
        "full_goal_complete": False,
        "seconds": time.perf_counter() - started,
        "sources": {
            path.name: sha(path)
            for path in (
                HERE,
                TR / "sequence_velocity_conditioning_v1.py",
                TR / "sequence_transformer_model_v1.py",
                TR / "sequence_transformer_numpy_v1.py",
            )
        },
    }
    (BASE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
