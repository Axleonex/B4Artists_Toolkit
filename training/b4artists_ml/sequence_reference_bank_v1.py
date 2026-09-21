"""Train-only procedural reference bank over the expanded sequence store.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np

from kinematic_trajectory_v20 import predict_packed as control_predict
from sequence_constrained_reference_v1 import build as constrained_reference
from sequence_packet_v2 import packet
from sequence_velocity_conditioning_v1 import augment


REFERENCE_NAMES = ("linear", "hermite", "shape")
CONDITION = 853


def build(row):
    prepared = constrained_reference(row)
    request = row["request"]
    times = request["times"]
    mask = request["mask"].reshape(len(times), 153)
    observed = request["observed"].reshape(len(times), 153)
    linear = np.asarray(request["baseline"], dtype=np.float32).reshape(len(times), 153).copy()
    shape = np.asarray(prepared["baseline"], dtype=np.float32).copy()
    hermite = linear.copy()
    context = bool(row["observations"].context)
    boundary = {0, len(mask) - 1}
    if context:
        boundary |= {1, len(mask) - 2}
    interior_known = any(np.any(mask[index]) for index in range(len(mask)) if index not in boundary)
    if not interior_known:
        gap = len(times) - 1 - 2 * int(context)
        query = np.arange(gap + 1, dtype=np.float64) / gap
        value = control_predict(
            {"kind": "baseline", "baseline": "hermite"}, row["observations"], query
        ).astype(np.float32)
        if context:
            hermite[1:-1] = value
        else:
            hermite[:] = value
    for reference in (linear, hermite, shape):
        reference[mask] = observed[mask]
    references = np.stack((linear, hermite, shape), axis=1)
    condition = np.concatenate(
        (
            augment(prepared["condition"]),
            linear - shape,
            hermite - shape,
        ),
        axis=-1,
    ).astype(np.float32)
    if condition.shape != (len(times), CONDITION) or references.shape != (len(times), 3, 153):
        raise ValueError("Invalid reference-bank shape")
    if not np.isfinite(condition).all() or not np.isfinite(references).all():
        raise ValueError("Nonfinite reference bank")
    for value in (condition, references):
        value.setflags(write=False)
    return {
        "condition": condition,
        "references": references,
        "target": prepared["target"],
        "mask": mask,
        "envelope": prepared["envelope"],
        "used_distinct_references": not interior_known,
    }


class ReferenceBankSampler:
    def __init__(self, store):
        self.store = store

    def sample_batch(self, batch_size, *, gap, context, seed):
        if not isinstance(batch_size, int) or not 1 <= batch_size <= 256:
            raise ValueError("Invalid batch size")
        if gap not in (8, 16, 32, 64, 96) or not isinstance(context, bool):
            raise ValueError("Unsupported request")
        eligible = {
            subject: [
                index
                for index in self.store.by_subject[subject]
                if self.store.entries[index]["frames"] >= gap + (3 if context else 1)
            ]
            for subject in self.store.subjects
        }
        subjects = [subject for subject, indices in eligible.items() if indices]
        if not subjects:
            raise ValueError("No eligible training windows")
        rng = np.random.default_rng(seed)
        packets = []
        identities = []
        for item in range(batch_size):
            subject = subjects[int(rng.integers(len(subjects)))]
            clip_index = eligible[subject][int(rng.integers(len(eligible[subject])))]
            sequence = self.store.clip(clip_index)
            low = 1 if context else 0
            high = len(sequence.positions) - gap - (1 if context else 0)
            start = int(rng.integers(low, high))
            pattern = item % 3
            packets.append(packet(sequence, start, start + gap, context=context, pattern=pattern))
            identities.append(
                {
                    "clip": self.store.entries[clip_index]["clip"],
                    "subject": subject,
                    "start": start,
                    "gap": gap,
                    "context": context,
                    "pattern": pattern,
                }
            )
        prepared = [build(row) for row in packets]
        return {
            "condition": np.stack([row["condition"] for row in prepared]),
            "references": np.stack([row["references"] for row in prepared]),
            "target": np.stack([row["target"] for row in prepared]),
            "mask": np.stack([row["mask"] for row in prepared]),
            "envelope": np.stack([row["envelope"] for row in prepared]),
            "dt": np.asarray([row["observations"].dt for row in packets], dtype=np.float32),
            "identities": identities,
        }

