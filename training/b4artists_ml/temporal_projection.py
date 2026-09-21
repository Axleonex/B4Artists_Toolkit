"""Research temporal proposal -> actual FK controls -> editable native action.

Providers consume shared observations and normalized query times, returning
normalized positions and calibrated rotation matrices. This module supplies no
learned temporal model. The procedural provider is an explicitly named baseline.
"""
import copy, math
import numpy as np
import bpy
from mathutils import Quaternion, Matrix
from b4artists_ml import body_solver as solver,workflow as w,posing as p,rig_state as rs,motion_layer
from rig_observations import sample_anchors,_array,_rotations


def procedural(observations,t):
    """Linear positions and SLERP orientations; not a learned predictor."""
    return observations.baseline(t)


def _frame(scene,value):
    scene.frame_set(math.floor(value),subframe=value-math.floor(value))


def _apply_known_blend(obj,a,b,t):
    values=w.blend_pose(a,b,t,'LINEAR')
    for name,value in values.items():
        bone=obj.pose.bones[name]
        bone.location=value['location'];bone.scale=value['scale']
        solver._set_quat(bone,Quaternion(value['rotation']))
    p._update(obj)


def generate_samples(obj,predictor,*,context=True,iterations=50,constraints=None,cancel_requested=None):
    """Stage a full sample set without making an action or retaining a preview.

    Constraints are frame -> solver options, with position_pins mapping semantic
    joint indices to world positions; orientations/poles/limits use solver units.
    All solved controls must be captured. Uncaptured accessory channels remain
    source context. Endpoint samples always use the exact authored control values.
    This synchronous research path does not yet provide interactive scheduling.
    """
    if not callable(predictor):raise ValueError('A temporal proposal provider is required')
    if cancel_requested is not None and not callable(cancel_requested):raise ValueError('Cancellation probe must be callable')
    w.require_rig(obj);w._reject_nla(obj);p._check_space(obj)
    state=obj.b4ml;owner=solver._SESSIONS.get(obj.as_pointer())
    if (state.posing_payload or state.body_payload or state.candidate_action or motion_layer.find(obj)
            or (owner is not None and not owner.closed)):
        raise ValueError('Resolve the active pose or animation preview first')
    rows=w.read_anchors(obj);binding=solver.mapping(obj);names=set(rows[0][1]['pose'])
    if not set(binding['controls'])<=names:
        raise ValueError('Temporal whole-body projection requires all mapped controls in the anchors')
    frames=sorted({f for f,_ in rows}|{float(f) for f in range(math.ceil(rows[0][0]),math.floor(rows[-1][0])+1)})
    if len(frames)*len(names)*10>w.MAX_KEYS:raise ValueError('Projected animation exceeds the key budget')
    constraints={} if constraints is None else copy.deepcopy(constraints)
    if not isinstance(constraints,dict) or any(type(f) not in (int,float) or f not in frames for f in constraints):
        raise ValueError('Constraints must refer to generated frames')
    priorities=dict(rows)
    if set(constraints)&set(priorities):raise ValueError('Author contacts into priority poses; projection never changes a priority')
    allowed={'position_pins','orientations_world','pole_targets','rotation_limits'}
    for opts in constraints.values():
        if not isinstance(opts,dict) or set(opts)-allowed:raise ValueError('Unknown projection constraint')
    scene=bpy.context.scene
    before_frame=(scene.frame_current,scene.frame_subframe);before=w.raw_pose(obj);modes=rs.mode_values(obj)
    channels=('location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale','delta_location','delta_rotation_euler','delta_rotation_quaternion','delta_scale')
    object_channels={n:tuple(getattr(obj,n)) for n in channels}
    samples={f:copy.deepcopy(v['pose']) for f,v in rows};metrics=[]
    try:
        for (fa,a),(fb,b) in zip(rows,rows[1:]):
            if cancel_requested is not None and cancel_requested():raise InterruptedError('Temporal projection cancelled')
            observed=sample_anchors(obj,fa,fb,context=context,cancel_requested=cancel_requested)
            query=[f for f in frames if fa<f<fb]
            if not query:continue
            t=np.asarray([(f-fa)/(fb-fa) for f in query])
            # Providers receive observations only, never the rig or hidden source samples.
            points,rotations=predictor(copy.deepcopy(observed),t.copy())
            points=_array(points,(len(query),17,3),'predicted positions')
            rotations=_rotations(rotations,(len(query),17,3,3),'predicted rotations')
            world_points=observed.world_points(points);world_rotations=observed.world_rotations(rotations)
            for i,frame in enumerate(query):
                if cancel_requested is not None and cancel_requested():raise InterruptedError('Temporal projection cancelled')
                # Evaluate unowned source channels, then overwrite EVERY modeled
                # control with known-anchor interpolation before constructing a fit.
                w.restore_pose(obj,before);rs.restore_values(obj,modes);_frame(scene,frame)
                rs.restore_values(obj,a.get('rig_modes',{}));_apply_known_blend(obj,a['pose'],b['pose'],float(t[i]))
                target=world_points[i].copy();mask=np.zeros(17,dtype=bool);mask[0]=True
                opts=copy.deepcopy(constraints.get(frame,{}));pins=opts.pop('position_pins',{})
                if not isinstance(pins,dict):raise ValueError('Position pins must be a dictionary')
                for index,point in pins.items():
                    if type(index)!=int or not 0<=index<17:raise ValueError('Invalid semantic pin index')
                    target[index]=_array(point,(3,),'position pin');mask[index]=True
                orientations={j:tuple(Matrix(world_rotations[i,j]).to_quaternion()) for j in solver.ORIENTATION_JOINTS}
                orientations.update(opts.pop('orientations_world',{}))
                session=solver.Session(obj)
                try:
                    result=session.solve(target,mask,learned_influence=0.,iterations=iterations,
                        proposal_world=world_points[i],proposal_rotations_world=[tuple(Matrix(m).to_quaternion()) for m in world_rotations[i]],orientations_world=orientations,
                        cancel_requested=cancel_requested,**opts)
                    samples[frame]=w.raw_pose(obj,names)
                    metrics.append(dict(frame=frame,**{k:v for k,v in result.items() if k!='points'}))
                finally:session.cancel()
    finally:
        _frame(scene,before_frame[0]+before_frame[1])
        for n,value in object_channels.items():
            if tuple(getattr(obj,n))!=value:setattr(obj,n,value)
        w.restore_pose(obj,before);rs.restore_values(obj,modes)
    return w._validated_pose_samples(obj,rows,frames,samples),metrics


def preview(obj,predictor,**options):
    """Publish only a completely generated and validated candidate."""
    samples,metrics=generate_samples(obj,predictor,**options)
    w.preview(obj,bpy.context.scene,pose_samples=samples)
    return metrics
