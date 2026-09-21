"""Source-preserving authored-motion previews using only bundled local modules."""
import bpy
from . import workflow as w,temporal_generation as generation,temporal_math,curve_smoothing
_JOBS={}

def start(obj,scene):
    w.require_rig(obj)
    if scene!=bpy.context.scene:raise ValueError('Use the active scene for motion generation')
    key=obj.as_pointer()
    if key in _JOBS or obj.b4ml.temporal_running:raise ValueError('Motion generation is already running')
    state=obj.b4ml
    if (state.candidate_action or state.posing_payload or state.body_payload
            or state.quadruped_payload or state.body_running or state.body_live
            or state.contact_running or state.contact_suggest_running
            or state.flight_running or state.secondary_running
            or state.cleanup_running or w.motion_layer.find(obj)):
        raise ValueError('Finish the active animation operation first')
    strength=temporal_math.validate_proposal_strength(state.temporal_strength)
    iterator=generation.generate_private_steps(obj,lambda observed,t:observed.baseline(t),context=False,
        prepare_predictor=temporal_math.prepare,_return_validated_packet=True,
        proposal_strength=strength)
    _JOBS[key]=dict(obj=obj,scene=scene,iterator=iterator,
                    smoothing=bool(state.temporal_smoothing),strength=strength)
    state.temporal_running=True;state.temporal_progress='Reading authored poses'

def abort(obj,reason='Motion generation cancelled; source preserved'):
    key=obj.as_pointer();job=_JOBS.pop(key,None)
    try:
        if job is not None:job['iterator'].close()
    finally:
        obj.b4ml.temporal_running=False;obj.b4ml.temporal_progress='';obj.b4ml.status=reason

def step(obj):
    key=obj.as_pointer();job=_JOBS.get(key)
    if job is None:raise InterruptedError('Motion generation stopped')
    try:
        if bool(obj.b4ml.temporal_smoothing)!=job['smoothing']:
            raise ValueError('Smoothing setting changed; generate the preview again')
        strength=temporal_math.validate_proposal_strength(obj.b4ml.temporal_strength)
        if abs(strength-job['strength'])>1e-12:
            raise ValueError('Motion strength changed; generate the preview again')
        try:progress=next(job['iterator'])
        except StopIteration as done:
            samples,metrics=done.value
            # The generator has validated all frames and restored the source.
            # Only now create a separate editable action through the usual path.
            _publish(job,samples)
            candidate=obj.b4ml.candidate_action
            if candidate is not None:
                candidate['b4ml_temporal_strength']=job['strength']
                candidate['b4ml_temporal_learned']=False
            mode='Smoothed ' if job['smoothing'] else ''
            obj.b4ml.status=(f'{mode}procedural whole-body preview ready at {job["strength"]:.0%} strength; review and correct captured contacts')
            _JOBS.pop(key,None);obj.b4ml.temporal_running=False;obj.b4ml.temporal_progress=''
            return True
        frame=progress.get('frame');phase=progress.get('phase','working').replace('_',' ')
        obj.b4ml.temporal_progress=phase.title()+(f' at frame {frame:g}' if frame is not None else '')
        return False
    except BaseException:
        abort(obj,'Motion generation stopped; source preserved')
        raise


def _publish(job,samples):
    obj=job['obj'];scene=job['scene'];candidate=None;smoothed=None
    try:
        # Validate anchors once at the transaction boundary. No user or timer
        # yield occurs before both consumers finish, so this snapshot cannot go
        # stale while the candidate is being published.
        anchors=w.read_anchors(obj)
        w.preview(obj,scene,pose_samples=samples,_validated_rows=anchors)
        candidate=obj.b4ml.candidate_action;slot=w._slot(obj.animation_data)
        if job['smoothing']:
            smoothed,_=curve_smoothing.smooth_copy(obj,candidate,anchors[0][0],anchors[-1][0],_validated_rows=anchors)
            smoothed['b4ml_backend']=curve_smoothing.BACKEND
            w.assign_action(obj,smoothed,slot);obj.b4ml.candidate_action=smoothed
    except BaseException:
        if candidate is not None:
            # Restore the owned generated candidate before invoking its complete
            # source/mode recovery, including failures during smoothing publish.
            w.assign_action(obj,candidate,slot);obj.b4ml.candidate_action=candidate
            w.finish_preview(obj,scene,False)
        if smoothed is not None and smoothed.users==0:bpy.data.actions.remove(smoothed)
        raise
    if smoothed is not None and candidate.users==0:bpy.data.actions.remove(candidate)


def run(obj,scene):
    """Synchronous operator path for background scripts; UI uses timed steps."""
    start(obj,scene)
    while not step(obj):pass
    return obj.b4ml.candidate_action

@bpy.app.handlers.persistent
def before_host_change(*args):
    for job in list(_JOBS.values()):
        try:abort(job['obj'],'Motion generation cancelled before save, load, undo or redo')
        except ReferenceError:pass
    _JOBS.clear()

def register():
    generation.register()
    for name in ('save_pre','load_pre','undo_pre','redo_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if before_host_change not in handlers:handlers.append(before_host_change)

def unregister():
    before_host_change();generation.unregister()
    for name in ('save_pre','load_pre','undo_pre','redo_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if before_host_change in handlers:handlers.remove(before_host_change)
