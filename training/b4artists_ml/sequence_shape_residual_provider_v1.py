"""Bridge a shape-residual sequence fit to the protected semantic benchmark.

SPDX-License-Identifier: GPL-2.0-or-later
Research only. No model is registered with the addon by this module.
"""
import hashlib
import zipfile
from pathlib import Path

import numpy as np

from semantic_motion_data import baseline
from sequence_conditioning_v1 import restore_observations
from sequence_numpy_v1 import forward
from sequence_shape_conditioning_v1 import build
from temporal_data import rotation6, rotation_matrix, slerp


def load_weights(path, expected_sha256):
    path = Path(path)
    if path.stat().st_size > 5 * 1024**2:
        raise ValueError("Weight archive exceeds the fixed research limit")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError("Weight identity mismatch")
    shapes = {
        "input.weight": (128, 563),
        "input.bias": (128,),
        "norm.weight": (128,),
        "norm.bias": (128,),
        "output.weight": (153, 128),
        "output.bias": (153,),
    }
    for index in range(6):
        block = {
            "norm.weight": (128,),
            "norm.bias": (128,),
            "conv.weight": (128, 128, 3),
            "conv.bias": (128,),
            "ff1.weight": (256, 128),
            "ff1.bias": (256,),
            "ff2.weight": (128, 256),
            "ff2.bias": (128,),
        }
        shapes.update({f"blocks.{index}.{name}": shape for name, shape in block.items()})
    with zipfile.ZipFile(path) as archive:
        if len(archive.infolist()) != len(shapes):
            raise ValueError("Unexpected weight archive")
        if sum(item.file_size for item in archive.infolist()) > 5 * 1024**2:
            raise ValueError("Expanded weight archive exceeds the fixed research limit")
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != set(shapes):
            raise ValueError("Unexpected parameter set")
        weights = {name: archive[name] for name in archive.files}
    for name, value in weights.items():
        if value.dtype != np.float32 or value.shape != shapes[name] or not np.isfinite(value).all():
            raise ValueError("Invalid parameter: " + name)
        value.setflags(write=False)
    return weights


def observed_request(observations):
    duration = float(observations.duration)
    dt = float(observations.dt)
    if (
        observations.schema != "b4ml-semantic-observations-v1"
        or not np.isfinite([duration, dt]).all()
        or dt <= 0
        or duration < dt
        or not isinstance(observations.context, (bool, np.bool_))
    ):
        raise ValueError("Unsupported observations")
    ratio = duration / dt
    if ratio > 127:
        raise ValueError("Sequence length exceeds model budget")
    interior = np.arange(1, int(np.floor(ratio)) + 1) * dt
    interior = interior[interior < duration - 1e-9 * dt]
    times = np.r_[0.0, interior, duration]
    if observations.context:
        times = np.r_[-dt, times, duration + dt]
    if len(times) > 128:
        raise ValueError("Sequence context exceeds model budget")
    known = np.zeros((len(times), 17, 9))
    mask = np.zeros((len(times), 17, 2), dtype=bool)
    locations = [(1 if observations.context else 0, 0), (-2 if observations.context else -1, 1)]
    if observations.context:
        locations += [(0, 2), (-1, 3)]
    for index, source in locations:
        known[index] = np.concatenate(
            (observations.positions[source], rotation6(observations.rotations[source])), axis=-1
        )
        mask[index] = True
    return build(times, known, mask, observations.rest)["request"], times


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
        digest = hashlib.sha256()
        for name in ("condition", "observed", "mask", "times"):
            digest.update(request[name].tobytes())
        key = digest.hexdigest()
        if self._cache is None or self._cache[0] != key:
            condition = request["condition"][None]
            residual = forward(
                self.weights,
                condition,
                np.zeros((1, len(times), 153), dtype=np.float32),
                np.zeros(1, dtype=np.float32),
            )
            packed = restore_observations(
                request["baseline"] + residual[0].reshape(len(times), 17, 9), request
            )
            rotations, bad = rotation_matrix(packed[..., 3:])
            if bad.any():
                raise ValueError("Generated rotation is degenerate")
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
