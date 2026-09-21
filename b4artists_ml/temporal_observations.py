"""Known authored poses calibrated for actual humanoid rigs; no training data dependency."""
from dataclasses import dataclass
import math
import numpy as np
from .temporal_math import rotation6,slerp
SCHEMA="b4ml-semantic-observations-v1"

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
    calibrated = basis.T @ rotations @ np.swapaxes(rest_rotations, -1, -2) @ reference
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

def sample_steps(obj,start,end,*,tx,context,cancel_requested,total_frames):
    # Keep the observation value object and its pure interpolation helpers
    # importable in an ordinary Python process.  Blender is only required for
    # sampling a live rig; importing it at module scope made offline math
    # validation depend on the host runtime unnecessarily.
    import bpy
    from . import workflow as w,posing as p,rig_state as rs,body_solver as solver
    rows=dict(w.read_anchors(obj))
    if isinstance(start,bool) or isinstance(end,bool) or start not in rows or end not in rows or not start<end:
        raise ValueError('Select two increasing stored anchor frames')
    if end-start<1.:raise ValueError('Temporal observations require at least one frame between anchors')
    if any(start<f<end for f in rows):raise ValueError('Choose adjacent stored anchors; do not span a priority pose')
    if not isinstance(context,bool):raise ValueError('Explicit context availability required')
    w.require_rig(obj);w._reject_nla(obj);p._check_space(obj)
    owner=solver._SESSIONS.get(obj.as_pointer())
    if obj.b4ml.posing_payload or obj.b4ml.body_payload or obj.b4ml.quadruped_payload or obj.b4ml.candidate_action or (owner is not None and not owner.closed):
        raise ValueError('Resolve the active pose or animation preview first')
    binding=solver.mapping(obj,writable=False);scene=bpy.context.scene
    fps=scene.render.fps/scene.render.fps_base
    if not math.isfinite(fps) or fps<=0:raise ValueError('Positive scene frame rate required')
    frames=[start,end,start-1,end+1] if context else [start,end]
    before=type(tx.initial)(obj,scene);points=[];rotations=[]
    try:
        for index,frame in enumerate(frames):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Rig observation sampling cancelled')
            # Match the reference evaluation order. Unkeyed channels must not
            # carry the previous stored pose into a different known frame.
            w.restore_pose(obj,before.pose);rs.restore_values(obj,before.modes)
            _frame_set(scene,math.floor(frame),subframe=frame-math.floor(frame))
            if frame in rows:
                payload=rows[frame];rs.restore_values(obj,payload.get('rig_modes',{}))
                w.restore_pose(obj,payload['pose']);p._update(obj)
            p._check_space(obj)
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());world=evaluated.matrix_world
            points.append(np.array([world @ evaluated.pose.bones[n].head for n in binding['names']]))
            rotations.append(np.array([_orientation(world @ evaluated.pose.bones[n].matrix) for n in binding['names']]))
            if index==0:
                rest=np.array([world @ obj.data.bones[n].head_local for n in binding['names']])
                rest_rotations=np.array([_orientation(world @ obj.data.bones[n].matrix_local) for n in binding['names']])
            yield from tx.pause(dict(phase='observed_pose',frame=frame,observed_index=index,total_observations=len(frames),total_frames=total_frames),cancel_requested)
        if not context:
            points += [points[0].copy(),points[1].copy()]
            rotations += [rotations[0].copy(),rotations[1].copy()]
        return encode(rest,rest_rotations,np.array(points),np.array(rotations),duration=(end-start)/fps,dt=1/fps,context=context)
    finally:
        # When suspended, the animator may have edited the visible source. The
        # outer transaction must capture it before any working-state cleanup.
        if not tx.exposed:before.restore()
