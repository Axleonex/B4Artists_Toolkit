"""Real-host inventory, panel draws and independent semantic baseline oracles.

Run only inside Bforartists, through run_anim_assist_regression.py.
Unexecuted operators remain PENDING in the coverage matrix.
"""
from __future__ import annotations

import inspect
import json
import math
from pathlib import Path
import struct
import sys
import traceback
import types
import wave

import bpy

ROOT, OUTPUT = map(Path, sys.argv[sys.argv.index('--') + 1:][:2])
EVIDENCE = Path(sys.argv[sys.argv.index('--') + 3]) if len(sys.argv[sys.argv.index('--') + 1:]) > 2 else ROOT
EVIDENCE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))
import anim_assist as addon
from anim_assist.core.fcurve_compat import get_fcurves
from anim_assist.core import p10_tool_registry as registry
from anim_assist.ui import header_menus

RESULT = {'host': {'version': bpy.app.version_string,
    'branch': bpy.app.build_branch.decode(), 'build_hash': bpy.app.build_hash.decode()},
    'checks': [], 'census': {}, 'passed': False}
INVOKED = []


def check(name, operators, function):
    entry = {'name': name, 'operators': operators, 'status': 'FAIL'}
    start = len(INVOKED)
    try:
        function()
        entry['status'] = 'PASS'
    except Exception:
        entry['error'] = traceback.format_exc()
    RESULT['checks'].append(entry)
    entry['invoked_operators'] = INVOKED[start:]
    print(name + ': ' + entry['status'], flush=True)


def clean():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None


def animated(name='Timing fixture'):
    clean()
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for frame, value in ((1, 0.), (11, 10.), (21, 0.)):
        obj.location.x = value
        obj.keyframe_insert(data_path='location', frame=frame)
    bpy.context.scene.frame_set(6)
    return obj


def curves(obj):
    return get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)


def keys(obj):
    return sorted({round(p.co.x, 4) for fc in curves(obj) for p in fc.keyframe_points})


def runop(op_name, **kwargs):
    INVOKED.append('animassist.' + op_name)
    result = getattr(bpy.ops.animassist, op_name)(**kwargs)
    assert result == {'FINISHED'}, (op_name, result)


def record_census():
    operators = []
    search = {t.op_id for t in registry.all_tools()}
    ids = {c.bl_idname for c in addon.ops_pkg.CLASSES
        if isinstance(c, type) and issubclass(c, bpy.types.Operator) and c.is_registered}
    ids |= {'animassist.' + name for name in dir(bpy.ops.animassist)}
    for op_id in sorted(ids):
        namespace, name = op_id.split('.')
        rna = getattr(getattr(bpy.ops, namespace), name).get_rna_type()
        cls = bpy.types.Operator.bl_rna_get_subclass_py(rna.identifier)
        props = []
        for p in rna.properties:
            if p.identifier == 'rna_type':
                continue
            item = {'id': p.identifier, 'type': p.type, 'description': p.description}
            if hasattr(p, 'default_array') and getattr(p, 'is_array', False):
                item['default'] = list(p.default_array)
            elif hasattr(p, 'default'):
                default = p.default
                item['default'] = sorted(default) if isinstance(default, set) else default
            if p.type == 'ENUM':
                item['items'] = [e.identifier for e in p.enum_items]
            props.append(item)
        file = inspect.getsourcefile(cls) if cls else None
        operators.append({'id': op_id, 'label': rna.name,
            'description': rna.description, 'doc': inspect.getdoc(cls) if cls else '',
            'source': str(Path(file).relative_to(ROOT)) if file else None,
            'line': inspect.getsourcelines(cls)[1] if cls else None,
            'options': sorted(getattr(cls, 'bl_options', set())) if cls else [],
            'searchable': op_id in search, 'properties': props})
    panel_classes = [c for c in addon.ui.CLASSES if isinstance(c, type)
                     and issubclass(c, bpy.types.Panel) and c.is_registered]
    menus = {}
    for space, (_, _, groups) in header_menus.MENUS.items():
        menus[space] = [{'group': label, 'operators': ['animassist.' + e for e in entries if e]}
                        for _, label, _, entries in groups]
    RESULT['census'] = {'operators': operators,
        'panels': [{'id': c.__name__, 'space': c.bl_space_type, 'region': c.bl_region_type,
                    'parent': getattr(c, 'bl_parent_id', '')} for c in panel_classes],
        'menus': menus, 'search_ids': sorted(search),
        'pie_ids': ['animassist.' + op for op, _, _ in header_menus.PIE_SLOTS],
        'native_toolshelf_capability': 'show_toolshelf_tabs' in bpy.types.SpaceView3D.bl_rna.properties}
    def descendants(base):
        for cls in base.__subclasses__():
            yield cls
            yield from descendants(cls)
    groups = {}
    for cls in descendants(bpy.types.PropertyGroup):
        if not cls.__module__.startswith('anim_assist') or not cls.is_registered: continue
        groups[cls.__name__] = [{'id': p.identifier, 'type': p.type,
            'description': p.description, 'default':
                list(p.default_array) if getattr(p, 'is_array', False) else
                sorted(p.default) if isinstance(getattr(p, 'default', None), set) else
                getattr(p, 'default', None)} for p in cls.bl_rna.properties if p.identifier != 'rna_type']
    RESULT['census']['property_groups'] = groups
    assert len(operators) == len({o['id'] for o in operators})

    class Layout:
        def __init__(self, calls): self.calls = calls
        def __getattr__(self, name):
            def call(*args, **kwargs):
                if name == 'operator':
                    self.calls.append(args[0])
                    return types.SimpleNamespace()
                if name == 'panel': return Layout(self.calls), Layout(self.calls)
                return Layout(self.calls)
            return call

    class Proxy:
        def __init__(self, cls, calls): self.cls, self.layout = cls, Layout(calls)
        def __getattr__(self, name):
            value = getattr(self.cls, name)
            return types.MethodType(value, self) if callable(value) else value

    failures, draws, routes = [], [], {}
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    animated('Panel draw fixture')
    for state in ('animated_object', 'empty_selection'):
        if state == 'empty_selection': clean()
        for space in ('GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'PROPERTIES'):
            area.type = space
            if space == 'PROPERTIES':
                try:
                    area.spaces.active.context = 'SCENE'
                except TypeError:
                    pass  # Background hosts may expose no tabs until the area is redrawn.
            with bpy.context.temp_override(area=area):
                for cls in panel_classes:
                    if cls.bl_space_type != space: continue
                    calls = []
                    try:
                        visible = not hasattr(cls, 'poll') or cls.poll(bpy.context)
                        if visible: cls.draw(Proxy(cls, calls), bpy.context)
                        draws.append({'panel': cls.__name__, 'state': state, 'visible': visible})
                        for op in calls: routes.setdefault(op, set()).add(cls.__name__)
                    except Exception:
                        failures.append({'panel': cls.__name__, 'state': state,
                                         'error': traceback.format_exc()})
    RESULT['census']['panel_routes'] = {op: sorted(paths) for op, paths in routes.items()}
    RESULT['census']['draws'] = draws
    RESULT['census']['draw_failures'] = failures
    assert not failures, failures
    area.type = 'GRAPH_EDITOR'


def breakdown(factor, operator):
    obj = animated('Breakdown fixture')
    before = [(fc.data_path, fc.array_index, len(fc.keyframe_points)) for fc in curves(obj)]
    runop(operator, **({'factor': factor} if operator == 'breakdown_weighted' else {}))
    x = next(fc for fc in curves(obj) if fc.array_index == 0)
    point = next(p for p in x.keyframe_points if abs(p.co.x - 6) < 1e-5)
    assert abs(point.co.y - factor * 10) < 1e-5, (factor, tuple(point.co))
    assert len(x.keyframe_points) == 4
    assert before[0][2] == 3


def retime():
    obj = animated()
    p6 = bpy.context.scene.anim_assist_p6
    p6.anchor_mode = 'CUSTOM'; p6.pivot_frame = 0; p6.range_mode = 'SCENE'
    runop('p6_scale_keys', scale_factor=2)
    assert keys(obj) == [2., 22., 42.], keys(obj)
    runop('p6_offset_keys', offset_frames=3)
    assert keys(obj) == [5., 25., 45.], keys(obj)
    bpy.context.scene.frame_set(20)
    runop('p6_ripple_forward', ripple_delta=4)
    assert keys(obj) == [5., 29., 49.], keys(obj)


def metadata():
    from anim_assist.core import key_metadata as meta
    from anim_assist.core.context_utils import key_identity
    obj = animated('Metadata fixture')
    for fc in curves(obj):
        fc.select = True
        for p in fc.keyframe_points: p.select_control_point = True
    runop('tag_selected_keys', tag='baseline')
    fc = curves(obj)[0]; ident = key_identity(obj.name, fc, 1)
    assert meta.get_meta(bpy.context.scene, ident).tag == 'baseline'
    runop('protect_selected_keys', protected=True)
    assert meta.get_meta(bpy.context.scene, ident).protected
    runop('clear_tag_selected_keys')
    assert meta.get_meta(bpy.context.scene, ident).tag == ''


def offsets():
    obj = animated('Offset fixture')
    p4 = bpy.context.scene.anim_assist_p4
    p4.scope = 'CURRENT_FRAME'; p4.push_amount = 2
    p4.active_preset = 'NORMAL'; p4.fine_step = False; p4.falloff_shape = 'NONE'
    p4.selected_channels_only = False; p4.skip_muted = False
    bpy.context.scene.frame_set(11)
    runop('p4_push_x')
    fc = next(fc for fc in curves(obj) if fc.array_index == 0)
    assert abs(fc.evaluate(11) - 12.) < 1e-5, fc.evaluate(11)
    runop('p4_pull_x')
    assert abs(fc.evaluate(11) - 10.) < 1e-5, fc.evaluate(11)


def matching():
    obj = animated('Match fixture'); obj.animation_data_clear()
    obj.location = (3, 4, 5); obj.scale = (2, 3, 4)
    bpy.context.view_layer.update()
    p8 = bpy.context.scene.anim_assist_p8
    p8.maintain_offset = False; p8.auto_key_switch = False
    p8.match_channels = 'LOCATION'
    runop('p8_match_to_world')
    assert obj.location.length < 1e-5, tuple(obj.location)
    assert tuple(obj.scale) == (2., 3., 4.), tuple(obj.scale)


def paired_armature():
    clean()
    arm = bpy.data.armatures.new('Paired bone data')
    obj = bpy.data.objects.new('Paired rig', arm)
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    for name, x in (('hand.L', 1.), ('hand.R', -1.), ('jaw', 0.)):
        bone = arm.edit_bones.new(name)
        bone.head = (x, 0, 0); bone.tail = (x, 0, 1)
    bpy.ops.object.mode_set(mode='POSE')
    arm.bones.active = arm.bones['hand.L']
    from anim_assist.core.bone_utils import set_pose_bone_selected
    set_pose_bone_selected(obj.pose.bones['hand.L'], True)
    return obj


def mirror():
    obj = paired_armature()
    left, right = obj.pose.bones['hand.L'], obj.pose.bones['hand.R']
    left.location = (2, 3, 4)
    runop('p9_match_opposite_to_active')
    assert (right.location - left.location).length < 1e-5
    right.location = (0, 0, 0)
    runop('p9_mirror_pose')
    assert abs(right.location.x + 2) < 1e-5, tuple(right.location)
    assert abs(right.location.y - 3) < 1e-5, tuple(right.location)
    assert abs(right.location.z - 4) < 1e-5, tuple(right.location)
    clean()


def locator():
    from anim_assist.core import p7_session as session
    obj = animated('Locator owner'); obj.animation_data_clear(); obj.location = (2, 4, 6)
    bpy.context.view_layer.update()
    before = set(bpy.data.objects.keys())
    runop('p7_create_locator')
    created = set(bpy.data.objects.keys()) - before
    assert len(created) == 1, created
    helper = bpy.data.objects[next(iter(created))]
    assert (helper.location - obj.location).length < 1e-5
    p7 = bpy.context.scene.anim_assist_p7
    sid = p7.active_session_id
    assert session.get_session(sid) is not None
    # Purge the actual created object and its session via the public action.
    runop('p7_purge_artifacts')
    assert not set(created) & set(bpy.data.objects.keys())
    assert obj.name in bpy.data.objects


def layers():
    obj = animated('Layer owner')
    p11 = bpy.context.scene.anim_assist_p11
    runop('p11_init_layers')
    assert p11.layers[0].is_base_layer and p11.layers[0].action_name == obj.animation_data.action.name
    initial = len(p11.layers)
    runop('p11_add_layer', name='Baseline additive', blend_mode='ADDITIVE', weight=.25)
    layer = p11.layers[-1]
    assert len(p11.layers) == initial + 1 and layer.blend_mode == 'ADDITIVE'
    assert abs(layer.weight - .25) < 1e-6 and layer.action_name in bpy.data.actions
    p11.active_layer_index = len(p11.layers) - 1
    runop('p11_remove_layer')
    assert len(p11.layers) == initial


def lipsync():
    from anim_assist.core import p12_lipsync_engine as engine
    clean()
    mesh = bpy.data.meshes.new('Face data')
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    obj = bpy.data.objects.new('Lipsync face', mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.shape_key_add(name='Basis'); obj.shape_key_add(name='mouth_A')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    audio = EVIDENCE / 'fixture.wav'
    with wave.open(str(audio), 'wb') as dst:
        dst.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        dst.writeframes(b''.join(struct.pack('<h', int(20000 * math.sin(2 * math.pi * 220 * i / 8000)))
            if 2000 < i < 6000 else b'\x00\x00' for i in range(8000)))
    p12 = bpy.context.scene.anim_assist_p12
    p12.layer_links.clear(); p12.shape_key_wiring.clear()
    link = p12.layer_links.add(); link.layer_name = 'Baseline lipsync'; link.audio_path = str(audio)
    link.mesh_name = obj.name; link.target_kind = 'SHAPE_KEYS'; link.mode = 'SHIPPED'
    link.backend = 'AMPLITUDE'; link.anticipation_frames = 0
    wiring = p12.shape_key_wiring.add(); wiring.viseme_name = 'A'; wiring.shape_key_name = 'mouth_A'
    bpy.ops.wm.save_as_mainfile(filepath=str(EVIDENCE / 'lipsync-bake-repro.blend'))
    runop('p12_bake_lipsync')
    assert len(link.cue_table) > 0, 'Real audio analysis produced no cues'
    sk = mesh.shape_keys
    action = sk.animation_data.action
    fcs = get_fcurves(action, anim_data=sk.animation_data)
    RESULT['lipsync_diagnostic'] = {'cues': len(link.cue_table),
        'legacy_action_fcurves_attribute': hasattr(action, 'fcurves'),
        'curves_written': len(fcs), 'engine_ensure_returns_none':
            engine._ensure_fcurve(action, 'key_blocks["mouth_A"].value', 0) is None,
        'reproduction_blend': str(EVIDENCE / 'lipsync-bake-repro.blend'), 'audio': str(audio)}
    if not fcs:
        from anim_assist.core.fcurve_compat import ensure_fcurve
        compat = ensure_fcurve(action, 'key_blocks["mouth_A"].value', 0, anim_data=sk.animation_data)
        RESULT['lipsync_diagnostic']['existing_compat_helper_creates_curve'] = compat is not None
        RESULT['lipsync_diagnostic']['correct_slot_type'] = sk.animation_data.action_slot.target_id_type
        # This diagnoses the API boundary; it does not rescue or pass the bake.
    assert fcs and sum(len(fc.keyframe_points) for fc in fcs) > 0, 'Configured bake reported FINISHED but wrote no real shape-key curves'
    fc = fcs[0]; point = fc.keyframe_points[0]; frame = round(point.co.x)
    point.co.y = .42
    # The engine reads small values as key indices (as the Mark Manual operator
    # passes them); pass index 0 so the frame number is never misread.
    engine.mark_manual_override(action, fc.data_path, fc.array_index, 0, anim_data=sk.animation_data)
    runop('p12_rebake')
    fcs = get_fcurves(action, anim_data=sk.animation_data)
    point = next(p for c in fcs for p in c.keyframe_points if round(p.co.x) == frame)
    assert abs(point.co.y - .42) < 1e-6, 'Manual shape key lost on rebake'


def lipsync_layer_slot():
    """A detached layer Action keyed by Animation Layers keeps one slot."""
    from anim_assist.core import fcurve_compat
    from anim_assist.core.p12_lipsync_engine import action_context
    clean()
    rig = bpy.data.objects.new('Lipsync slot rig', bpy.data.armatures.new('Lipsync slot rig'))
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.update()
    layer = bpy.data.actions.new('Lipsync slot layer')
    curve = fcurve_compat.new_fcurve(layer, 'pose.bones["jaw"].rotation_euler', 0)
    curve.keyframe_points.insert(1, .5)
    if hasattr(layer, 'slots'):
        context = action_context(layer, owner=rig)
        assert len(layer.slots) == 1, [s.name_display for s in layer.slots]
        assert context.action_slot == layer.slots[0]
        assert action_context(layer, owner=rig, create=False).action_slot == layer.slots[0]


def recents_order():
    """Repeat Last uses the newest entry; 12.1.0 files stored oldest-first."""
    from anim_assist.core.p10_properties import get_p10, recents_newest_first, sort_recents
    p10 = get_p10(bpy.context)
    p10.recents.clear()
    for index, op_id in enumerate(('animassist.oldest', 'animassist.middle', 'animassist.newest')):
        item = p10.recents.add()
        item.op_id, item.label, item.timestamp = op_id, op_id, 1000.0 + index
    assert recents_newest_first(p10)[0].op_id == 'animassist.newest'
    sort_recents(p10)
    assert [r.op_id for r in p10.recents] == ['animassist.newest', 'animassist.middle', 'animassist.oldest']
    p10.recents.clear()


def negative():
    obj = animated('Untouched negative fixture')
    before = [(fc.data_path, fc.array_index, [tuple(p.co) for p in fc.keyframe_points]) for fc in curves(obj)]
    clean()
    for name in ('breakdown_current_frame', 'p6_scale_keys', 'p8_match_to_world', 'p9_mirror_pose'):
        assert not getattr(bpy.ops.animassist, name).poll(), name
    after = [(fc.data_path, fc.array_index, [tuple(p.co) for p in fc.keyframe_points]) for fc in curves(obj)]
    assert before == after


addon.register()
try:
    check('runtime_census_and_all_panel_draws', [], record_census)
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    area.type = 'GRAPH_EDITOR'
    with bpy.context.temp_override(area=area):
        for name, factor in (('breakdown_midpoint', .5), ('breakdown_favor_prev', .25),
                             ('breakdown_favor_next', .75), ('breakdown_weighted', .3)):
            check(name + '_values', ['animassist.' + name], lambda n=name, f=factor: breakdown(f, n))
        check('retime_scale_offset_ripple_frames', ['animassist.' + n for n in
            ('p6_scale_keys', 'p6_offset_keys', 'p6_ripple_forward')], retime)
        check('metadata_tag_protection_clear', ['animassist.' + n for n in
            ('tag_selected_keys', 'protect_selected_keys', 'clear_tag_selected_keys')], metadata)
        check('offset_push_pull_values', ['animassist.p4_push_x', 'animassist.p4_pull_x'], offsets)
        check('object_match_scope_values', ['animassist.p8_match_to_world'], matching)
        check('paired_bone_match_mirror_values', ['animassist.p9_match_opposite_to_active', 'animassist.p9_mirror_pose'], mirror)
        check('locator_create_position_and_purge', ['animassist.p7_create_locator', 'animassist.p7_purge_artifacts'], locator)
        check('layer_action_creation_and_removal', ['animassist.' + n for n in
            ('p11_init_layers', 'p11_add_layer', 'p11_remove_layer')], layers)
        check('configured_shape_key_audio_bake_and_manual_rebake', ['animassist.p12_bake_lipsync', 'animassist.p12_rebake'], lipsync)
        check('lipsync_layer_action_keeps_single_slot', [], lipsync_layer_slot)
        check('recents_newest_first_with_legacy_order', [], recents_order)
        check('empty_selection_rejects_without_key_mutation', [], negative)
    RESULT['passed'] = bool(RESULT['checks']) and all(c['status'] == 'PASS' for c in RESULT['checks'])
finally:
    clean()
    addon.unregister()
    OUTPUT.write_text(json.dumps(RESULT, indent=2), encoding='utf-8')
assert RESULT['passed'], 'Semantic baseline failures: ' + ', '.join(c['name'] for c in RESULT['checks'] if c['status'] != 'PASS')
