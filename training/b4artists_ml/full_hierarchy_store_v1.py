"""Memory-mapped full-hierarchy motion access for train-only research.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

import numpy as np

from temporal_data import quat_matrix, rotation6


SEMANTIC_GROUPS = {
    "upper_body": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    "feet": (13, 16),
    "lower_body": (11, 12, 13, 14, 15, 16),
    "extremities": (4, 7, 10, 13, 16),
}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _angular_velocity(quaternions, dt):
    """Return joint-local angular velocity vectors without Euler conversion."""
    q = np.asarray(quaternions, dtype=np.float64)
    if q.ndim != 3 or q.shape[-1] != 4 or len(q) < 2 or not np.isfinite(q).all():
        raise ValueError("Expected at least two frames of finite joint quaternions")
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("Positive frame interval required")
    a = q[:-1]
    b = q[1:]
    aw, av = a[..., :1], a[..., 1:]
    bw, bv = b[..., :1], b[..., 1:]
    delta = np.concatenate(
        (
            aw * bw + np.sum(av * bv, axis=-1, keepdims=True),
            aw * bv - bw * av - np.cross(av, bv),
        ),
        axis=-1,
    )
    delta = np.where(delta[..., :1] < 0, -delta, delta)
    vector = delta[..., 1:]
    magnitude = np.linalg.norm(vector, axis=-1, keepdims=True)
    angle = 2 * np.arctan2(magnitude, np.clip(delta[..., :1], 0, 1))
    step = vector / np.maximum(magnitude, 1e-12) * angle / dt
    step = np.where(magnitude < 1e-10, 2 * vector / dt, step)
    result = np.empty((len(q), q.shape[1], 3), dtype=np.float64)
    result[0] = step[0]
    result[-1] = step[-1]
    if len(q) > 2:
        result[1:-1] = (step[:-1] + step[1:]) * 0.5
    return result


def authored_masks(frames, semantic, pattern):
    """Create explicit sparse-control masks; intermediate helper joints stay hidden."""
    if not isinstance(frames, int) or frames < 2:
        raise ValueError("At least two frames required")
    if pattern not in ("endpoints", "upper_mid", "foot_contacts", "extremity_mid"):
        raise ValueError("Unknown authored-mask pattern")
    semantic = tuple(int(value) for value in semantic)
    root = np.zeros((frames, 3), dtype=bool)
    rotation = np.zeros((frames, max(semantic) + 1, 6), dtype=bool)
    root[[0, -1]] = True
    rotation[0, semantic] = True
    rotation[-1, semantic] = True
    middle = frames // 2
    if pattern == "upper_mid":
        rotation[middle, [semantic[index] for index in SEMANTIC_GROUPS["upper_body"]]] = True
    elif pattern == "foot_contacts":
        for frame, side in ((frames // 4, 13), ((3 * frames) // 4, 16)):
            rotation[frame, semantic[side]] = True
    elif pattern == "extremity_mid":
        root[middle] = True
        rotation[middle, [semantic[index] for index in SEMANTIC_GROUPS["extremities"]]] = True
    return {"root": root, "rotation": rotation, "pattern": pattern}


@dataclass(frozen=True)
class HierarchyClip:
    root_positions: np.ndarray
    local_quaternions: np.ndarray
    offsets: np.ndarray
    reference: np.ndarray
    rest_pelvis_rotation: np.ndarray
    scale: float
    dt: float
    names: tuple
    parents: tuple
    semantic: tuple

    def normalized_window(self, start, end, *, context=False, mask_pattern="endpoints"):
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end < len(self.root_positions):
            raise ValueError("Invalid hierarchy window")
        pad = int(bool(context))
        if start - pad < 0 or end + pad >= len(self.root_positions):
            raise ValueError("Requested context is unavailable")
        indices = np.arange(start - pad, end + pad + 1)
        q = np.asarray(self.local_quaternions[indices], dtype=np.float64)
        matrices = quat_matrix(q)
        anchor = pad
        basis = matrices[anchor, 0] @ self.rest_pelvis_rotation.T @ self.reference
        roots = (
            np.asarray(self.root_positions[indices], dtype=np.float64) - self.root_positions[start]
        ) @ basis / self.scale
        local = matrices.copy()
        local[:, 0] = np.einsum("ij,fjk->fik", basis.T, local[:, 0])
        state = np.concatenate((roots, rotation6(local).reshape(len(indices), -1)), axis=-1)
        root_velocity = np.gradient(roots, self.dt, axis=0, edge_order=1)
        angular_velocity = _angular_velocity(q, self.dt)
        masks = authored_masks(end - start + 1, self.semantic, mask_pattern)
        if not all(np.isfinite(value).all() for value in (state, root_velocity, angular_velocity)):
            raise ValueError("Nonfinite normalized hierarchy window")
        return {
            "indices": indices,
            "state": state,
            "root_velocity": root_velocity,
            "angular_velocity": angular_velocity,
            "offsets": np.asarray(self.offsets, dtype=np.float64),
            "basis": basis,
            "origin": np.asarray(self.root_positions[start], dtype=np.float64),
            "masks": masks,
            "context": bool(context),
        }


class FullHierarchyStore:
    def __init__(self, root=None, *, verify_hashes=False):
        self.root = Path(root or Path(__file__).resolve().parent).resolve()
        result = self.root / "results/full-hierarchy-store-v1"
        cache = self.root / "cache-expanded-v1/full-hierarchy-store-v1"
        self.report = json.loads((result / "report.json").read_text())
        self.layout = json.loads((result / "layout.json").read_text())
        if not self.report["complete"] or self.report["validation_read"] or self.report["confirmation_read"]:
            raise ValueError("Full-hierarchy store qualification is invalid")
        if _sha256(result / "layout.json") != self.report["layout_sha256"]:
            raise ValueError("Full-hierarchy layout identity mismatch")
        self.root_positions = np.load(cache / "root_positions.npy", mmap_mode="r", allow_pickle=False)
        self.local_quaternions = np.load(cache / "local_quaternions.npy", mmap_mode="r", allow_pickle=False)
        self.offsets = np.load(cache / "offsets.npy", mmap_mode="r", allow_pickle=False)
        self.references = np.load(cache / "references.npy", mmap_mode="r", allow_pickle=False)
        self.rest_pelvis_rotations = np.load(
            cache / "rest_pelvis_rotations.npy", mmap_mode="r", allow_pickle=False
        )
        self.scales = np.load(cache / "scales.npy", mmap_mode="r", allow_pickle=False)
        arrays = {
            "root_positions.npy": (self.root_positions, np.float32, tuple(self.layout["root_position_shape"])),
            "local_quaternions.npy": (self.local_quaternions, np.float32, tuple(self.layout["local_quaternion_shape"])),
            "offsets.npy": (self.offsets, np.float32, (self.layout["clips"], self.layout["joints"], 3)),
            "references.npy": (self.references, np.float64, (self.layout["clips"], 3, 3)),
            "rest_pelvis_rotations.npy": (self.rest_pelvis_rotations, np.float64, (self.layout["clips"], 3, 3)),
            "scales.npy": (self.scales, np.float64, (self.layout["clips"],)),
        }
        for name, (value, dtype, shape) in arrays.items():
            if not isinstance(value, np.memmap) or value.dtype != dtype or value.shape != shape:
                raise ValueError("Unexpected full-hierarchy array: " + name)
            path = cache / name
            if path.stat().st_size != self.report["files"][name]["bytes"]:
                raise ValueError("Unexpected full-hierarchy byte size: " + name)
            if verify_hashes and _sha256(path) != self.report["files"][name]["sha256"]:
                raise ValueError("Full-hierarchy checksum mismatch: " + name)
        self.entries = self.layout["entries"]
        self.names = tuple(self.layout["names"])
        self.parents = tuple(self.layout["parents"])
        self.semantic = tuple(self.layout["semantic"])

    def clip(self, index):
        if not isinstance(index, (int, np.integer)) or not 0 <= int(index) < len(self.entries):
            raise ValueError("Invalid clip index")
        index = int(index)
        row = self.entries[index]
        start = row["offset"]
        end = start + row["frames"]
        return HierarchyClip(
            self.root_positions[start:end],
            self.local_quaternions[start:end],
            self.offsets[index],
            self.references[index],
            self.rest_pelvis_rotations[index],
            float(self.scales[index]),
            float(row["dt"]),
            self.names,
            self.parents,
            self.semantic,
        )
