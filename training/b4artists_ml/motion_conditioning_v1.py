"""Versioned contact, scene, intent and authored-control conditioning schema.

SPDX-License-Identifier: GPL-2.0-or-later
Unknown values are required to be zero so hidden labels cannot leak into model input.
"""
from dataclasses import dataclass, fields

import numpy as np


EFFECTORS = ("left_foot", "right_foot", "left_hand", "right_hand")
SCENE_PROBES = ("root", *EFFECTORS)
ACTIONS = (
    "walk", "run", "jump", "landing", "turn", "crouch", "reach_or_object",
    "recovery", "interaction", "aerial", "combat", "dance", "gesture", "other",
)
STYLES = (
    "locomotion", "jump", "dance", "combat", "sport", "acrobatics",
    "interaction", "gesture", "other",
)
PROVENANCE = ("unknown", "authored", "reviewed", "measured", "metadata", "heuristic", "model")
PROVENANCE_CODE = {name: index for index, name in enumerate(PROVENANCE)}


def _array(value, shape, dtype, name):
    result = np.asarray(value, dtype=dtype)
    if result.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if np.issubdtype(result.dtype, np.floating) and not np.isfinite(result).all():
        raise ValueError(f"{name} must be finite")
    return result


def _require_zero(values, unknown, name):
    if np.any(np.asarray(values)[unknown] != 0):
        raise ValueError(f"Unknown {name} values must be zero")


def _confidence(known, confidence, provenance, name):
    _require_zero(confidence, ~known, name + " confidence")
    _require_zero(provenance, ~known, name + " provenance")
    if np.any(known & ((confidence <= 0) | (confidence > 1))):
        raise ValueError(f"Known {name} confidence must lie in (0, 1]")
    if np.any(known & ((provenance <= 0) | (provenance >= len(PROVENANCE)))):
        raise ValueError(f"Known {name} provenance is invalid")
    if np.any((provenance == PROVENANCE_CODE["heuristic"]) & (confidence > 0.35)):
        raise ValueError(f"Heuristic {name} confidence cannot exceed 0.35")
    if np.any((provenance == PROVENANCE_CODE["metadata"]) & (confidence > 0.5)):
        raise ValueError(f"Metadata {name} confidence cannot exceed 0.5")


def _unit_when_known(vectors, known, name):
    norms = np.linalg.norm(vectors, axis=-1)
    if np.any(known & (np.abs(norms - 1) > 1e-5)):
        raise ValueError(f"Known {name} vectors must be unit length")
    _require_zero(vectors, ~known, name)


@dataclass(frozen=True)
class MotionConditioning:
    contact_probability: np.ndarray
    contact_known: np.ndarray
    contact_confidence: np.ndarray
    contact_provenance: np.ndarray
    support_point: np.ndarray
    support_normal: np.ndarray
    support_velocity: np.ndarray
    support_known: np.ndarray
    scene_signed_distance: np.ndarray
    scene_normal: np.ndarray
    scene_known: np.ndarray
    scene_confidence: np.ndarray
    scene_provenance: np.ndarray
    action_weight: np.ndarray
    action_known: np.ndarray
    action_confidence: np.ndarray
    action_provenance: np.ndarray
    style_weight: np.ndarray
    style_known: np.ndarray
    style_confidence: np.ndarray
    style_provenance: np.ndarray
    desired_root_velocity: np.ndarray
    desired_facing: np.ndarray
    trajectory_known: np.ndarray
    trajectory_confidence: np.ndarray
    trajectory_provenance: np.ndarray
    authored_root: np.ndarray
    authored_root_mask: np.ndarray
    authored_rotation6: np.ndarray
    authored_rotation_mask: np.ndarray

    @classmethod
    def empty(cls, frames, joints=23):
        if not isinstance(frames, int) or frames < 2 or joints != 23:
            raise ValueError("Invalid conditioning dimensions")
        z = np.zeros
        return cls(
            z((frames, len(EFFECTORS)), np.float32),
            z((frames, len(EFFECTORS)), bool),
            z((frames, len(EFFECTORS)), np.float32),
            z((frames, len(EFFECTORS)), np.uint8),
            z((frames, len(EFFECTORS), 3), np.float32),
            z((frames, len(EFFECTORS), 3), np.float32),
            z((frames, len(EFFECTORS), 3), np.float32),
            z((frames, len(EFFECTORS)), bool),
            z((frames, len(SCENE_PROBES)), np.float32),
            z((frames, len(SCENE_PROBES), 3), np.float32),
            z((frames, len(SCENE_PROBES)), bool),
            z((frames, len(SCENE_PROBES)), np.float32),
            z((frames, len(SCENE_PROBES)), np.uint8),
            z((frames, len(ACTIONS)), np.float32),
            z((frames,), bool),
            z((frames,), np.float32),
            z((frames,), np.uint8),
            z((frames, len(STYLES)), np.float32),
            z((frames,), bool),
            z((frames,), np.float32),
            z((frames,), np.uint8),
            z((frames, 3), np.float32),
            z((frames, 3), np.float32),
            z((frames,), bool),
            z((frames,), np.float32),
            z((frames,), np.uint8),
            z((frames, 3), np.float32),
            z((frames, 3), bool),
            z((frames, joints, 6), np.float32),
            z((frames, joints, 6), bool),
        )

    @property
    def frames(self):
        return len(self.action_known)

    @property
    def joints(self):
        return self.authored_rotation6.shape[1]

    def validated(self):
        t, j = self.frames, self.joints
        if t < 2 or j != 23:
            raise ValueError("Motion conditioning v1 requires at least two frames and 23 joints")
        shapes = {
            "contact_probability": (t, len(EFFECTORS)),
            "contact_known": (t, len(EFFECTORS)),
            "contact_confidence": (t, len(EFFECTORS)),
            "contact_provenance": (t, len(EFFECTORS)),
            "support_point": (t, len(EFFECTORS), 3),
            "support_normal": (t, len(EFFECTORS), 3),
            "support_velocity": (t, len(EFFECTORS), 3),
            "support_known": (t, len(EFFECTORS)),
            "scene_signed_distance": (t, len(SCENE_PROBES)),
            "scene_normal": (t, len(SCENE_PROBES), 3),
            "scene_known": (t, len(SCENE_PROBES)),
            "scene_confidence": (t, len(SCENE_PROBES)),
            "scene_provenance": (t, len(SCENE_PROBES)),
            "action_weight": (t, len(ACTIONS)),
            "action_known": (t,),
            "action_confidence": (t,),
            "action_provenance": (t,),
            "style_weight": (t, len(STYLES)),
            "style_known": (t,),
            "style_confidence": (t,),
            "style_provenance": (t,),
            "desired_root_velocity": (t, 3),
            "desired_facing": (t, 3),
            "trajectory_known": (t,),
            "trajectory_confidence": (t,),
            "trajectory_provenance": (t,),
            "authored_root": (t, 3),
            "authored_root_mask": (t, 3),
            "authored_rotation6": (t, j, 6),
            "authored_rotation_mask": (t, j, 6),
        }
        bool_names = {
            "contact_known", "support_known", "scene_known", "action_known", "style_known",
            "trajectory_known", "authored_root_mask", "authored_rotation_mask",
        }
        code_names = {
            "contact_provenance", "scene_provenance", "action_provenance",
            "style_provenance", "trajectory_provenance",
        }
        values = {}
        for item in fields(self):
            dtype = bool if item.name in bool_names else np.uint8 if item.name in code_names else np.float32
            values[item.name] = _array(getattr(self, item.name), shapes[item.name], dtype, item.name)
        if np.any((values["contact_probability"] < 0) | (values["contact_probability"] > 1)):
            raise ValueError("Contact probabilities must lie in [0, 1]")
        _require_zero(values["contact_probability"], ~values["contact_known"], "contact")
        _confidence(values["contact_known"], values["contact_confidence"], values["contact_provenance"], "contact")
        for name in ("support_point", "support_normal", "support_velocity"):
            _require_zero(values[name], ~values["support_known"], name)
        _unit_when_known(values["support_normal"], values["support_known"], "support normal")
        if np.any(values["support_known"] & ~values["contact_known"]):
            raise ValueError("Support geometry requires known contact state")
        _require_zero(values["scene_signed_distance"], ~values["scene_known"], "scene distance")
        _unit_when_known(values["scene_normal"], values["scene_known"], "scene normal")
        _confidence(values["scene_known"], values["scene_confidence"], values["scene_provenance"], "scene")
        for prefix in ("action", "style"):
            known = values[prefix + "_known"]
            weight = values[prefix + "_weight"]
            _require_zero(weight, ~known, prefix)
            if np.any(known & (np.abs(weight.sum(axis=-1) - 1) > 1e-5)) or np.any(weight < 0):
                raise ValueError(f"Known {prefix} weights must be a probability distribution")
            _confidence(known, values[prefix + "_confidence"], values[prefix + "_provenance"], prefix)
        for name in ("desired_root_velocity", "desired_facing"):
            _require_zero(values[name], ~values["trajectory_known"], name)
        _unit_when_known(values["desired_facing"], values["trajectory_known"], "desired facing")
        _confidence(
            values["trajectory_known"],
            values["trajectory_confidence"],
            values["trajectory_provenance"],
            "trajectory",
        )
        _require_zero(values["authored_root"], ~values["authored_root_mask"], "authored root")
        _require_zero(values["authored_rotation6"], ~values["authored_rotation_mask"], "authored rotation")
        complete_rotation_masks = values["authored_rotation_mask"].all(axis=-1) | ~values["authored_rotation_mask"].any(axis=-1)
        if not complete_rotation_masks.all():
            raise ValueError("A local rotation must expose all six coordinates or none")
        return MotionConditioning(**values)

    def packed(self):
        value = self.validated()
        t = value.frames
        provenance_eye = np.eye(len(PROVENANCE), dtype=np.float32)
        blocks = []
        layout = {}

        def add(name, array):
            flat = np.asarray(array, dtype=np.float32).reshape(t, -1)
            start = sum(block.shape[1] for block in blocks)
            blocks.append(flat)
            layout[name] = [start, start + flat.shape[1]]

        def provenance_one_hot(codes):
            result = provenance_eye[codes]
            return result * (np.asarray(codes) != PROVENANCE_CODE["unknown"])[..., None]

        for name in (
            "contact_probability", "contact_known", "contact_confidence", "support_point",
            "support_normal", "support_velocity", "support_known", "scene_signed_distance",
            "scene_normal", "scene_known", "scene_confidence", "action_weight", "action_known",
            "action_confidence", "style_weight", "style_known", "style_confidence",
            "desired_root_velocity", "desired_facing", "trajectory_known", "trajectory_confidence",
            "authored_root", "authored_root_mask", "authored_rotation6", "authored_rotation_mask",
        ):
            add(name, getattr(value, name))
        add("contact_provenance_one_hot", provenance_one_hot(value.contact_provenance))
        add("scene_provenance_one_hot", provenance_one_hot(value.scene_provenance))
        add("action_provenance_one_hot", provenance_one_hot(value.action_provenance))
        add("style_provenance_one_hot", provenance_one_hot(value.style_provenance))
        add("trajectory_provenance_one_hot", provenance_one_hot(value.trajectory_provenance))
        packed = np.concatenate(blocks, axis=-1)
        if not np.isfinite(packed).all():
            raise ValueError("Nonfinite packed conditioning")
        return packed, layout


def with_hierarchy_controls(conditioning, window):
    """Copy exact normalized authored values from a full-hierarchy window."""
    base = conditioning.validated()
    root_mask = np.asarray(window["masks"]["root"], dtype=bool)
    rotation_mask = np.asarray(window["masks"]["rotation"], dtype=bool)
    core = np.asarray(window["state"], dtype=np.float32)
    pad = (len(core) - len(root_mask)) // 2
    core = core[pad : pad + len(root_mask)]
    roots = np.where(root_mask, core[:, :3], 0)
    rotations = core[:, 3:].reshape(len(core), base.joints, 6)
    rotations = np.where(rotation_mask, rotations, 0)
    data = {item.name: getattr(base, item.name) for item in fields(base)}
    data.update(
        authored_root=roots,
        authored_root_mask=root_mask,
        authored_rotation6=rotations,
        authored_rotation_mask=rotation_mask,
    )
    return MotionConditioning(**data).validated()
