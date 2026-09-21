"""Torch contracts for full-hierarchy FK and motion losses."""
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import torch

from full_hierarchy_torch_kinematics_v1 import forward_kinematics, motion_loss


PARENTS = (-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 11, 15, 16, 17, 11, 19, 20, 21)
SEMANTIC = (0, 10, 11, 13, 14, 16, 17, 18, 20, 21, 22, 2, 3, 4, 6, 7, 8)


def identity_state(batch, frames):
    state = torch.zeros(batch, frames, 141)
    rotation = state[..., 3:].reshape(batch, frames, 23, 6)
    rotation[..., :3] = torch.tensor((1.0, 0.0, 0.0))
    rotation[..., 3:] = torch.tensor((0.0, 1.0, 0.0))
    return state


def main():
    torch.manual_seed(20260909)
    offsets = torch.randn(2, 23, 3) * 0.1
    offsets[:, 0] = 0
    target = identity_state(2, 9)
    position, rotation = forward_kinematics(target, offsets, PARENTS)
    assert position.shape == (2, 9, 23, 3)
    assert rotation.shape == (2, 9, 23, 3, 3)
    edge = torch.linalg.vector_norm(position[..., 1:, :] - position[..., torch.tensor(PARENTS[1:]), :], dim=-1)
    expected = torch.linalg.vector_norm(offsets[:, None, 1:, :], dim=-1)
    assert torch.allclose(edge, expected, atol=1e-6)

    contact = torch.zeros(2, 9, 2)
    contact[:, :, :] = 0.2
    zero, terms, _ = motion_loss(target, target, offsets, PARENTS, SEMANTIC, torch.tensor((1 / 30, 1 / 30)), contact)
    assert zero.item() == 0
    assert all(value.item() == 0 for value in terms.values())

    prediction = target.clone().requires_grad_(True)
    prediction.data[:, 4, 0] = 0.1
    loss, terms, _ = motion_loss(prediction, target, offsets, PARENTS, SEMANTIC, torch.tensor((1 / 30, 1 / 30)), contact)
    assert loss.item() > 0 and terms["position"].item() > 0 and terms["velocity"].item() > 0
    loss.backward()
    assert prediction.grad is not None and torch.isfinite(prediction.grad).all()
    assert torch.count_nonzero(prediction.grad) > 0

    invalid = 0
    for action in (
        lambda: forward_kinematics(target[..., :-1], offsets, PARENTS),
        lambda: motion_loss(target[:, :2], target[:, :2], offsets, PARENTS, SEMANTIC, 1 / 30),
        lambda: motion_loss(target, target, offsets, PARENTS, SEMANTIC, 0),
        lambda: motion_loss(target, target, offsets, PARENTS, SEMANTIC, 1 / 30, torch.zeros(2, 8, 2)),
    ):
        try:
            action()
        except ValueError:
            invalid += 1
    assert invalid == 4
    print(json.dumps({
        "passed": True,
        "batch": 2,
        "frames": 9,
        "joints": 23,
        "semantic_joints": 17,
        "maximum_edge_error": float(torch.max(torch.abs(edge - expected)).item()),
        "zero_identity_loss": True,
        "finite_nonzero_gradient": True,
        "loss_terms": sorted(terms),
        "invalid_cases": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
