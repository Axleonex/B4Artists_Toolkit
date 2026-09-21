"""Evaluate a C2-constrained sequence residual without registering it at runtime.

SPDX-License-Identifier: GPL-2.0-or-later
Research only. The provider preserves authored semantic channels exactly.
"""
import hashlib

import numpy as np

from semantic_motion_data import baseline
from sequence_conditioning_v1 import restore_observations
from sequence_constrained_reference_v1 import build as constrained_reference
from sequence_numpy_v1 import forward
from sequence_shape_residual_provider_v1 import load_weights, observed_request
from temporal_data import rotation6, rotation_matrix, slerp


class Provider:
    def __init__(self, path, expected_sha256, *, seed=20260909):
        self.weights = load_weights(path, expected_sha256)
        self.seed = seed
        self._cache = None

    def predict_packed(self, observations, query_times):
        query_times = np.asarray(query_times, dtype=float)
        if (
            query_times.ndim != 1
            or not np.isfinite(query_times).all()
            or np.any((query_times < 0) | (query_times > 1))
        ):
            raise ValueError("Invalid query times")
        request, times = observed_request(observations)
        observed_count = 4 if observations.context else 2
        if np.array_equal(
            observations.positions[:observed_count],
            np.broadcast_to(observations.positions[0], observations.positions[:observed_count].shape),
        ) and np.array_equal(
            observations.rotations[:observed_count],
            np.broadcast_to(observations.rotations[0], observations.rotations[:observed_count].shape),
        ):
            return baseline(observations, query_times)

        prepared = constrained_reference(
            {
                "request": request,
                "observations": observations,
                # The reference builder exposes a target for training batches, but
                # inference does not use it. Supply an observed-only placeholder.
                "target": request["baseline"],
            }
        )
        digest = hashlib.sha256()
        for value in (
            prepared["condition"],
            prepared["baseline"],
            prepared["mask"],
            prepared["envelope"],
            request["times"],
        ):
            digest.update(value.tobytes())
        key = digest.hexdigest()
        if self._cache is None or self._cache[0] != key:
            raw = forward(
                self.weights,
                prepared["condition"][None],
                np.zeros((1, len(times), 153), dtype=np.float32),
                np.zeros(1, dtype=np.float32),
            )[0]
            residual = raw * prepared["envelope"]
            generated = (prepared["baseline"] + residual).reshape(len(times), 17, 9)
            packed = restore_observations(generated, request)
            rotations, bad = rotation_matrix(packed[..., 3:])
            if bad.any() or not np.isfinite(packed).all():
                raise ValueError("Generated pose is invalid")
            self._cache = (key, packed.copy(), rotations.copy())

        _, packed, rotations = self._cache
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
