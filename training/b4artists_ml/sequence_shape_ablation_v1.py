"""Exact procedural ablation for the observed-only shape-residual provider.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np

from sequence_shape_residual_provider_v1 import observed_request
from temporal_data import rotation6, rotation_matrix, slerp


def predict_packed(observations, query_times):
    query_times = np.asarray(query_times, dtype=float)
    if (
        query_times.ndim != 1
        or not np.isfinite(query_times).all()
        or np.any((query_times < 0) | (query_times > 1))
    ):
        raise ValueError("Invalid query times")
    request, times = observed_request(observations)
    packed = request["baseline"].reshape(len(times), 17, 9)
    rotations, bad = rotation_matrix(packed[..., 3:])
    if bad.any():
        raise ValueError("Procedural rotation is degenerate")
    query = query_times * observations.duration
    points = np.empty((len(query_times), 17, 3))
    angles = np.empty((len(query_times), 17, 3, 3))
    for joint in range(17):
        for axis in range(3):
            points[:, joint, axis] = np.interp(query, times, packed[:, joint, axis])
    indices = np.clip(np.searchsorted(times, query, side="right") - 1, 0, len(times) - 2)
    for index in np.unique(indices):
        rows = np.flatnonzero(indices == index)
        blend = (query[rows] - times[index]) / (times[index + 1] - times[index])
        angles[rows] = slerp(rotations[index], rotations[index + 1], blend)
    result = np.concatenate((points, rotation6(angles)), axis=-1).reshape(len(query_times), 153)
    anchors = np.concatenate(
        (observations.positions[:2], rotation6(observations.rotations[:2])), axis=-1
    ).reshape(2, 153)
    result[query_times == 0] = anchors[0]
    result[query_times == 1] = anchors[1]
    return result
