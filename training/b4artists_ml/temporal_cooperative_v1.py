"""Cooperative research temporal generation with source-visible pause points.
SPDX-License-Identifier: GPL-2.0-or-later
No model is supplied, qualified or installed by this module. Candidate publication
continues through the existing workflow after the entire sample set succeeds.
"""
import sys
from temporal_projection import (copy,math,np,bpy,Quaternion,Matrix,solver,w,p,rs,
    motion_layer,sample_anchors,_array,_rotations,_frame,_apply_known_blend)
from b4artists_ml.flight import _curve_token
from temporal_observer_steps_v1 import sample_steps as _observe_steps
_OWNERS={}
_LIVE={}
_HANDLER_NAMES=('save_pre','load_pre','undo_pre','redo_pre')
_CHANNELS=('location','rotation_euler','rotation_quaternion','rotation_axis_angle',
           'scale','delta_location','delta_rotation_euler','delta_rotation_quaternion','delta_scale')

class VisibleState:
    def __init__(self,obj,scene):
        self.obj=obj;self.scene=scene;self.frame=p._frame(scene)
        self.pose=w.raw_pose(obj);self.modes=rs.mode_values(obj)
        self.channels={n:tuple(getattr(obj,n)) for n in _CHANNELS}
    def restore(self):
        if p._frame(self.scene)!=self.frame:_frame(self.scene,self.frame)
        for name,value in self.channels.items():
            if tuple(getattr(self.obj,name))!=value:setattr(self.obj,name,value)
        for name,value in self.pose.items():
            bone=self.obj.pose.bones.get(name)
            if bone is None:continue
            for field in ('location','scale'):
                if tuple(getattr(bone,field))!=tuple(value[field]):setattr(bone,field,value[field])
            field='rotation_quaternion' if value['mode']=='QUATERNION' else 'rotation_axis_angle' if value['mode']=='AXIS_ANGLE' else 'rotation_euler'
            if tuple(getattr(bone,field))!=tuple(value['raw_rotation']):setattr(bone,field,value['raw_rotation'])
        for name,properties in self.modes.items():
            bone=self.obj.pose.bones.get(name)
            if bone is not None:
                for key,value in properties.items():
                    if key in bone and bone[key]!=value:bone[key]=value
        # Keep one explicit final evaluation even if all values already match.
        # Structural, curve, pose, anchor and mode guards remain unchanged.
        p._update(self.obj)
    def matches(self):
        return (self.frame==p._frame(self.scene) and self.pose==w.raw_pose(self.obj)
                and self.modes==rs.mode_values(self.obj)
                and all(tuple(getattr(self.obj,n))==v for n,v in self.channels.items()))

class Transaction:
    def __init__(self,obj,scene):
        self.obj=obj;self.scene=scene;self.key=obj.as_pointer();self.initial=VisibleState(obj,scene)
        self.exposed=False;self.structure=w._rest_signature(obj);self.switches=w._switches(obj)
        ad=obj.animation_data;self.action=ad.action.as_pointer() if ad and ad.action else None
        self.slot=w._slot(ad) if ad else '';self.curves=_curve_token(obj) if self.action else None
        self.anchors=tuple((a.frame,a.payload) for a in obj.b4ml.anchors)
        self.fps=(scene.render.fps,scene.render.fps_base);self.mode=obj.mode;self.rotation_mode=obj.rotation_mode
    def guard(self):
        obj=self.obj;state=obj.b4ml;ad=obj.animation_data
        action=ad.action.as_pointer() if ad and ad.action else None
        if _OWNERS.get(self.key) is not self:raise ValueError('Temporal job ownership changed')
        if bpy.context.scene!=self.scene or obj.mode!=self.mode or obj.rotation_mode!=self.rotation_mode:raise ValueError('Host context changed during temporal generation')
        if not self.initial.matches():raise ValueError('Pose or playhead changed during temporal generation')
        if action!=self.action or (w._slot(ad) if ad else '')!=self.slot:raise ValueError('Source action or slot changed during temporal generation')
        if (_curve_token(obj) if action else None)!=self.curves:raise ValueError('Source curves changed during temporal generation')
        if self.structure!=w._rest_signature(obj) or self.switches!=w._switches(obj):raise ValueError('Rig structure or properties changed during temporal generation')
        if self.anchors!=tuple((a.frame,a.payload) for a in state.anchors):raise ValueError('Authored poses changed during temporal generation')
        if self.fps!=(self.scene.render.fps,self.scene.render.fps_base):raise ValueError('Frame rate changed during temporal generation')
        if (state.posing_payload or state.body_payload or state.quadruped_payload
                or state.candidate_action or state.body_running or state.body_live
                or state.contact_running or state.contact_suggest_running
                or state.flight_running or state.secondary_running
                or state.cleanup_running or motion_layer.find(obj)):
            raise ValueError('Another animation workflow started during temporal generation')
        w._reject_nla(obj)
    def pause(self,progress,cancel_requested):
        working=VisibleState(self.obj,self.scene);self.initial.restore();self.exposed=True
        yield progress
        self.guard()
        if cancel_requested is not None and cancel_requested():raise InterruptedError('Temporal projection cancelled')
        self.exposed=False;working.restore()


def _generate_steps(obj,predictor,*,context=True,iterations=50,constraints=None,cancel_requested=None):
    """Yield with the original visible frame/pose; return complete validated samples.

    Closing at a pause keeps subsequent animator edits. Source/rig/anchor changes
    reject before resuming the inner solver. No candidate action is created here.
    Pause lengths, total latency and final publication need separate measurements;
    cooperative scheduling alone is not a viewport responsiveness qualification.
    """
    if not callable(predictor):raise ValueError('A temporal proposal provider is required')
    if cancel_requested is not None and not callable(cancel_requested):raise ValueError('Cancellation probe must be callable')
    w.require_rig(obj);w._reject_nla(obj);p._check_space(obj)
    key=obj.as_pointer();state=obj.b4ml;owner=solver._SESSIONS.get(key)
    if key in _OWNERS:raise ValueError('A temporal job already owns this rig')
    if (state.posing_payload or state.body_payload or state.quadruped_payload
            or state.candidate_action or state.body_running or state.body_live
            or state.contact_running or state.contact_suggest_running
            or state.flight_running or state.secondary_running
            or state.cleanup_running or motion_layer.find(obj)
            or (owner is not None and not owner.closed)):
        raise ValueError('Resolve the active pose or animation preview first')
    rows=w.read_anchors(obj);binding=solver.mapping(obj);names=set(rows[0][1]['pose'])
    if not set(binding['controls'])<=names:raise ValueError('Temporal whole-body projection requires all mapped controls in the anchors')
    frames=sorted({f for f,_ in rows}|{float(f) for f in range(math.ceil(rows[0][0]),math.floor(rows[-1][0])+1)})
    if len(frames)*len(names)*10>w.MAX_KEYS:raise ValueError('Projected animation exceeds the key budget')
    constraints={} if constraints is None else copy.deepcopy(constraints)
    if not isinstance(constraints,dict) or any(type(f) not in (int,float) or f not in frames for f in constraints):raise ValueError('Constraints must refer to generated frames')
    priorities=dict(rows)
    if set(constraints)&set(priorities):raise ValueError('Author contacts into priority poses; projection never changes a priority')
    allowed={'position_pins','orientations_world','pole_targets','rotation_limits'}
    if any(not isinstance(opts,dict) or set(opts)-allowed for opts in constraints.values()):raise ValueError('Unknown projection constraint')
    scene=bpy.context.scene;tx=Transaction(obj,scene);_OWNERS[key]=tx;inner=None;session=None
    samples={f:copy.deepcopy(v['pose']) for f,v in rows};metrics=[]
    try:
        for (fa,a),(fb,b) in zip(rows,rows[1:]):
            yield from tx.pause(dict(phase='observing',frame=fa,total_frames=len(frames)),cancel_requested)
            observed=yield from _observe_steps(obj,fa,fb,tx=tx,context=context,cancel_requested=cancel_requested,total_frames=len(frames))
            query=[f for f in frames if fa<f<fb]
            if not query:continue
            t=np.asarray([(f-fa)/(fb-fa) for f in query])
            points,rotations=predictor(copy.deepcopy(observed),t.copy())
            points=_array(points,(len(query),17,3),'predicted positions')
            rotations=_rotations(rotations,(len(query),17,3,3),'predicted rotations')
            world_points=observed.world_points(points);world_rotations=observed.world_rotations(rotations)
            yield from tx.pause(dict(phase='proposal_ready',frame=fa,total_frames=len(frames)),cancel_requested)
            for i,frame in enumerate(query):
                if cancel_requested is not None and cancel_requested():raise InterruptedError('Temporal projection cancelled')
                w.restore_pose(obj,tx.initial.pose);rs.restore_values(obj,tx.initial.modes);_frame(scene,frame)
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
                inner=session.solve_steps(target,mask,learned_influence=0.,iterations=iterations,
                    proposal_world=world_points[i],proposal_rotations_world=[tuple(Matrix(m).to_quaternion()) for m in world_rotations[i]],
                    orientations_world=orientations,cancel_requested=cancel_requested,**opts)
                while True:
                    try:progress=next(inner)
                    except StopIteration as done:result=done.value;inner=None;break
                    yield from tx.pause(dict(progress,frame=frame,total_frames=len(frames)),cancel_requested)
                samples[frame]=w.raw_pose(obj,names)
                metrics.append(dict(frame=frame,**{k:v for k,v in result.items() if k!='points'}))
                session.cancel();session=None
                yield from tx.pause(dict(phase='frame_ready',frame=frame,total_frames=len(frames)),cancel_requested)
        tx.initial.restore()
        yield from tx.pause(dict(phase='ready',frame=frames[-1],total_frames=len(frames)),cancel_requested)
        return w._validated_pose_samples(obj,rows,frames,samples),metrics
    finally:
        # The outer transaction, not a frame-local session, owns source recovery.
        # Capture newer visible edits BEFORE closing an inner iterator: its own
        # failure cleanup restores its working-frame pose as designed.
        failed=sys.exc_info()[0] is not None;preserved=None;cleanup_error=None
        try:preserved=VisibleState(obj,scene) if tx.exposed else tx.initial
        except ReferenceError:pass  # A deleted rig must never be resurrected.
        try:
            if inner is not None:inner.close()
        except BaseException as exc:cleanup_error=exc
        finally:
            if session is not None:
                session.closed=True
                if solver._SESSIONS.get(key) is session:solver._SESSIONS.pop(key,None)
            try:
                if preserved is not None:preserved.restore()
            finally:
                if _OWNERS.get(key) is tx:_OWNERS.pop(key,None)
        if cleanup_error is not None and not failed:raise cleanup_error


def generate_samples(obj,predictor,**options):
    """Synchronous consumer for reference and data tests, not viewport scheduling."""
    steps=generate_steps(obj,predictor,**options)
    try:
        while True:
            try:next(steps)
            except StopIteration as done:return done.value
    finally:steps.close()


class Job:
    """Own the iterator so host lifecycle hooks can cancel paused work."""
    def __init__(self,obj,predictor,options):
        self.steps=_generate_steps(obj,predictor,**options);self.reason=None;self.running=False;self.closed=False
        _LIVE[id(self)]=self
    def __iter__(self):return self
    def __next__(self):
        if self.reason is not None:raise InterruptedError(self.reason)
        if self.closed:raise StopIteration
        self.running=True
        try:progress=next(self.steps)
        except BaseException:
            self.closed=True;_LIVE.pop(id(self),None);raise
        finally:self.running=False
        if self.reason is not None:
            self.close();raise InterruptedError(self.reason)
        return progress
    def close(self):
        if self.running:raise RuntimeError('Cannot close temporal work while executing a step')
        try:
            if not self.closed:self.steps.close()
        finally:self.closed=True;_LIVE.pop(id(self),None)
    def cancel(self,reason):
        self.reason=reason
        if not self.running:self.close()


@bpy.app.handlers.persistent
def before_host_change(*args):
    for job in list(_LIVE.values()):job.cancel('Temporal generation cancelled before save, load, undo or redo')


def register():
    # Register idempotently. The research caller owns unregister; product addon
    # registration/disable integration is still required before distribution.
    for name in _HANDLER_NAMES:
        handlers=getattr(bpy.app.handlers,name)
        if before_host_change not in handlers:handlers.append(before_host_change)


def unregister():
    for job in list(_LIVE.values()):job.cancel('Temporal generation stopped by unregister')
    for name in _HANDLER_NAMES:
        handlers=getattr(bpy.app.handlers,name)
        if before_host_change in handlers:handlers.remove(before_host_change)


def generate_steps(obj,predictor,**options):
    """Return a lifecycle-owned iterator; call unregister after research use."""
    register();return Job(obj,predictor,options)
