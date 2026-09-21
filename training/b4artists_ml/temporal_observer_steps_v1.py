"""Research-only cooperative sampling of known poses; never reads hidden inbetweens."""
import math
import numpy as np
from temporal_projection import bpy,w,p,rs,solver
from rig_observations import _frame_set,_orientation,encode


def sample_steps(obj,start,end,*,tx,context,cancel_requested,total_frames):
    rows=dict(w.read_anchors(obj))
    if isinstance(start,bool) or isinstance(end,bool) or start not in rows or end not in rows or not start<end:
        raise ValueError('Select two increasing stored anchor frames')
    if end-start<1.:raise ValueError('Temporal observations require at least one frame between anchors')
    if any(start<f<end for f in rows):raise ValueError('Choose adjacent stored anchors; do not span a priority pose')
    if not isinstance(context,bool):raise ValueError('Explicit context availability required')
    w.require_rig(obj);w._reject_nla(obj);p._check_space(obj)
    owner=solver._SESSIONS.get(obj.as_pointer())
    if obj.b4ml.posing_payload or obj.b4ml.body_payload or obj.b4ml.candidate_action or (owner is not None and not owner.closed):
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
