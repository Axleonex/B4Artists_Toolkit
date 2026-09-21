"""Observed-only contextual curve baseline for sequence residual learning.

SPDX-License-Identifier: GPL-2.0-or-later
Research only: this baseline is procedural and must remain labelled as such.
"""
import numpy as np

from sequence_conditioning_v1 import expanded_mask, request
from temporal_data import quat_matrix, quaternion, rotation6, rotation_matrix, slerp


SCHEMA = "b4ml-observed-shape-baseline-v1"


def _derivatives(times, values):
    """Return observed-only Catmull-Rom derivatives for irregular samples."""
    t = np.asarray(times, dtype=np.float64)
    v = np.asarray(values, dtype=np.float64)
    if t.ndim != 1 or len(t) != len(v) or len(t) < 2 or np.any(np.diff(t) <= 0):
        raise ValueError("Increasing observed samples required")
    result = np.empty_like(v)
    result[0] = (v[1] - v[0]) / (t[1] - t[0])
    result[-1] = (v[-1] - v[-2]) / (t[-1] - t[-2])
    if len(t) > 2:
        result[1:-1] = (v[2:] - v[:-2]) / (t[2:, None] - t[:-2, None])
    return result


def _hermite(times, sample_times, values):
    t = np.asarray(times, dtype=np.float64)
    knots = np.asarray(sample_times, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    derivatives = _derivatives(knots, values)
    segment = np.clip(np.searchsorted(knots, t, side="right") - 1, 0, len(knots) - 2)
    left = knots[segment]
    span = knots[segment + 1] - left
    u = ((t - left) / span)[:, None]
    h00 = 2 * u**3 - 3 * u**2 + 1
    h10 = u**3 - 2 * u**2 + u
    h01 = -2 * u**3 + 3 * u**2
    h11 = u**3 - u**2
    return (h00 * values[segment] + h10 * span[:, None] * derivatives[segment]
            + h01 * values[segment + 1] + h11 * span[:, None] * derivatives[segment + 1])


def _aligned_quaternions(matrices):
    q = quaternion(matrices).copy()
    for index in range(1, len(q)):
        if np.dot(q[index - 1], q[index]) < 0:
            q[index] *= -1
    return q


def _rotation_curve(times, sample_times, matrices):
    knots = np.asarray(sample_times, dtype=np.float64)
    matrices = np.asarray(matrices, dtype=np.float64)
    if len(knots) == 2:
        u = (np.asarray(times) - knots[0]) / (knots[1] - knots[0])
        return slerp(matrices[0], matrices[1], u)[:, 0]
    q = _aligned_quaternions(matrices)
    curve = _hermite(times, knots, q)
    norm = np.linalg.norm(curve, axis=-1, keepdims=True)
    segment = np.clip(np.searchsorted(knots, times, side="right") - 1, 0, len(knots) - 2)
    u = (np.asarray(times) - knots[segment]) / (knots[segment + 1] - knots[segment])
    # The shared slerp helper treats its time input as a new leading sample
    # dimension.  Here each time belongs to an already-indexed quaternion pair,
    # so interpolate the aligned pairs row by row for the degenerate fallback.
    qa = q[segment]
    qb = q[segment + 1]
    blend = u[:, None]
    fallback = qa * (1.0 - blend) + qb * blend
    fallback /= np.maximum(np.linalg.norm(fallback, axis=-1, keepdims=True), 1e-12)
    normalized = np.where(norm > 1e-8, curve / np.maximum(norm, 1e-12), fallback)
    return quat_matrix(normalized)


def build(times, observed, mask, rest):
    """Build a contextual baseline using observed values only.

    Position and orientation masks remain independent. With only two samples,
    the result equals the established linear/SLERP request. Exterior or sparse
    authored samples supply curve derivatives without exposing hidden labels.
    """
    base = request(times, observed, mask, rest)
    t = base["times"]
    known = base["observed"]
    m = np.asarray(mask)
    shaped = np.array(base["baseline"], dtype=np.float64, copy=True)
    for joint in range(17):
        position_ids = np.flatnonzero(m[:, joint, 0])
        shaped[:, joint, :3] = _hermite(t, t[position_ids], known[position_ids, joint, :3])
        rotation_ids = np.flatnonzero(m[:, joint, 1])
        rotations, bad = rotation_matrix(known[rotation_ids, joint, 3:])
        if bad.any():
            raise ValueError("Degenerate observed orientation")
        shaped[:, joint, 3:] = rotation6(_rotation_curve(t, t[rotation_ids], rotations))
    expanded = expanded_mask(m)
    shaped[expanded] = known[expanded]
    if not np.isfinite(shaped).all():
        raise ValueError("Nonfinite contextual baseline")
    condition = np.array(base["condition"], copy=True)
    condition[:, :153] = shaped.reshape(len(t), 153)
    shaped = shaped.astype(np.float32)
    condition = condition.astype(np.float32)
    shaped.setflags(write=False)
    condition.setflags(write=False)
    result = dict(base)
    result.update(baseline=shaped, condition=condition)
    return {"request": result, "schema": SCHEMA}
