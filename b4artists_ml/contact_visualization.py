"""Read-only viewport feedback for authored animation contacts.

The overlay never changes animation or contact data.  It shows the selected
contact target, the evaluated limb point, and their current separation while
the sidebar reports the same timing weight used by contact correction.
"""
import math

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from . import contact_math as cm
from . import contacts
from . import posing
from . import quadruped_contacts
from . import workflow
from .rigs import detect_rig


_HANDLER = None
_COLORS = {
    'ACCEPTED': (0.18, 0.92, 0.45),
    'PROPOSED': (1.0, 0.58, 0.12),
    'REJECTED': (0.95, 0.18, 0.18),
}


def timing(item, frame):
    """Return the visible phase and the exact correction influence at a frame."""
    blend_in = item.blend_in if item.asymmetric_blend else item.blend
    blend_out = item.blend_out if item.asymmetric_blend else item.blend
    values = (item.start, item.end, item.blend, blend_in, blend_out, item.strength, frame)
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool)
               and math.isfinite(value) for value in values):
        raise ValueError('Contact timing and strength must be finite numbers')
    if item.start > item.end or min(item.blend,blend_in,blend_out) < 0 or not 0 <= item.strength <= 1:
        raise ValueError('Contact timing or strength is invalid')
    blend_in_frame = item.start - blend_in
    blend_out_frame = item.end + blend_out
    if frame < blend_in_frame:
        phase = 'Before'
    elif frame < item.start:
        phase = 'Blend In'
    elif frame <= item.end:
        phase = 'Hold'
    elif frame < blend_out_frame:
        phase = 'Blend Out'
    else:
        phase = 'After'
    row = dict(start=item.start, end=item.end, blend=item.blend,
               blend_in=blend_in,blend_out=blend_out,
               strength=item.strength)
    return dict(phase=phase, influence=cm.weight(row, frame),
                blend_in=blend_in_frame, start=item.start, end=item.end,
                blend_out=blend_out_frame)


def review_frame(item, operation):
    """Resolve one of the four non-mutating interval review boundaries."""
    boundaries = timing(item, float(item.start))
    key = {
        'GO_BLEND_IN': 'blend_in',
        'GO_START': 'start',
        'GO_END': 'end',
        'GO_BLEND_OUT': 'blend_out',
    }.get(operation)
    if key is None:
        raise ValueError('Unknown contact review boundary')
    return boundaries[key]


def _target_point(obj, item, scene):
    if item.prop_bound and item.limb in {'arm-L', 'arm-R', 'leg-L', 'leg-R'}:
        return Vector(contacts._resolved_contact(
            obj, contacts._row(item), scene)['point'])
    return Vector(item.point)


def _effector_point(obj, item):
    if item.limb in quadruped_contacts.LIMBS:
        _, _, mapping = quadruped_contacts._mapping(obj)
        row = mapping[item.limb]
        return quadruped_contacts._point(obj, row, item.offset)
    _, _, limbs = posing.bindings(obj)
    row = next(value for value in limbs if value['id'] == item.limb)
    matrix = workflow.display_world(obj) @ obj.pose.bones[row['joints'][2]].matrix
    return matrix @ Vector(item.offset)


def _marker_size(obj):
    matrix = workflow.display_world(obj)
    points = [matrix @ bone.head for bone in obj.pose.bones]
    if not points:
        return .05
    origin = points[0]
    return max(max((point - origin).length for point in points) * .018, .015)


def build_payload(obj, scene):
    """Build finite, read-only overlay primitives for the active rig."""
    state = getattr(obj, 'b4ml', None)
    if state is None or not state.show_contact_overlay:
        return []
    quadruped = detect_rig(obj.data.bones.keys()).family == 'quadruped'
    if not (state.show_quadruped_contacts if quadruped else state.show_contacts):
        return []
    if not state.contacts:
        return []
    limbs = set(quadruped_contacts.LIMBS) if quadruped else {
        'arm-L', 'arm-R', 'leg-L', 'leg-R'}
    if state.show_all_contact_overlays:
        indices = [index for index, item in enumerate(state.contacts)
                   if item.limb in limbs]
    elif (0 <= state.contact_index < len(state.contacts)
          and state.contacts[state.contact_index].limb in limbs):
        indices = (state.contact_index,)
    else:
        return []
    frame = scene.frame_current + scene.frame_subframe
    size = _marker_size(obj)
    payload = []
    for index in indices:
        item = state.contacts[index]
        try:
            target = _target_point(obj, item, scene)
            effector = _effector_point(obj, item)
            interval = timing(item, frame)
            if not all(math.isfinite(value) for point in (target, effector) for value in point):
                continue
        except (KeyError, StopIteration, TypeError, ValueError, ReferenceError, RuntimeError):
            continue
        base = _COLORS.get(item.review_state, _COLORS['REJECTED'])
        active = interval['influence'] > 0 and item.enabled and item.review_state != 'REJECTED'
        alpha = .95 if active else .3
        payload.append(dict(index=index, selected=index == state.contact_index,
                            target=tuple(target), effector=tuple(effector),
                            distance=(target - effector).length,
                            color=(*base, alpha), size=size,
                            phase=interval['phase'], influence=interval['influence'],
                            review_state=item.review_state, enabled=item.enabled))
    return payload


def _draw():
    changed_state = False
    try:
        context = bpy.context
        obj = workflow.active_rig(context)
        if obj is None or context.scene is None:
            return
        payload = build_payload(obj, context.scene)
        if not payload:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.5)
        changed_state = True
        for item in payload:
            target = Vector(item['target'])
            effector = Vector(item['effector'])
            size = item['size'] * (1.35 if item['selected'] else 1.0)
            vertices = [effector, target]
            for axis in (Vector((size, 0, 0)), Vector((0, size, 0)), Vector((0, 0, size))):
                vertices.extend((target - axis, target + axis))
            batch = batch_for_shader(shader, 'LINES', {'pos': vertices})
            shader.bind()
            shader.uniform_float('color', item['color'])
            batch.draw(shader)
    except Exception:
        # Viewport feedback must never interrupt animation work.
        return
    finally:
        if changed_state:
            try:
                gpu.state.line_width_set(1.0)
                gpu.state.blend_set('NONE')
            except Exception:
                pass


def register():
    global _HANDLER
    if _HANDLER is None and not bpy.app.background:
        _HANDLER = bpy.types.SpaceView3D.draw_handler_add(
            _draw, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global _HANDLER
    if _HANDLER is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_HANDLER, 'WINDOW')
        except (ReferenceError, RuntimeError):
            pass
        _HANDLER = None
