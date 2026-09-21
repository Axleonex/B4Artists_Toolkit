"""Research-only, rest-calibrated semantic observations for real humanoid rigs.
SPDX-License-Identifier: GPL-2.0-or-later
Schema 1 is NOT the 23-joint fixed-offset kernel input. No learned output is
applied here. Four known poses are sampled; hidden inbetweens are never read.
"""
from dataclasses import dataclass
import math
import numpy as np
from temporal_data import rotation6, slerp

SCHEMA = "b4ml-semantic-observations-v1"


def _array(value, shape, label):
    value = np.asarray(value, dtype=float)
    if value.shape != shape or not np.isfinite(value).all():
        raise ValueError(f"Invalid {label}")
    return value


def _rotations(value, shape, label):
    value = _array(value, shape, label)
    if np.max(np.abs(np.swapaxes(value, -1, -2) @ value - np.eye(3))) > 2e-5 or np.min(np.linalg.det(value)) < .99998:
        raise ValueError(f"Expected proper {label}")
    return value


def _project_rotations(value, label):
    """Return the nearest proper rotations after finite-precision composition."""
    value = np.asarray(value, dtype=float)
    if value.shape[-2:] != (3, 3) or not np.isfinite(value).all():
        raise ValueError(f"Invalid {label}")
    left, _, right = np.linalg.svd(value)
    result = left @ right
    if np.min(np.linalg.det(result)) <= 0:
        raise ValueError(f"Reflected {label}")
    return result


@dataclass(frozen=True)
class Observations:
    positions: np.ndarray
    rotations: np.ndarray
    rest: np.ndarray
    origin: np.ndarray
    basis: np.ndarray
    scale: float
    rest_alignment: np.ndarray
    duration: float
    dt: float
    context: bool
    schema: str = SCHEMA

    def features(self):
        # Explicitly calibrated world rotations, not ancestor-local rotations.
        packed = np.concatenate((self.positions, rotation6(self.rotations)), axis=-1)
        return np.r_[packed.ravel(), self.rest.ravel(), float(self.context),
                     float(self.context), self.duration, self.dt]

    def baseline(self, t):
        t = np.asarray(t, dtype=float)
        if t.ndim != 1 or not np.isfinite(t).all() or np.any((t < 0) | (t > 1)):
            raise ValueError("Query times must lie in [0, 1]")
        points = (1-t[:, None, None])*self.positions[0] + t[:, None, None]*self.positions[1]
        return points, slerp(self.rotations[0], self.rotations[1], t)

    def world_rotations(self, rotations):
        return self.basis @ np.asarray(rotations) @ self.rest_alignment

    def world_points(self, points):
        return np.asarray(points)*self.scale @ self.basis.T + self.origin


def encode(rest, rest_rotations, observed, rotations, *, duration, dt, context):
    rest = _array(rest, (17, 3), "rest positions")
    rest_rotations = _rotations(rest_rotations, (17, 3, 3), "rest rotations")
    observed = _array(observed, (4, 17, 3), "observed positions")
    rotations = _rotations(rotations, (4, 17, 3, 3), "observed rotations")
    if not np.isfinite([duration, dt]).all() or min(duration, dt) <= 0 or duration < dt:
        raise ValueError("Positive duration and sample time required")
    if not isinstance(context, (bool, np.bool_)):
        raise ValueError("Explicit context availability required")
    left = rest[11]-rest[14]
    up = (rest[5]+rest[8]-rest[11]-rest[14])*.5
    scale = float(np.linalg.norm(up)); width = float(np.linalg.norm(left))
    if min(scale, width) < 1e-8:
        raise ValueError("Degenerate body reference")
    left = left/width; up = up-left*np.dot(up, left)
    if np.linalg.norm(up) < 1e-8:
        raise ValueError("Degenerate body axes")
    up /= np.linalg.norm(up)
    reference = np.stack((left, np.cross(up, left), up), axis=1)
    basis = rotations[0, 0] @ rest_rotations[0].T @ reference
    origin = observed[0, 0].copy()
    # Calibrate each semantic bone against its own rest axes. Bone roll cannot
    # become a false motion signal, and distributed rig joints stay explicit.
    calibrated = _project_rotations(
        basis.T @ rotations @ np.swapaxes(rest_rotations, -1, -2) @ reference,
        "calibrated rotations",
    )
    points = (observed-origin) @ basis/scale
    if not context:
        points[2:] = points[:2]
        calibrated[2:] = calibrated[:2]
    return Observations(points, calibrated, (rest-rest[0]) @ reference/scale,
                        origin, basis, scale, reference.T @ rest_rotations, float(duration), float(dt), bool(context))


def _orientation(matrix):
    columns = np.array(matrix.to_3x3())
    lengths = np.linalg.norm(columns, axis=0)
    if not np.isfinite(columns).all() or min(lengths) < 1e-8 or np.linalg.det(columns) <= 0:
        raise ValueError("Reflected or collapsed joint orientation")
    unit = columns / lengths
    if np.max(np.abs(unit.T @ unit-np.eye(3))) > 1e-4:
        raise ValueError("Sheared joint orientation requires a separate adapter")
    return np.array(matrix.to_quaternion().to_matrix())


def _frame_set(scene, frame, *, subframe=0.):
    scene.frame_set(frame, subframe=subframe)


def sample(obj, start, end, *, context=True, cancel_requested=None):
    """Read source-action poses explicitly; stored anchors are not applied."""
    if type(start) is not int or type(end) is not int or not start < end:
        raise ValueError("Increasing integer anchor frames required")
    return _sample(obj,start,end,context=context,cancel_requested=cancel_requested)


def sample_anchors(obj, start, end, *, context=True, cancel_requested=None):
    """Evaluate two stored priority poses, with optional outside-gap source context.

    No action or key is created. Uncaptured channels follow source evaluation;
    captured channels and canonical modes come from the saved anchor payload.
    """
    from b4artists_ml import workflow as w
    rows=dict(w.read_anchors(obj))
    if isinstance(start,bool) or isinstance(end,bool) or start not in rows or end not in rows or not start<end:
        raise ValueError('Select two increasing stored anchor frames')
    if end-start<1.:raise ValueError('Temporal observations require at least one frame between anchors')
    if any(start<frame<end for frame in rows):
        raise ValueError('Choose adjacent stored anchors; do not span a priority pose')
    return _sample(obj,start,end,context=context,cancel_requested=cancel_requested,anchor_poses=rows)


def _sample(obj, start, end, *, context, cancel_requested, anchor_poses=None):
    """Sample known integer frames and restore raw source pose, modes and frame.

    Reads evaluated joints in their existing IK/FK mode. The disposable host
    owns frame evaluation; no action, key, helper, normalization or model load.
    Active previews are refused because another workflow owns their state.
    """
    import bpy
    from b4artists_ml import workflow as w, posing as p, rig_state as rs, motion_layer
    from b4artists_ml.body_solver import mapping, _SESSIONS
    if not isinstance(context, bool):
        raise ValueError("Explicit context availability required")
    w.require_rig(obj); w._reject_nla(obj); p._check_space(obj)
    owner = _SESSIONS.get(obj.as_pointer())
    state = obj.b4ml
    if (state.posing_payload or state.body_payload or state.quadruped_payload
            or state.candidate_action or state.temporal_running
            or state.body_running or state.body_live or state.contact_running
            or state.contact_suggest_running or state.flight_running
            or state.secondary_running or state.cleanup_running
            or motion_layer.find(obj) or (owner is not None and not owner.closed)):
        raise ValueError("Resolve the active pose or animation preview first")
    binding = mapping(obj, writable=False)
    scene = bpy.context.scene
    fps = scene.render.fps / scene.render.fps_base
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("Positive scene frame rate required")
    frames = [start, end, start-1, end+1] if context else [start, end]
    before_frame = (scene.frame_current, scene.frame_subframe)
    before_pose = w.raw_pose(obj); before_modes = rs.mode_values(obj)
    # Restoring a matrix decomposes it and can alter raw Euler/scale channels.
    # Keep the authored channel values instead, including inactive rotations.
    channel_names = ('location', 'rotation_euler', 'rotation_quaternion',
                     'rotation_axis_angle', 'scale', 'delta_location',
                     'delta_rotation_euler', 'delta_rotation_quaternion', 'delta_scale')
    before_channels = {n: tuple(getattr(obj, n)) for n in channel_names}
    points = []; rotations = []
    try:
        for frame in frames:
            if cancel_requested is not None and cancel_requested():
                raise InterruptedError("Rig observation sampling cancelled")
            if anchor_poses is not None:
                # Frame changes do not reset unkeyed channels. Do not let an
                # applied anchor contaminate another anchor or source context.
                w.restore_pose(obj,before_pose);rs.restore_values(obj,before_modes)
            _frame_set(scene, math.floor(frame), subframe=frame-math.floor(frame))
            if anchor_poses is not None and frame in anchor_poses:
                payload=anchor_poses[frame]
                rs.restore_values(obj,payload.get('rig_modes',{}))
                w.restore_pose(obj,payload['pose']);p._update(obj)
            p._check_space(obj)
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            world = evaluated.matrix_world
            points.append(np.array([world @ evaluated.pose.bones[n].head for n in binding['names']]))
            rotations.append(np.array([_orientation(world @ evaluated.pose.bones[n].matrix) for n in binding['names']]))
            if len(points) == 1:
                rest = np.array([world @ obj.data.bones[n].head_local for n in binding['names']])
                rest_rotations = np.array([_orientation(world @ obj.data.bones[n].matrix_local) for n in binding['names']])
        if not context:
            points += [points[0].copy(), points[1].copy()]
            rotations += [rotations[0].copy(), rotations[1].copy()]
        return encode(rest, rest_rotations, np.array(points), np.array(rotations),
                      duration=(end-start)/fps, dt=1/fps, context=context)
    finally:
        _frame_set(scene, before_frame[0], subframe=before_frame[1])
        for name, values in before_channels.items():
            if tuple(getattr(obj, name)) != values:
                setattr(obj, name, values)
        w.restore_pose(obj, before_pose)
        rs.restore_values(obj, before_modes)
