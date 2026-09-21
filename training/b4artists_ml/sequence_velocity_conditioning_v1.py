"""Observed-only velocity features for keyframe-conditioned sequence models.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np


BASE_CONDITION = 394
POSE_CHANNELS = 153
CONDITION = BASE_CONDITION + POSE_CHANNELS


def augment(condition):
    """Append signed-log baseline velocity without consulting hidden motion."""
    values = np.asarray(condition, dtype=np.float32)
    if values.ndim not in (2, 3) or values.shape[-1] != BASE_CONDITION:
        raise ValueError("Expected [time,394] or [batch,time,394] condition")
    if values.shape[-2] < 2 or not np.isfinite(values).all():
        raise ValueError("Invalid condition")
    single = values.ndim == 2
    rows = values[None] if single else values
    baseline = rows[..., :POSE_CHANNELS]
    relative_time = rows[..., -2]
    if np.any(np.diff(relative_time, axis=1) <= 0):
        raise ValueError("Condition time must be strictly increasing")
    velocity = np.empty_like(baseline)
    velocity[:, 0] = (baseline[:, 1] - baseline[:, 0]) / (
        relative_time[:, 1] - relative_time[:, 0]
    )[:, None]
    velocity[:, -1] = (baseline[:, -1] - baseline[:, -2]) / (
        relative_time[:, -1] - relative_time[:, -2]
    )[:, None]
    if baseline.shape[1] > 2:
        velocity[:, 1:-1] = (baseline[:, 2:] - baseline[:, :-2]) / (
            relative_time[:, 2:] - relative_time[:, :-2]
        )[..., None]
    velocity = np.sign(velocity) * np.log1p(np.abs(velocity))
    result = np.concatenate((rows, velocity), axis=-1).astype(np.float32, copy=False)
    if not np.isfinite(result).all() or result.shape[-1] != CONDITION:
        raise ValueError("Invalid augmented condition")
    result = result[0] if single else result
    result.setflags(write=False)
    return result

