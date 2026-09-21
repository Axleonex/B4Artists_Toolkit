"""Bridge a constrained sequence Transformer to the semantic benchmark.

SPDX-License-Identifier: GPL-2.0-or-later
Research only. No model is registered with the addon by this module.
"""
import hashlib
import zipfile
from pathlib import Path

import numpy as np

from semantic_motion_data import baseline
from sequence_conditioning_v1 import restore_observations
from sequence_constrained_reference_v1 import build as constrained_reference
from sequence_shape_residual_provider_v1 import observed_request
from sequence_transformer_numpy_v1 import forward, residual
from sequence_velocity_conditioning_v1 import augment
from temporal_data import rotation6, rotation_matrix, slerp


def load_weights(path, expected_sha256):
    path = Path(path)
    if path.stat().st_size > 5 * 1024**2:
        raise ValueError("Weight archive exceeds the fixed research limit")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError("Weight identity mismatch")
    shapes = {
        "input.weight": (128, 547),
        "input.bias": (128,),
        "norm.weight": (128,),
        "norm.bias": (128,),
        "output.weight": (154, 128),
        "output.bias": (154,),
    }
    for index in range(4):
        block = {
            "norm1.weight": (128,),
            "norm1.bias": (128,),
            "qkv.weight": (384, 128),
            "qkv.bias": (384,),
            "attention_output.weight": (128, 128),
            "attention_output.bias": (128,),
            "norm2.weight": (128,),
            "norm2.bias": (128,),
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
            {"request": request, "observations": observations, "target": request["baseline"]}
        )
        condition = augment(prepared["condition"])
        digest = hashlib.sha256()
        for value in (
            condition,
            prepared["baseline"],
            prepared["mask"],
            prepared["envelope"],
            request["times"],
        ):
            digest.update(value.tobytes())
        key = digest.hexdigest()
        if self._cache is None or self._cache[0] != key:
            raw = forward(self.weights, condition[None])
            correction = residual(raw, prepared["envelope"][None])[0]
            generated = (prepared["baseline"] + correction).reshape(len(times), 17, 9)
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
