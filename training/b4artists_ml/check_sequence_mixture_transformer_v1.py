"""Train-only contracts for the procedural reference bank and mixture Transformer."""
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

from kinematic_trajectory_v20 import predict_packed as control_predict
from sequence_mixture_transformer_model_v1 import MixtureTransformer
from sequence_mixture_transformer_numpy_v1 import compose, forward
from sequence_packet_v2 import packet
from sequence_reference_bank_v1 import ReferenceBankSampler, build
from sequence_store_v1 import SequenceStore


BASE = TR / "results/sequence-mixture-transformer-contract-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    BASE.mkdir(exist_ok=False)
    started = time.perf_counter()
    store = SequenceStore(cache_clips=4)
    sampler = ReferenceBankSampler(store)
    batch = sampler.sample_batch(4, gap=32, context=True, seed=20260909)
    assert batch["condition"].shape == (4, 35, 853)
    assert batch["references"].shape == (4, 35, 3, 153)
    assert batch["target"].shape == batch["mask"].shape == batch["envelope"].shape == (4, 35, 153)
    assert np.isfinite(batch["condition"]).all() and np.isfinite(batch["references"]).all()
    for index in range(3):
        assert np.array_equal(
            batch["references"][:, :, index][batch["mask"]],
            batch["target"][batch["mask"]],
        )

    # The no-interior-key reference must reproduce the protected direct Hermite control.
    sequence = store.clip(store.by_subject[store.subjects[0]][0])
    row = packet(sequence, 1, 33, context=True, pattern=0)
    prepared = build(row)
    expected = control_predict(
        {"kind": "baseline", "baseline": "hermite"},
        row["observations"],
        np.arange(33, dtype=np.float64) / 32,
    ).astype(np.float32)
    assert np.array_equal(prepared["references"][1:-1, 1], expected)
    assert prepared["used_distinct_references"]
    assert np.any(prepared["references"][:, 0] != prepared["references"][:, 1])

    # Hidden answers may change labels, never model inputs or proposal references.
    changed = dict(row)
    changed_target = np.array(row["target"], copy=True).reshape(len(row["target"]), 153)
    changed_target[~row["request"]["mask"].reshape(len(changed_target), 153)] += 123.0
    changed["target"] = changed_target.reshape(row["target"].shape)
    changed_prepared = build(changed)
    assert np.array_equal(prepared["condition"], changed_prepared["condition"])
    assert np.array_equal(prepared["references"], changed_prepared["references"])
    assert np.array_equal(prepared["envelope"], changed_prepared["envelope"])

    torch.manual_seed(20260909)
    model = MixtureTransformer().eval()
    torch.nn.init.normal_(model.output.weight, mean=0.0, std=0.02)
    weights = {name: value.detach().numpy().copy() for name, value in model.state_dict().items()}
    with torch.no_grad():
        expected_raw = model(torch.from_numpy(np.array(batch["condition"], copy=True))).numpy()
    actual_raw = forward(weights, batch["condition"])
    max_abs = float(np.max(np.abs(expected_raw - actual_raw)))
    assert max_abs < 5e-5

    output, mixture, correction = compose(
        actual_raw,
        batch["references"],
        batch["envelope"],
        batch["mask"],
        batch["target"],
    )
    assert output.shape == correction.shape == batch["target"].shape
    assert mixture.shape == (4, 3)
    assert np.all(mixture >= 0) and np.allclose(mixture.sum(axis=-1), 1.0, atol=1e-6, rtol=0)
    assert np.array_equal(output[batch["mask"]], batch["target"][batch["mask"]])
    assert np.array_equal(correction[batch["mask"]], np.zeros_like(correction[batch["mask"]]))

    invalid = 0
    for function in (
        lambda: forward(weights, np.zeros((1, 4, 852), dtype=np.float32)),
        lambda: compose(actual_raw, batch["references"], batch["envelope"], batch["mask"]),
        lambda: compose(actual_raw, batch["references"], batch["envelope"], batch["mask"][:, :-1], batch["target"]),
    ):
        try:
            function()
        except ValueError:
            invalid += 1
    assert invalid == 3

    report = {
        "complete": True,
        "contracts": 13,
        "source_examples": 4,
        "condition_shape": list(batch["condition"].shape),
        "reference_shape": list(batch["references"].shape),
        "output_shape": list(output.shape),
        "torch_numpy_max_abs_error": max_abs,
        "authored_values_exact": True,
        "hidden_target_invariant": True,
        "direct_hermite_exact": True,
        "convex_mixture": True,
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
                TR / "sequence_reference_bank_v1.py",
                TR / "sequence_mixture_transformer_model_v1.py",
                TR / "sequence_mixture_transformer_numpy_v1.py",
            )
        },
    }
    (BASE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
