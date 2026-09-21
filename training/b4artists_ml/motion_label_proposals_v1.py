"""Weak motion-label proposals for review and train-only experiments.

SPDX-License-Identifier: GPL-2.0-or-later

These signals come from motion geometry alone.  They are never force-plate,
scene, or animator ground truth.  All emitted confidence is capped at the
heuristic ceiling defined by :mod:`motion_conditioning_v1`.
"""
from dataclasses import dataclass

import numpy as np

from motion_conditioning_v1 import PROVENANCE_CODE
from sequence_kinematics import forward
from temporal_data import quat_matrix, rotation6


HEURISTIC_CONFIDENCE_CEILING = 0.35
FOOT_SEMANTIC_SLOTS = (13, 16)
FOOT_NAMES = ("left_foot", "right_foot")


def _finite(value, name):
    result = np.asarray(value, dtype=np.float64)
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must be finite")
    return result


def _smooth_transition(value, lower, upper):
    """Return zero at/below lower and one at/above upper."""
    if not np.isfinite([lower, upper]).all() or not lower < upper:
        raise ValueError("A finite increasing transition interval is required")
    x = np.clip((_finite(value, "transition value") - lower) / (upper - lower), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _runs(mask):
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 1:
        raise ValueError("Run mask must be one-dimensional")
    padded = np.r_[False, mask, False].astype(np.int8)
    edges = np.flatnonzero(np.diff(padded))
    return [(int(start), int(end - 1)) for start, end in edges.reshape(-1, 2)]


def _remove_short_true(mask, minimum_frames):
    if not isinstance(minimum_frames, int) or minimum_frames < 1:
        raise ValueError("minimum_frames must be a positive integer")
    result = np.asarray(mask, dtype=bool).copy()
    for start, end in _runs(result):
        if end - start + 1 < minimum_frames:
            result[start : end + 1] = False
    return result


def _hysteresis(probability, on, off, minimum_frames):
    """Turn on at ``on`` and remain on until probability reaches ``off``."""
    probability = _finite(probability, "contact probability")
    if probability.ndim != 1 or np.any((probability < 0) | (probability > 1)):
        raise ValueError("Contact probability must be a one-dimensional [0, 1] array")
    if not 0 <= off < on <= 1:
        raise ValueError("Hysteresis thresholds must satisfy 0 <= off < on <= 1")
    active = False
    result = np.zeros(len(probability), dtype=bool)
    for index, value in enumerate(probability):
        if active:
            active = value > off
        else:
            active = value >= on
        result[index] = active
    return _remove_short_true(result, minimum_frames)


@dataclass(frozen=True)
class NormalizedKinematics:
    positions: np.ndarray
    rotations: np.ndarray
    root_velocity: np.ndarray
    angular_velocity: np.ndarray
    dt: float


def normalized_kinematics(clip):
    """Reconstruct one complete clip in its fixed rest-reference frame."""
    roots = _finite(clip.root_positions, "root positions")
    quaternions = _finite(clip.local_quaternions, "local quaternions")
    offsets = _finite(clip.offsets, "joint offsets")
    reference = _finite(clip.reference, "rest reference")
    parents = tuple(int(value) for value in clip.parents)
    if roots.ndim != 2 or roots.shape[1] != 3 or len(roots) < 2:
        raise ValueError("At least two root frames are required")
    if quaternions.shape != (len(roots), len(parents), 4):
        raise ValueError("Unexpected local quaternion shape")
    if offsets.shape != (len(parents), 3) or reference.shape != (3, 3):
        raise ValueError("Unexpected hierarchy reference shape")
    if not np.isfinite(clip.scale) or clip.scale <= 0 or not np.isfinite(clip.dt) or clip.dt <= 0:
        raise ValueError("Positive scale and frame interval are required")
    matrices = quat_matrix(quaternions)
    root = (roots - roots[:1]) / float(clip.scale)
    state = np.concatenate((root, rotation6(matrices).reshape(len(root), -1)), axis=-1)
    positions, rotations, _ = forward(state, offsets, parents)
    positions = np.einsum("fji,ik->fjk", positions, reference)
    rotations = np.einsum("ij,fkjl->fkil", reference.T, rotations)
    root_velocity = np.gradient(positions[:, 0], float(clip.dt), axis=0, edge_order=1)
    from full_hierarchy_store_v1 import _angular_velocity

    angular_velocity = _angular_velocity(quaternions, float(clip.dt))
    if not all(np.isfinite(value).all() for value in (positions, rotations, root_velocity, angular_velocity)):
        raise ValueError("Nonfinite normalized kinematics")
    return NormalizedKinematics(positions, rotations, root_velocity, angular_velocity, float(clip.dt))


def contact_signals(kinematics, semantic, thresholds):
    """Estimate foot contact from low height and low foot speed."""
    semantic = tuple(int(value) for value in semantic)
    if len(semantic) <= max(FOOT_SEMANTIC_SLOTS):
        raise ValueError("The semantic map does not contain both feet")
    foot_indices = tuple(semantic[index] for index in FOOT_SEMANTIC_SLOTS)
    feet = _finite(kinematics.positions[:, foot_indices], "foot positions")
    if feet.shape[1:] != (2, 3):
        raise ValueError("Unexpected foot position shape")
    velocity = np.gradient(feet, kinematics.dt, axis=0, edge_order=1)
    speed = np.linalg.norm(velocity, axis=-1)
    height = feet[..., 2]
    floor = float(np.percentile(height, thresholds["floor_percentile"]))
    relative_height = height - floor
    height_bad = _smooth_transition(
        relative_height,
        thresholds["height_on_body_heights"],
        thresholds["height_off_body_heights"],
    )
    speed_bad = _smooth_transition(
        speed,
        thresholds["speed_on_body_heights_per_second"],
        thresholds["speed_off_body_heights_per_second"],
    )
    probability = np.sqrt(np.maximum(0.0, (1.0 - height_bad) * (1.0 - speed_bad)))
    contact = np.column_stack(
        [
            _hysteresis(
                probability[:, side],
                thresholds["probability_on"],
                thresholds["probability_off"],
                thresholds["minimum_contact_frames"],
            )
            for side in range(2)
        ]
    )
    confidence = HEURISTIC_CONFIDENCE_CEILING * np.abs(probability - 0.5) * 2.0
    return {
        "foot_indices": foot_indices,
        "floor": floor,
        "height": height,
        "speed": speed,
        "probability": probability,
        "contact": contact,
        "confidence": confidence,
        "provenance": PROVENANCE_CODE["heuristic"],
        "ground_truth": False,
    }


def event_proposals(signals, root_velocity, thresholds):
    """Find weak takeoff and landing proposals around sustained flight runs."""
    contact = np.asarray(signals["contact"], dtype=bool)
    root_velocity = _finite(root_velocity, "root velocity")
    if contact.ndim != 2 or contact.shape[1] != 2 or root_velocity.shape != (len(contact), 3):
        raise ValueError("Unexpected contact or root-velocity shape")
    airborne = _remove_short_true(
        ~np.any(contact, axis=1), thresholds["minimum_flight_frames"]
    )
    events = []
    for start, end in _runs(airborne):
        before = start > 0 and bool(np.any(contact[start - 1]))
        after = end + 1 < len(contact) and bool(np.any(contact[end + 1]))
        take_slice = root_velocity[max(0, start - 2) : min(len(contact), start + 2), 2]
        land_slice = root_velocity[max(0, end - 1) : min(len(contact), end + 3), 2]
        upward = float(np.max(take_slice)) if len(take_slice) else 0.0
        downward = float(np.min(land_slice)) if len(land_slice) else 0.0
        base = {
            "flight_start": start,
            "flight_end": end,
            "flight_frames": end - start + 1,
            "provenance": "heuristic",
            "ground_truth": False,
        }
        if before and upward >= thresholds["takeoff_upward_root_speed"]:
            events.append(
                {
                    **base,
                    "kind": "takeoff",
                    "frame": start,
                    "vertical_root_speed": upward,
                    "confidence": min(
                        HEURISTIC_CONFIDENCE_CEILING,
                        HEURISTIC_CONFIDENCE_CEILING
                        * upward
                        / max(thresholds["takeoff_upward_root_speed"] * 2.0, 1e-12),
                    ),
                }
            )
        if after and downward <= -thresholds["landing_downward_root_speed"]:
            events.append(
                {
                    **base,
                    "kind": "landing",
                    "frame": end + 1,
                    "vertical_root_speed": downward,
                    "confidence": min(
                        HEURISTIC_CONFIDENCE_CEILING,
                        HEURISTIC_CONFIDENCE_CEILING
                        * abs(downward)
                        / max(thresholds["landing_downward_root_speed"] * 2.0, 1e-12),
                    ),
                }
            )
    return events


def static_proposals(kinematics, semantic, thresholds):
    """Find low-motion windows without labelling them as reviewed static poses."""
    semantic = tuple(int(value) for value in semantic)
    frames = thresholds["window_frames"]
    stride = thresholds["stride_frames"]
    if not isinstance(frames, int) or frames < 2 or not isinstance(stride, int) or stride < 1:
        raise ValueError("Static window and stride must be positive integers")
    root_speed = np.linalg.norm(kinematics.root_velocity, axis=-1)
    joint_speed = np.linalg.norm(kinematics.angular_velocity[:, semantic], axis=-1)
    result = []
    for start in range(0, len(root_speed) - frames + 1, stride):
        end = start + frames - 1
        root_p95 = float(np.percentile(root_speed[start : end + 1], 95))
        angular_p95 = float(np.percentile(joint_speed[start : end + 1], 95))
        root_segment = kinematics.positions[start : end + 1, 0]
        displacement = float(np.max(np.linalg.norm(root_segment - root_segment[:1], axis=-1)))
        if (
            root_p95 <= thresholds["maximum_root_speed_body_heights_per_second"]
            and angular_p95 <= thresholds["maximum_angular_speed_radians_per_second"]
            and displacement <= thresholds["maximum_root_displacement_body_heights"]
        ):
            margin = min(
                1.0 - root_p95 / thresholds["maximum_root_speed_body_heights_per_second"],
                1.0 - angular_p95 / thresholds["maximum_angular_speed_radians_per_second"],
                1.0 - displacement / thresholds["maximum_root_displacement_body_heights"],
            )
            result.append(
                {
                    "kind": "static",
                    "start": start,
                    "end": end,
                    "frames": frames,
                    "root_speed_p95": root_p95,
                    "angular_speed_p95": angular_p95,
                    "root_displacement": displacement,
                    "confidence": min(
                        HEURISTIC_CONFIDENCE_CEILING,
                        HEURISTIC_CONFIDENCE_CEILING * max(0.0, margin),
                    ),
                    "provenance": "heuristic",
                    "ground_truth": False,
                }
            )
    return result


def clip_proposals(clip, thresholds):
    """Return compact weak proposals for one hierarchy clip."""
    kinematics = normalized_kinematics(clip)
    signals = contact_signals(kinematics, clip.semantic, thresholds["contact"])
    contacts = []
    for side, name in enumerate(FOOT_NAMES):
        for start, end in _runs(signals["contact"][:, side]):
            block = signals["probability"][start : end + 1, side]
            confidence = signals["confidence"][start : end + 1, side]
            contacts.append(
                {
                    "kind": "contact",
                    "side": name,
                    "start": start,
                    "end": end,
                    "frames": end - start + 1,
                    "mean_probability": float(np.mean(block)),
                    "minimum_probability": float(np.min(block)),
                    "maximum_probability": float(np.max(block)),
                    "confidence": float(min(HEURISTIC_CONFIDENCE_CEILING, np.mean(confidence))),
                    "provenance": "heuristic",
                    "ground_truth": False,
                }
            )
    events = event_proposals(signals, kinematics.root_velocity, thresholds["events"])
    static = static_proposals(kinematics, clip.semantic, thresholds["static"])
    return {
        "frames": len(kinematics.positions),
        "dt": kinematics.dt,
        "floor": signals["floor"],
        "contact_fraction": [float(value) for value in signals["contact"].mean(axis=0)],
        "double_contact_fraction": float(np.all(signals["contact"], axis=1).mean()),
        "contacts": contacts,
        "events": events,
        "static": static,
        "provenance": "heuristic",
        "ground_truth": False,
        "scene_geometry_known": False,
        "hand_contacts_known": False,
    }
