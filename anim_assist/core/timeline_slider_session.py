"""Absolute preview transactions using existing animation math."""
import math


class Transaction:
    def __init__(self, restore, apply, valid=lambda: True):
        self.restore, self.apply, self.valid = restore, apply, valid
        self.closed = False

    def preview(self, value):
        if self.closed or not self.valid(): raise ValueError('The original animation target is no longer available')
        if not math.isfinite(value): raise ValueError('Enter a finite slider value')
        self.restore()
        try: self.apply(value)
        except Exception:
            self.restore()
            raise

    def cancel(self):
        if not self.closed:
            self.restore()
            self.closed = True

    def commit(self):
        if self.closed or not self.valid(): raise ValueError('The original animation target is no longer available')
        self.closed = True


KEY_FIELDS=('handle_left_type','handle_right_type','interpolation','type','easing',
            'amplitude','back','period','select_control_point','select_left_handle','select_right_handle')


def snapshot(curves):
    return [(fc, [dict(co=tuple(k.co),left=tuple(k.handle_left),right=tuple(k.handle_right),
                    **{field:getattr(k,field) for field in KEY_FIELDS})
                 for k in fc.keyframe_points]) for fc in curves]


def restore_snapshot(saved):
    for fc, rows in saved:
        points=fc.keyframe_points
        while len(points)>len(rows): points.remove(points[-1],fast=True)
        while len(points)<len(rows):
            row=rows[len(points)]; points.insert(*row['co'],options={'FAST'})
        for k,row in zip(points,rows):
            for field in KEY_FIELDS: setattr(k,field,row[field])
            k.co=row['co']; k.handle_left=row['left']; k.handle_right=row['right']
        fc.update()


def capture(context,action):
    from .fcurve_compat import get_fcurves
    from . import curve_tools as math_tools, p6_retime_math as retime, breakdown_core as breakdown
    from ..operators import curve_tool_ops as curves_ops
    from ..operators.p3_breakdown_ops import _resolve_target, _options_from_scene
    obj=context.active_object
    if not obj or not obj.animation_data or not obj.animation_data.action:
        raise ValueError('Select an object with editable animation')
    data=obj.animation_data; native_action=data.action; scene=context.scene
    if obj.library and not obj.override_library or native_action.library and not native_action.override_library:
        raise ValueError('Use local or overridden animation data')
    frame=scene.frame_current_final
    options=None; bones=None; curve_data=[]; pivot=frame; snap=False
    if action=='DRAG':
        obj,bones=_resolve_target(context)
        options=_options_from_scene(context,target_frame=frame)
        curves=breakdown.iter_target_fcurves(obj,bones,options.mask,options.exclusion)
    elif action in {'SCALE_DRAG','OFFSET_DRAG'}:
        curves=[fc for fc in get_fcurves(native_action,anim_data=data) if not fc.lock and not fc.hide]
        p6=scene.anim_assist_p6
        pivot=retime.resolve_pivot(p6.anchor_mode,retime.collect_key_frames(curves),frame,custom_frame=p6.pivot_frame)
        snap=p6.modal_snap
    else:
        curves=[fc for fc in curves_ops._editable_fcurves(context) if not fc.lock and not fc.hide]
        ref_frame=scene.anim_assist.reference_frame or frame
        for fc in curves:
            keys=curves_ops._snapshot_keys(fc)
            selected=[i for i,k in enumerate(keys) if k.selected]
            if not selected or (action=='EASE' and len(selected)<2): continue
            curve_data.append((fc,keys,selected,fc.evaluate(ref_frame)))
        curves=[row[0] for row in curve_data]
    if not curves: raise ValueError('Select editable keys that match the tool mask')
    saved=snapshot(curves)

    def refresh():
        # Keep the playhead fixed and evaluate the updated pose, including bones.
        base=math.floor(frame)
        scene.frame_set(base,subframe=frame-base)

    def restore():
        restore_snapshot(saved)
        refresh()

    def valid():
        try:
            return obj.animation_data.action==native_action and context.scene==scene
        except (ReferenceError, AttributeError): return False

    def apply(value):
        factor=value/100.
        if action=='DRAG':
            options.factor=factor
            breakdown.apply_breakdown(context,obj,bones,options)
        elif action=='SCALE_DRAG': retime.apply_scale(curves,pivot,factor,snap=snap)
        elif action=='OFFSET_DRAG': retime.apply_offset(curves,value,snap=snap)
        else:
            for fc,keys,selected,reference in curve_data:
                chosen=[keys[i] for i in selected]
                if action=='SMOOTH': values=math_tools.smooth_keys(keys,selected,factor)
                elif action=='NEIGHBORS': values=math_tools.blend_to_neighbor(keys,selected,factor)
                elif action=='FRAME': values=math_tools.blend_toward_value(chosen,reference,factor)
                elif action=='AMPLIFY': values=math_tools.push_pull(chosen,reference,factor)
                elif action=='EASE': values=math_tools.ease_to_ease(chosen,factor)
                else: raise ValueError('Unknown scalar tool')
                if not all(math.isfinite(v) for v in values): raise ValueError('Adjustment produced an invalid value')
                curves_ops._write_values(fc,selected,values)
        refresh()

    return Transaction(restore,apply,valid)
