"""Strong observed-only reference and C2 residual envelope.

SPDX-License-Identifier: GPL-2.0-or-later
Research only; no model weights or runtime registration.
"""
import numpy as np

from shape_reference import reference as shape_reference


def residual_envelope(mask):
    """Return a channel-wise envelope with zero value/slope/curvature at keys."""
    known = np.asarray(mask, dtype=bool)
    if known.ndim not in (2, 3) or known.shape[-1] != 153:
        raise ValueError("Expected [time,153] or [batch,time,153] mask")
    single = known.ndim == 2
    if single:
        known = known[None]
    if not known[:, [0, -1]].all():
        raise ValueError("Complete boundary observations required")
    result = np.zeros(known.shape, dtype=np.float32)
    for batch in range(len(known)):
        for channel in range(153):
            indices = np.flatnonzero(known[batch, :, channel])
            for left, right in zip(indices[:-1], indices[1:]):
                if right - left <= 1:
                    continue
                u = np.arange(right - left + 1, dtype=np.float64) / (right - left)
                result[batch, left : right + 1, channel] = (64 * u**3 * (1 - u) ** 3).astype(np.float32)
    result[known] = 0
    return result[0] if single else result


def build(packet):
    """Replace boundary-only context requests with the strongest shape control.

    Requests containing interior full/partial priorities retain their established
    per-channel linear/SLERP reference until a general shape-preserving keyed
    curve is independently qualified. Hidden labels are never consulted.
    """
    request = packet["request"]
    baseline = np.array(request["baseline"], copy=True).reshape(len(request["times"]), 153)
    mask = request["mask"].reshape(len(request["times"]), 153)
    context = bool(packet["observations"].context)
    boundary_rows = {0, len(mask) - 1}
    if context:
        boundary_rows |= {1, len(mask) - 2}
    interior_known = any(np.any(mask[index]) for index in range(len(mask)) if index not in boundary_rows)
    if not interior_known:
        gap = len(mask) - 1 - 2 * int(context)
        query = np.arange(gap + 1, dtype=np.float64) / gap
        shaped = shape_reference(packet["observations"], query)
        if context:
            baseline[1:-1] = shaped
        else:
            baseline[:] = shaped
        observed = request["observed"].reshape(len(mask), 153)
        baseline[mask] = observed[mask]
    condition = np.array(request["condition"], copy=True)
    condition[:, :153] = baseline
    baseline = baseline.astype(np.float32)
    condition = condition.astype(np.float32)
    baseline.setflags(write=False)
    condition.setflags(write=False)
    return {
        "condition": condition,
        "baseline": baseline,
        "target": np.asarray(packet["target"], dtype=np.float32).reshape(len(mask), 153),
        "mask": mask,
        "envelope": residual_envelope(mask),
        "used_shape_reference": not interior_known,
    }
