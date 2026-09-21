"""Bounded actual-data microfit for the fixed full-hierarchy TCN.

This proves that the streaming example, network, kinematics and composite loss
can optimize together.  It is not a generalization or promotion result.
"""
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from full_hierarchy_sequence_dataset_v1 import HierarchySequenceDataset, load_specs
from full_hierarchy_tcn_v1 import MaskedResidualTCN
from full_hierarchy_torch_kinematics_v1 import motion_loss


SEED = 20260909
STEPS = 160


def tensor(value, device, dtype=None):
    array = np.array(value, copy=True)
    return torch.as_tensor(array, dtype=dtype, device=device)


def main():
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training, _ = load_specs(ROOT)
    selected = next(
        item for item in training
        if item["gap"] == 32 and item["mask_pattern"] == "endpoints"
    )
    dataset = HierarchySequenceDataset(
        [selected],
        "training",
        split["training_subjects"],
        labels["thresholds"]["contact"],
        weak_contacts=True,
        root=ROOT,
    )
    example = dataset[0]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    features = tensor(example["features"], device, torch.float32).unsqueeze(0)
    baseline = tensor(example["baseline"], device, torch.float32).unsqueeze(0)
    target = tensor(example["target"], device, torch.float32).unsqueeze(0)
    authored = tensor(example["authored_mask"], device, torch.bool).unsqueeze(0)
    offsets = tensor(example["offsets"], device, torch.float32).unsqueeze(0)
    contact = tensor(example["contact_weight"], device, torch.float32).unsqueeze(0)
    parents = tuple(int(value) for value in example["parents"])
    semantic = tuple(int(value) for value in example["semantic"])
    dt = torch.tensor((float(example["dt"]),), device=device)

    model = MaskedResidualTCN(width=128).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    with torch.no_grad():
        initial_output = model(features, baseline, authored)
        initial, _, _ = motion_loss(
            initial_output, target, offsets, parents, semantic, dt, contact
        )
    best = float(initial.item())
    final = best
    for _ in range(STEPS):
        optimizer.zero_grad(set_to_none=True)
        output = model(features, baseline, authored)
        loss, _, _ = motion_loss(output, target, offsets, parents, semantic, dt, contact)
        if not torch.isfinite(loss):
            raise AssertionError("Microfit loss became non-finite")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        final = float(loss.detach().item())
        best = min(best, final)
        if not torch.equal(output[authored], baseline[authored]):
            raise AssertionError("Authored projection changed during microfit")

    with torch.no_grad():
        output = model(features, baseline, authored)
        measured, terms, _ = motion_loss(
            output, target, offsets, parents, semantic, dt, contact
        )
    final = float(measured.item())
    assert final < float(initial.item()) * 0.25
    assert torch.equal(output[authored], baseline[authored])
    print(json.dumps({
        "passed": True,
        "scope": "one actual training window; optimization integration only",
        "clip": selected["clip"],
        "gap": selected["gap"],
        "frames": features.shape[1],
        "device": str(device),
        "steps": STEPS,
        "initial_loss": float(initial.item()),
        "best_training_step_loss": best,
        "final_loss": final,
        "final_ratio": final / float(initial.item()),
        "exact_authored_projection": True,
        "finite": all(torch.isfinite(value).item() for value in terms.values()),
        "development_read": False,
        "confirmation_read": False,
        "generalization_claim": False,
        "runtime_promoted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
