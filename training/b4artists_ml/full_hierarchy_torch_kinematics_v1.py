"""Differentiable full-hierarchy FK and shared motion losses.

SPDX-License-Identifier: GPL-2.0-or-later
Training dependency only.
"""
import torch
from torch.nn import functional as F


JOINTS = 23
STATE_WIDTH = 141
FOOT_SEMANTIC_SLOTS = (13, 16)


def rotation_matrices(state, epsilon=1e-8):
    if state.shape[-1] != STATE_WIDTH:
        raise ValueError("Expected 141 full-hierarchy state features")
    values = state[..., 3:].reshape(*state.shape[:-1], JOINTS, 6)
    first, second = values[..., :3], values[..., 3:]
    x = F.normalize(first, dim=-1, eps=epsilon)
    y = second - x * torch.sum(x * second, dim=-1, keepdim=True)
    y = F.normalize(y, dim=-1, eps=epsilon)
    return torch.stack((x, y, torch.cross(x, y, dim=-1)), dim=-1)


def forward_kinematics(state, offsets, parents):
    if state.ndim != 3 or state.shape[-1] != STATE_WIDTH:
        raise ValueError("State must have shape (batch, frames, 141)")
    if len(parents) != JOINTS or int(parents[0]) != -1:
        raise ValueError("Expected a 23-joint hierarchy")
    parent_values = tuple(int(value) for value in parents)
    if any(parent < 0 or parent >= joint for joint, parent in enumerate(parent_values[1:], 1)):
        raise ValueError("Hierarchy parents must precede children")
    if offsets.ndim == 2:
        offsets = offsets.unsqueeze(0)
    if offsets.ndim != 3 or offsets.shape[-2:] != (JOINTS, 3):
        raise ValueError("Offsets must have shape (23, 3) or (batch, 23, 3)")
    if offsets.shape[0] not in (1, state.shape[0]):
        raise ValueError("Offset batch does not match state batch")
    offsets = offsets.expand(state.shape[0], -1, -1)
    local = rotation_matrices(state)
    positions = [state[..., :3]]
    world = [local[..., 0, :, :]]
    for joint, parent in enumerate(parent_values[1:], 1):
        rotated = torch.matmul(world[parent], offsets[:, None, joint, :, None]).squeeze(-1)
        positions.append(positions[parent] + rotated)
        world.append(torch.matmul(world[parent], local[..., joint, :, :]))
    return torch.stack(positions, dim=-2), torch.stack(world, dim=-3)


def _time_scale(dt, dimensions):
    if not torch.is_tensor(dt):
        dt = torch.as_tensor(dt)
    if dt.ndim == 0:
        dt = dt[None]
    if dt.ndim != 1 or torch.any(dt <= 0):
        raise ValueError("Positive per-batch frame intervals are required")
    return dt.reshape(len(dt), *([1] * dimensions))


def motion_loss(prediction, target, offsets, parents, semantic, dt, contact_weight=None, weights=None):
    if prediction.shape != target.shape or prediction.ndim != 3 or prediction.shape[-1] != STATE_WIDTH:
        raise ValueError("Prediction and target must be matching (batch, frames, 141) tensors")
    if prediction.shape[1] < 3:
        raise ValueError("At least three frames are required for temporal loss")
    if len(semantic) != 17:
        raise ValueError("Expected 17 semantic joints")
    weights = {
        "root": 1.0,
        "position": 1.0,
        "rotation": 1.0,
        "velocity": 0.05,
        "acceleration": 0.0005,
        "contact": 0.1,
        **(weights or {}),
    }
    pred_position, pred_rotation = forward_kinematics(prediction, offsets, parents)
    target_position, target_rotation = forward_kinematics(target, offsets, parents)
    semantic = tuple(int(value) for value in semantic)
    pp, tp = pred_position[..., semantic, :], target_position[..., semantic, :]
    pr, tr = pred_rotation[..., semantic, :, :], target_rotation[..., semantic, :, :]
    step = _time_scale(dt, 3).to(prediction.device, prediction.dtype)
    velocity_error = (pp[:, 1:] - pp[:, :-1] - (tp[:, 1:] - tp[:, :-1])) / step
    acceleration_error = (velocity_error[:, 1:] - velocity_error[:, :-1]) / step
    terms = {
        "root": F.mse_loss(prediction[..., :3], target[..., :3]),
        "position": F.mse_loss(pp, tp),
        "rotation": F.mse_loss(pr, tr),
        "velocity": torch.mean(velocity_error.square()),
        "acceleration": torch.mean(acceleration_error.square()),
    }
    if contact_weight is None:
        terms["contact"] = prediction.new_zeros(())
    else:
        if contact_weight.shape != (prediction.shape[0], prediction.shape[1], 2):
            raise ValueError("Contact weight must have shape (batch, frames, 2)")
        foot_indices = tuple(semantic[index] for index in FOOT_SEMANTIC_SLOTS)
        foot_velocity = (pred_position[:, 1:, foot_indices] - pred_position[:, :-1, foot_indices]) / step
        contact = torch.minimum(contact_weight[:, 1:], contact_weight[:, :-1]).unsqueeze(-1)
        terms["contact"] = torch.sum(foot_velocity.square() * contact) / torch.clamp(
            contact.sum() * foot_velocity.shape[-1], min=1.0
        )
    total = sum(float(weights[name]) * value for name, value in terms.items())
    return total, terms, {"position": pred_position, "rotation": pred_rotation}
