"""Actual-data optimization integration check for the diffusion candidate."""
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from full_hierarchy_diffusion_v1 import ConditionalResidualDiffusionUNet, q_sample
from full_hierarchy_sequence_dataset_v2 import PriorityHierarchySequenceDataset, load_priority_specs
from full_hierarchy_torch_kinematics_v1 import motion_loss


SEED = 20260914
STEPS = 160


def tensor(value, device, dtype=None):
    return torch.as_tensor(np.array(value, copy=True), dtype=dtype, device=device)


def main():
    torch.manual_seed(SEED)
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training, _ = load_priority_specs(ROOT)
    selected = next(item for item in training if item["gap"] == 32 and item["mask_pattern"] == "endpoints")
    dataset = PriorityHierarchySequenceDataset(
        [selected], "training", split["training_subjects"], labels["thresholds"]["contact"],
        weak_contacts=True, root=ROOT,
    )
    example = dataset[0]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    features = tensor(example["features"], device).unsqueeze(0)
    baseline = tensor(example["baseline"], device).unsqueeze(0)
    target = tensor(example["target"], device).unsqueeze(0)
    mask = tensor(example["authored_mask"], device, torch.bool).unsqueeze(0)
    offsets = tensor(example["offsets"], device).unsqueeze(0)
    contact = tensor(example["contact_weight"], device).unsqueeze(0)
    dt = torch.tensor((float(example["dt"]),), device=device)
    clean_target = (target - baseline).masked_fill(mask, 0)
    model = ConditionalResidualDiffusionUNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    generator = torch.Generator(device=device).manual_seed(SEED)
    history = []
    for step in range(STEPS):
        timestep = torch.randint(0, 100, (1,), generator=generator, device=device)
        noise = torch.randn(clean_target.shape, generator=generator, device=device)
        noisy, _ = q_sample(clean_target, mask, timestep, noise)
        optimizer.zero_grad(set_to_none=True)
        prediction = model.predict_clean_residual(noisy, features, mask, timestep)
        hidden = ~mask
        diffusion = torch.sum((prediction - clean_target).square() * hidden) / hidden.sum()
        output = model.compose(prediction, baseline, mask)
        motion, _, _ = motion_loss(
            output, target, offsets, example["parents"], example["semantic"], dt, contact
        )
        loss = diffusion + 0.5 * motion
        if not torch.isfinite(loss):
            raise AssertionError("Diffusion microfit became non-finite")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        history.append(float(loss.detach().item()))
    with torch.no_grad():
        timestep = torch.tensor((50,), device=device)
        noise = torch.randn(clean_target.shape, generator=generator, device=device)
        noisy, _ = q_sample(clean_target, mask, timestep, noise)
        prediction = model.predict_clean_residual(noisy, features, mask, timestep)
        hidden = ~mask
        diffusion = torch.sum((prediction - clean_target).square() * hidden) / hidden.sum()
        output = model.compose(prediction, baseline, mask)
        motion, _, _ = motion_loss(
            output, target, offsets, example["parents"], example["semantic"], dt, contact
        )
        final = float((diffusion + 0.5 * motion).item())
    initial = history[0]
    assert min(history[-20:] + [final]) < initial * 0.35
    assert torch.equal(output[mask], target[mask])
    print(json.dumps({
        "passed": True,
        "scope": "one actual v2 training window; optimization integration only",
        "clip": selected["clip"],
        "frames": features.shape[1],
        "steps": STEPS,
        "initial_loss": initial,
        "best_last_20_or_final": min(history[-20:] + [final]),
        "final_fixed_timestep_loss": final,
        "exact_complete_priority_projection": True,
        "development_read": False,
        "confirmation_read": False,
        "generalization_claim": False,
        "runtime_promoted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
