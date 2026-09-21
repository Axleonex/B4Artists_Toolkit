"""Memory-mapped, subject-balanced access to the expanded train-only corpus.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from collections import OrderedDict
from pathlib import Path
import hashlib
import json

import numpy as np

from semantic_motion_data import SemanticSequence
from sequence_packet_v2 import packet
STYLE_NAMES = (
    "locomotion",
    "jump",
    "dance",
    "combat",
    "sport",
    "acrobatics",
    "interaction",
    "gesture",
    "other",
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SequenceStore:
    def __init__(self, root=None, *, verify_hashes=False, cache_clips=8):
        if not isinstance(cache_clips, int) or not 1 <= cache_clips <= 64:
            raise ValueError("cache_clips must be in [1, 64]")
        self.root = Path(root or Path(__file__).resolve().parent).resolve()
        result = self.root / "results/cmu-sequence-store-v2"
        self.report = json.loads((result / "report.json").read_text())
        self.layout = json.loads((result / "layout.json").read_text())
        matrix_result = self.root / "results/rotation-matrix-store-v1"
        self.matrix_report = json.loads((matrix_result / "report.json").read_text())
        if not self.report["complete"] or self.report["validation_read"] or self.report["confirmation_read"]:
            raise ValueError("Sequence-store qualification is invalid")
        if not self.matrix_report["complete"] or self.matrix_report["validation_read"] or self.matrix_report["confirmation_read"]:
            raise ValueError("Rotation-matrix store qualification is invalid")
        if self.matrix_report["source_report_sha256"] != _sha256(result / "report.json"):
            raise ValueError("Rotation-matrix source identity mismatch")
        if _sha256(result / "layout.json") != self.report["layout_sha256"]:
            raise ValueError("Sequence layout identity mismatch")
        store = self.root / "cache-expanded-v1/sequence-store-v2"
        self.positions = np.load(store / "positions.npy", mmap_mode="r", allow_pickle=False)
        self.rest_positions = np.load(store / "rest_positions.npy", mmap_mode="r", allow_pickle=False)
        matrix_store = self.root / "cache-expanded-v1/rotation-matrix-store-v1"
        self.rotations = np.load(matrix_store / "rotation_matrices.npy", mmap_mode="r", allow_pickle=False)
        self.rest_rotations = np.load(matrix_store / "rest_rotation_matrices.npy", mmap_mode="r", allow_pickle=False)
        arrays = {
            "positions.npy": self.positions,
            "rest_positions.npy": self.rest_positions,
        }
        expected_shapes = {
            "positions.npy": tuple(self.layout["position_shape"]),
            "rest_positions.npy": (self.layout["clips"], 17, 3),
        }
        for name, value in arrays.items():
            if value.dtype != np.float32 or value.shape != expected_shapes[name]:
                raise ValueError("Unexpected store array: " + name)
            path = store / name
            if path.stat().st_size != self.report["files"][name]["bytes"]:
                raise ValueError("Unexpected store byte size: " + name)
            if verify_hashes and _sha256(path) != self.report["files"][name]["sha256"]:
                raise ValueError("Store checksum mismatch: " + name)
        matrix_arrays = {
            "rotation_matrices.npy": self.rotations,
            "rest_rotation_matrices.npy": self.rest_rotations,
        }
        matrix_shapes = {
            "rotation_matrices.npy": (self.layout["frames"], 17, 3, 3),
            "rest_rotation_matrices.npy": (self.layout["clips"], 17, 3, 3),
        }
        for name, value in matrix_arrays.items():
            if value.dtype != np.float32 or value.shape != matrix_shapes[name]:
                raise ValueError("Unexpected matrix store array: " + name)
            path = matrix_store / name
            if path.stat().st_size != self.matrix_report["files"][name]["bytes"]:
                raise ValueError("Unexpected matrix store byte size: " + name)
            if verify_hashes and _sha256(path) != self.matrix_report["files"][name]["sha256"]:
                raise ValueError("Matrix store checksum mismatch: " + name)
        self.entries = self.layout["entries"]
        self.index_by_clip = {row["clip"]: index for index, row in enumerate(self.entries)}
        self.subjects = sorted({row["subject"] for row in self.entries})
        self.by_subject = {
            subject: [index for index, row in enumerate(self.entries) if row["subject"] == subject]
            for subject in self.subjects
        }
        self.cache_clips = cache_clips
        self._cache = OrderedDict()

    def clip(self, index):
        if not isinstance(index, (int, np.integer)) or not 0 <= int(index) < len(self.entries):
            raise ValueError("Invalid clip index")
        index = int(index)
        if index in self._cache:
            value = self._cache.pop(index)
            self._cache[index] = value
            return value
        row = self.entries[index]
        start = row["offset"]
        end = start + row["frames"]
        value = SemanticSequence(
            np.asarray(self.rest_positions[index]),
            self.rest_rotations[index],
            self.positions[start:end],
            self.rotations[start:end],
            np.arange(row["frames"], dtype=np.int64),
            row["dt"],
        )
        self._cache[index] = value
        while len(self._cache) > self.cache_clips:
            self._cache.popitem(last=False)
        return value

    def style(self, index):
        tags = set(self.entries[index]["style_tags"])
        return np.asarray([name in tags for name in STYLE_NAMES], dtype=np.float32)

    def sample_batch(self, batch_size, *, gap, context, seed, constrained=False):
        if not isinstance(batch_size, int) or not 1 <= batch_size <= 256:
            raise ValueError("Invalid batch size")
        if gap not in (8, 16, 32, 64, 96):
            raise ValueError("Unsupported gap")
        if not isinstance(context, bool):
            raise ValueError("Explicit context flag required")
        if not isinstance(constrained, bool):
            raise ValueError("Explicit constrained flag required")
        eligible = {
            subject: [
                index
                for index in self.by_subject[subject]
                if self.entries[index]["frames"] >= gap + (3 if context else 1)
            ]
            for subject in self.subjects
        }
        subjects = [subject for subject, indices in eligible.items() if indices]
        if not subjects:
            raise ValueError("No eligible training windows")
        rng = np.random.default_rng(seed)
        rows = []
        identities = []
        for item in range(batch_size):
            subject = subjects[int(rng.integers(len(subjects)))]
            clip_index = eligible[subject][int(rng.integers(len(eligible[subject])))]
            sequence = self.clip(clip_index)
            low = 1 if context else 0
            high = len(sequence.positions) - gap - (1 if context else 0)
            start = int(rng.integers(low, high))
            pattern = item % 3
            rows.append(packet(sequence, start, start + gap, context=context, pattern=pattern))
            identities.append(
                {
                    "clip": self.entries[clip_index]["clip"],
                    "subject": subject,
                    "start": start,
                    "gap": gap,
                    "context": context,
                    "pattern": pattern,
                }
            )
        if constrained:
            from sequence_constrained_reference_v1 import build as constrained_reference
            prepared = [constrained_reference(row) for row in rows]
        else:
            prepared = [
                {
                    "condition": row["request"]["condition"],
                    "baseline": row["request"]["baseline"].reshape(len(row["request"]["times"]), 153),
                    "target": row["target"].reshape(len(row["target"]), 153).astype(np.float32),
                    "mask": row["request"]["mask"].reshape(len(row["request"]["times"]), 153),
                }
                for row in rows
            ]
        return {
            "condition": np.stack([row["condition"] for row in prepared]),
            "baseline": np.stack([row["baseline"] for row in prepared]),
            "target": np.stack([row["target"] for row in prepared]),
            "mask": np.stack([row["mask"] for row in prepared]),
            "envelope": np.stack([row["envelope"] for row in prepared]) if constrained else None,
            "dt": np.asarray([row["observations"].dt for row in rows], dtype=np.float32),
            "style": np.stack([self.style(self.index_by_clip[identity["clip"]]) for identity in identities]),
            "identities": identities,
        }
