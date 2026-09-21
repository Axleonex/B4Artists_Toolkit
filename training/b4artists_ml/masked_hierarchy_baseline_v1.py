"""Leak-resistant sparse-key baseline for full-hierarchy sequence models.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import fields

import numpy as np

from motion_conditioning_v1 import MotionConditioning
from temporal_data import rotation6, rotation_matrix, slerp


JOINTS = 23
STATE_WIDTH = 3 + 6 * JOINTS
CONDITIONING_WIDTH = 483
CONTEXT_WIDTH = STATE_WIDTH + 1
MODEL_INPUT_WIDTH = STATE_WIDTH + CONDITIONING_WIDTH + CONTEXT_WIDTH


def _identity_rotation6(frames, joints):
    matrix = np.broadcast_to(np.eye(3), (frames, joints, 3, 3)).copy()
    return rotation6(matrix)


def _linear_keys(values, mask):
    values = np.asarray(values, dtype=np.float64)
    mask = np.asarray(mask, dtype=bool)
    if values.shape != mask.shape or values.ndim != 2:
        raise ValueError("Root values and mask must be matching two-dimensional arrays")
    frames, components = values.shape
    result = np.zeros_like(values)
    time = np.arange(frames, dtype=np.float64)
    for component in range(components):
        known = np.flatnonzero(mask[:, component])
        if len(known) == 0:
            continue
        if len(known) == 1:
            result[:, component] = values[known[0], component]
        else:
            result[:, component] = np.interp(
                time, known, values[known, component], left=values[known[0], component], right=values[known[-1], component]
            )
    return result


def _slerp_keys(values, mask):
    values = np.asarray(values, dtype=np.float64)
    mask = np.asarray(mask, dtype=bool)
    if values.ndim != 3 or values.shape[-1] != 6 or values.shape != mask.shape:
        raise ValueError("Rotation values and mask must be matching (frames, joints, 6) arrays")
    frames, joints, _ = values.shape
    if joints != JOINTS:
        raise ValueError("Full-hierarchy baseline requires 23 joints")
    output = _identity_rotation6(frames, joints)
    complete = mask.all(axis=-1)
    if np.any(mask.any(axis=-1) & ~complete):
        raise ValueError("Each known rotation must provide all six coordinates")
    for joint in range(joints):
        known = np.flatnonzero(complete[:, joint])
        if len(known) == 0:
            continue
        matrices, bad = rotation_matrix(values[known, joint])
        if bad.any():
            raise ValueError("Known authored rotation is degenerate")
        if len(known) == 1:
            output[:, joint] = rotation6(np.broadcast_to(matrices[0], (frames, 3, 3)))
            continue
        output[: known[0] + 1, joint] = rotation6(np.broadcast_to(matrices[0], (known[0] + 1, 3, 3)))
        output[known[-1] :, joint] = rotation6(
            np.broadcast_to(matrices[-1], (frames - known[-1], 3, 3))
        )
        for left, right, a, b in zip(known[:-1], known[1:], matrices[:-1], matrices[1:]):
            factors = np.arange(right - left + 1, dtype=np.float64) / (right - left)
            interpolated = np.asarray(slerp(a, b, factors), dtype=np.float64).reshape(len(factors), 3, 3)
            output[left : right + 1, joint] = rotation6(interpolated)
    return output


def project_authored(state, conditioning):
    """Copy exact authored values after any procedural or learned proposal."""
    condition = conditioning.validated()
    state = np.asarray(state, dtype=np.float64)
    if state.shape != (condition.frames, STATE_WIDTH) or not np.isfinite(state).all():
        raise ValueError("Expected finite full-hierarchy state sequence")
    result = state.copy()
    result[:, :3] = np.where(condition.authored_root_mask, condition.authored_root, result[:, :3])
    rotations = result[:, 3:].reshape(condition.frames, JOINTS, 6)
    rotations[:] = np.where(condition.authored_rotation_mask, condition.authored_rotation6, rotations)
    return result


def baseline_from_authored(conditioning):
    """Interpolate only visible authored values; hidden target state is never read."""
    condition = conditioning.validated()
    roots = _linear_keys(condition.authored_root, condition.authored_root_mask)
    rotations = _slerp_keys(condition.authored_rotation6, condition.authored_rotation_mask)
    state = np.concatenate((roots, rotations.reshape(condition.frames, -1)), axis=-1)
    return project_authored(state, condition)


def boundary_context(state, pad, frames):
    """Encode only the immediate observed motion outside a generated interval.

    The first delta uses previous->first authored frame and the last delta uses
    last authored->next.  No hidden inbetween frame participates.
    """
    state = np.asarray(state, dtype=np.float64)
    if state.ndim != 2 or state.shape[1] != STATE_WIDTH or frames < 2:
        raise ValueError("Invalid full-hierarchy context state")
    delta = np.zeros((frames, STATE_WIDTH), dtype=np.float32)
    known = np.zeros((frames, 1), dtype=np.float32)
    if not pad:
        return delta, known
    if pad != 1 or len(state) != frames + 2:
        raise ValueError("Exactly one surrounding context frame is supported")
    delta[0] = state[1] - state[0]
    delta[-1] = state[-1] - state[-2]
    known[[0, -1]] = 1
    return delta, known


def model_window_example(window_result):
    """Build model input/target only after a caller supplied a controlled window."""
    condition = window_result["conditioning"].validated()
    state = np.asarray(window_result["window"]["state"], dtype=np.float64)
    pad = int(window_result["window"]["context"])
    target = state[pad : len(state) - pad if pad else len(state)]
    if target.shape != (condition.frames, STATE_WIDTH):
        raise ValueError("Window target and conditioning frames disagree")
    target = project_authored(target, condition)
    baseline = baseline_from_authored(condition)
    packed, layout = condition.packed()
    context_delta, context_known = boundary_context(state, pad, condition.frames)
    features = np.concatenate(
        (baseline.astype(np.float32), packed, context_delta, context_known), axis=-1
    )
    if features.shape != (condition.frames, MODEL_INPUT_WIDTH):
        raise ValueError("Unexpected full-hierarchy model input width")
    residual = target - baseline
    root_mask = condition.authored_root_mask
    rotation_mask = condition.authored_rotation_mask.reshape(condition.frames, -1)
    mask = np.concatenate((root_mask, rotation_mask), axis=-1)
    if not np.array_equal(baseline[mask], target[mask]):
        raise ValueError("Baseline failed exact authored-control projection")
    return {
        "features": features,
        "target": target.astype(np.float32),
        "baseline": baseline.astype(np.float32),
        "residual": residual.astype(np.float32),
        "authored_mask": mask,
        "conditioning_layout": layout,
        "model_feature_layout": {
            "procedural_baseline": [0, STATE_WIDTH],
            "conditioning": [STATE_WIDTH, STATE_WIDTH + CONDITIONING_WIDTH],
            "boundary_context_delta": [STATE_WIDTH + CONDITIONING_WIDTH, MODEL_INPUT_WIDTH - 1],
            "boundary_context_known": [MODEL_INPUT_WIDTH - 1, MODEL_INPUT_WIDTH],
        },
    }
