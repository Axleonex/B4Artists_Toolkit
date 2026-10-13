"""Disposable GUI verification of exact packaged Anim Assist; no user files.

Pass package staging parent after --. The first invocation inspects native RNA;
the completed suite will record independent numeric/structural effect oracles.
"""
from pathlib import Path
import json
import sys
import traceback
import math
import hashlib

import bpy
import addon_utils
import os
isolated_config = Path(os.environ['BLENDER_USER_CONFIG']).resolve()
assert isolated_config.is_dir() and Path(bpy.utils.user_resource('CONFIG')).resolve() == isolated_config

DEST = Path(__file__).resolve().parent
package_parent = sys.argv[sys.argv.index('--package-parent')+1] if '--package-parent' in sys.argv else sys.argv[sys.argv.index('--')+1]
sys.path.insert(0, package_parent)
bpy.context.preferences.view.show_splash = False
addon_utils.enable('B4_anim_assist', default_set=True, persistent=False)
if '--scale' in sys.argv:
    bpy.context.preferences.view.ui_scale = float(sys.argv[sys.argv.index('--scale')+1])


SETUP = {'stage': 0}
MATRIX_TARGET = None
if '--matrix' in sys.argv or '--demo' in sys.argv:
    from B4_anim_assist.prefs import get_prefs
    get_prefs().timeline_toolbar_row = False


def join_areas(source, target):
    with bpy.context.temp_override(area=source):
        bpy.ops.screen.area_join(source_xy=(source.x+source.width//2, source.y+source.height//2),
                                 target_xy=(target.x+target.width//2, target.y+target.height//2))


def ensure_test_strip():
    global MATRIX_TARGET
    from B4_anim_assist.ui.timeline_strip import is_strip, is_timeline
    screen = bpy.context.window.screen
    if '--matrix' in sys.argv or '--demo' in sys.argv:
        from B4_anim_assist.prefs import get_prefs
        stage=SETUP['stage']
        view=next((a for a in screen.areas if a.type=='VIEW_3D'),None)
        if stage==0:
            timeline=next(a for a in screen.areas if is_timeline(a))
            join_areas(view,timeline)
        elif stage==1:
            props=next(a for a in screen.areas if a.type=='PROPERTIES')
            outliner=next(a for a in screen.areas if a.type=='OUTLINER')
            join_areas(props,outliner)
        elif stage==2:
            props=next(a for a in screen.areas if a.type=='PROPERTIES')
            join_areas(view,props)
        elif stage==3:
            with bpy.context.temp_override(area=view):
                bpy.ops.screen.area_split(direction='HORIZONTAL',factor=.22)
            timeline = next(a for a in screen.areas if a != view)
            timeline.type='DOPESHEET_EDITOR';timeline.spaces.active.mode='TIMELINE'
            MATRIX_TARGET=timeline
        elif stage==4:
            desired=float(sys.argv[sys.argv.index('--logical-width')+1])*bpy.context.preferences.system.ui_scale if '--logical-width' in sys.argv else MATRIX_TARGET.width
            if MATRIX_TARGET.width>desired+4:
                with bpy.context.temp_override(area=MATRIX_TARGET):
                    bpy.ops.screen.area_split(direction='VERTICAL',factor=desired/MATRIX_TARGET.width)
        elif stage==5:
            get_prefs().timeline_toolbar_row=True
            return None
        SETUP['stage']+=1
        return .15
    if not any(is_strip(a) for a in screen.areas):
        timeline=next(a for a in screen.areas if is_timeline(a))
        with bpy.context.temp_override(area=timeline):
            result=bpy.ops.screen.area_move(x=timeline.x+timeline.width//2,y=timeline.y+timeline.height+1,delta=150)
            print('DISPOSABLE TIMELINE RESIZE',sorted(result),flush=True)
    if '--demo' in sys.argv:
        from B4_anim_assist.prefs import get_prefs
        get_prefs().timeline_toolbar_row=True
    return None


bpy.app.timers.register(ensure_test_strip, first_interval=.5 if '--demo' in sys.argv else .05)


def inspect_runtime():
    from B4_anim_assist.ui.timeline_strip import is_strip
    from B4_anim_assist.ui.timeline_catalog import ACTIONS
    window = bpy.context.window
    event = window.bl_rna.functions.get('event_simulate')
    result = {
        'host': bpy.app.version_string,
        'host_binary': bpy.app.binary_path,
        'actual_bforartists_feature_present': 'show_toolshelf_tabs' in bpy.types.SpaceView3D.bl_rna.properties,
        'event_simulate': [{ 'name': p.identifier, 'type': p.type,
            'enum': list(p.enum_items.keys()) if p.type == 'ENUM' else None}
            for p in event.parameters] if event else None,
        'areas': [{'type': a.type, 'is_strip': is_strip(a),
            'x': a.x, 'y': a.y, 'w': a.width, 'h': a.height}
            for a in bpy.context.screen.areas],
        'scene_properties': {},
        'operator_properties': {},
    }
    for attr in ('anim_assist_p3', 'anim_assist_p6', 'anim_assist_p7', 'anim_assist_p8', 'anim_assist_p9'):
        props = getattr(bpy.context.scene, attr)
        result['scene_properties'][attr] = {p.identifier: str(getattr(props, p.identifier))
            for p in props.bl_rna.properties if p.identifier != 'rna_type'}
    for suffix in sorted({r[0] for r in ACTIONS.values()}):
        rna = getattr(bpy.ops.animassist, suffix).get_rna_type()
        result['operator_properties'][suffix] = {p.identifier: {
            'default': str(getattr(p, 'default', '')), 'type': p.type,
            'enum': list(p.enum_items.keys()) if p.type == 'ENUM' else None}
            for p in rna.properties if p.identifier != 'rna_type'}
    (DEST/'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    bpy.ops.screen.screenshot(filepath=str(DEST/'toolbar.png'))
    bpy.ops.wm.quit_blender()


from B4_anim_assist.core.fcurve_compat import get_fcurves
from B4_anim_assist.ui.timeline_catalog import ACTIONS, GROUPS
from B4_anim_assist.ui.timeline_strip import is_strip, is_timeline

MODALS = {'DRAG', 'NEIGHBORS', 'FRAME', 'EASE', 'AMPLIFY', 'SMOOTH',
          'SCALE_DRAG', 'OFFSET_DRAG'}
CASES = [(key, False) for key in ACTIONS] + [(key, True) for key in sorted(MODALS)]
if '--keys' in sys.argv:
    wanted = set(sys.argv[sys.argv.index('--keys')+1].split(','))
    CASES = [case for case in CASES if case[0] in wanted]
if '--output' in sys.argv:
    DEST = Path(sys.argv[sys.argv.index('--output')+1])
    DEST.mkdir(parents=True, exist_ok=True)
RESULT = {'host': bpy.app.version_string, 'actual_bforartists':
    'show_toolshelf_tabs' in bpy.types.SpaceView3D.bl_rna.properties,
    'method': 'Exact ZIP; isolated GUI; toolbar dispatch; synthetic fixtures; native Blender event_simulate',
    'expected_release_sha256': hashlib.sha256((Path(__file__).resolve().parents[4]/'releases/b4_anim_assist_v12.5.0.zip').read_bytes()).hexdigest() if (Path(__file__).resolve().parents[4]/'releases/b4_anim_assist_v12.5.0.zip').exists() else None,
    'checks': [], 'limitations': ['Not actual Bforartists or owner usability.',
    'Native toolbar dispatch is invoked with bpy; menu hit targets are separately pending.',
    'Expected outputs authored by the same audit agent; independent review is still required.']}
STATE = {'index': 0, 'phase': 'setup'}


def areas():
    screen = bpy.context.window.screen
    strip = next(a for a in screen.areas if is_strip(a) and (MATRIX_TARGET is None or strip_module_pair(a) == MATRIX_TARGET))
    return strip, strip_module_pair(strip), next(a for a in screen.areas if a.type == 'VIEW_3D')


def window_region(area):
    return next(r for r in area.regions if r.type == 'WINDOW')


def call_toolbar(key):
    strip, timeline, view = areas()
    if '--direct' in sys.argv:
        with bpy.context.temp_override(area=timeline, region=window_region(timeline)):
            return sorted(getattr(bpy.ops.animassist,ACTIONS[key][0])(
                'INVOKE_DEFAULT', '--direct-undo' in sys.argv, **ACTIONS[key][1]))
    with bpy.context.temp_override(area=strip, region=next(r for r in strip.regions if r.type == 'HEADER')):
        return sorted(bpy.ops.animassist.timeline_tool('INVOKE_DEFAULT', action=key))


def native_event(kind, value='NOTHING', x=400, **modifiers):
    timeline=next((a for a in bpy.context.window.screen.areas if is_timeline(a)),None)
    bpy.context.window.event_simulate(type=kind, value=value, x=x, y=timeline.y+12 if timeline else 45, **modifiers)


def curves(name='AA_Test'):
    obj = bpy.data.objects.get(name)
    if not obj or not obj.animation_data or not obj.animation_data.action:
        return []
    return list(get_fcurves(obj.animation_data.action, anim_data=obj.animation_data))


def key_rows():
    fc = next((f for f in curves() if f.data_path == 'location' and f.array_index == 0), None)
    return [[round(k.co.x, 5), round(k.co.y, 5)] for k in fc.keyframe_points] if fc else []


def snapshot():
    objects = {}
    for obj in bpy.data.objects:
        objects[obj.name] = {'loc': list(obj.location), 'rot': list(obj.rotation_euler),
            'curves': [[fc.data_path, fc.array_index, [[round(k.co.x, 5), round(k.co.y, 5),
                bool(k.select_control_point), k.type, k.handle_left_type, k.handle_right_type,
                list(k.handle_left), list(k.handle_right), bool(k.select_left_handle),
                bool(k.select_right_handle), k.easing, k.amplitude, k.back, k.period]
                for k in fc.keyframe_points]] for fc in curves(obj.name)],
            'constraints': [(c.type, c.target.name if getattr(c, 'target', None) else None) for c in obj.constraints]}
        if obj.type == 'ARMATURE':
            objects[obj.name]['bones'] = {b.name: {'loc': list(b.location), 'selected': b.select}
                for b in obj.pose.bones}
    scene = bpy.context.scene
    return {'objects': objects, 'reference': scene.anim_assist.reference_frame,
        'mask': [scene.anim_assist.mask.enabled, scene.anim_assist.mask.start_frame, scene.anim_assist.mask.end_frame],
        'overlay': scene.anim_assist_p5.overlay_enabled}


def fixture(key):
    strip, timeline, view = areas()
    scene = bpy.context.scene
    scene.anim_assist.anim_offset_active = False
    with bpy.context.temp_override(area=view, region=window_region(view)):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.animassist.p5_disable_overlay()
    from B4_anim_assist.core import p7_session
    p7_session._sessions.clear()
    scene.anim_assist_p7.active_session_id = ''
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.frame_start, scene.frame_end = 1, 21
    p3, p6, p7 = scene.anim_assist_p3, scene.anim_assist_p6, scene.anim_assist_p7
    p3.factor, p3.modal_sensitivity, p3.inbetween_count = .5, 200, 2
    p6.range_mode, p6.anchor_mode, p6.modal_snap = 'SCENE', 'FIRST', False
    p6.offset_frames, p6.ripple_delta = 2, 2
    p7.bake_range_mode, p7.bake_step, p7.bake_channels = 'SCENE', 2, 'LOC'
    p7.smart_bake_tolerance = .0001
    scene.anim_assist.reference_frame = 1
    scene.anim_assist.mask.enabled = False
    obj = bpy.data.objects.new('AA_Test', None)
    scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    frames = (1, 6, 11, 21) if key != 'SNAP' else (1.2, 6.3, 11.2, 20.8)
    for frame, value in zip(frames, (0, 3, 10, 0)):
        obj.location.x = value
        obj.keyframe_insert(data_path='location', index=0, frame=frame)
    fc = curves()[0]
    if key == 'REDUCE':
        fc.keyframe_points.insert(3, 1.2)
    for k in fc.keyframe_points:
        k.interpolation = 'LINEAR'
        k.select_control_point = k.co.x in (6, 11)
        k.type = 'KEYFRAME'
        k.handle_left_type = k.handle_right_type = 'FREE'
    if key == 'TYPE_KEYFRAME':
        for k in fc.keyframe_points:
            if k.select_control_point: k.type = 'BREAKDOWN'
    if key in ('B25','B50','B75','PUSH_PREV','PULL_PREV','PULL_NEXT','PUSH_NEXT','DRAG','INBETWEEN'):
        fc.keyframe_points.remove(fc.keyframe_points[1])
    if key == 'DRAG':
        for i,k in enumerate(fc.keyframe_points):
            k.type = ('EXTREME','BREAKDOWN','MOVING_HOLD')[i % 3]
            k.select_left_handle = i == 1
            k.select_right_handle = i == 2
            k.easing = 'EASE_IN_OUT'
            k.amplitude, k.back, k.period = .7, .8, .9
    if key in ('INBETWEEN', 'INBETWEENS'):
        for k in fc.keyframe_points: k.select_control_point = k.co.x in (1, 11)
    if key == 'EASE':
        for k in fc.keyframe_points: k.select_control_point = True
    if key == 'SELECT_BREAKDOWNS':
        for k in fc.keyframe_points: k.select_control_point = False
        fc.keyframe_points[1].type = 'BREAKDOWN'
    if key.startswith('HANDLE_'):
        for k in fc.keyframe_points: k.handle_left_type = k.handle_right_type = 'VECTOR'
        if key == 'HANDLE_VECTOR':
            for k in fc.keyframe_points: k.handle_left_type = k.handle_right_type = 'FREE'
    scene.frame_set(6)
    other = bpy.data.objects.new('AA_Untouched', None)
    scene.collection.objects.link(other)
    for frame, value in ((1, 100), (21, 200)):
        other.location.x = value
        other.keyframe_insert(data_path='location', index=0, frame=frame)
    for k in curves(other.name)[0].keyframe_points: k.select_control_point = False
    if key == 'ALIGN':
        follower = bpy.data.objects.new('AA_Follower', None)
        scene.collection.objects.link(follower)
        follower.location = (9, 8, 7)
        follower.select_set(True)
    if key in ('MIRROR_ACTIVE', 'MIRROR_SELECTED', 'MIRROR_FRAME', 'MIRROR_RANGE', 'OPPOSITE', 'SWAP'):
        obj.select_set(False)
        arm = bpy.data.armatures.new('AA_RigData')
        rig = bpy.data.objects.new('AA_Rig', arm)
        scene.collection.objects.link(rig)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        with bpy.context.temp_override(area=view, region=window_region(view)):
            bpy.ops.object.mode_set(mode='EDIT')
            for name, x in (('hand.L', 1), ('hand.R', -1)):
                bone = arm.edit_bones.new(name)
                bone.head, bone.tail = (x, 0, 0), (x, 1, 0)
            bpy.ops.object.mode_set(mode='POSE')
        for bone in rig.pose.bones:
            bone.location = (2, 3, 4) if bone.name.endswith('.L') else (-9, 0, 0)
            for frame in (1, 21): bone.keyframe_insert(data_path='location', frame=frame)
            bone.select = bone.name.endswith('.L')
        arm.bones.active = arm.bones['hand.L']
        scene.frame_set(6)
    if key == 'BAKE_CLEANUP':
        with bpy.context.temp_override(area=timeline, region=window_region(timeline)):
            bpy.ops.animassist.p7_create_proxy(proxy_type='TRANSLATION')
    if key in ('TRAIL_HIDE', 'TRAIL_REFRESH', 'TRAIL_DIAGNOSE'):
        with bpy.context.temp_override(area=view, region=window_region(view)):
            bpy.ops.animassist.p5_enable_overlay()
    if key == 'OFFSET_SCENE_RANGE':
        scene.anim_assist.mask.start_frame, scene.anim_assist.mask.end_frame = 4, 9
    bpy.context.view_layer.update()


def close(a, b):
    return abs(a-b) < 2e-4


def numeric_rows(expected):
    actual = key_rows()
    assert len(actual) == len(expected) and all(close(x,u) and close(y,v)
        for (x,y),(u,v) in zip(actual, expected)), f'{actual} != {expected}'


def oracle(key, before, after, cancel=False):
    if cancel:
        assert after == before, 'Esc did not restore complete measured fixture state'
        return 'Esc restores keys and measured scene state'
    baseline = [(1,0),(6,3),(11,10),(21,0)]
    if key in ('B25','B50','B75','PUSH_PREV','PULL_PREV','PULL_NEXT','PUSH_NEXT','DRAG'):
        value = {'B25':2.5,'B50':5,'B75':7.5,'PUSH_PREV':-2.5,'PULL_PREV':2.5,
            'PULL_NEXT':7.5,'PUSH_NEXT':12.5,'DRAG':10}[key]
        numeric_rows([(1,0),(6,value),(11,10),(21,0)])
    elif key in ('INBETWEEN','INBETWEENS'):
        expected_frames = [1,6,11,21] if key=='INBETWEEN' else [1,4.33333,6,7.66667,11,21]
        assert len(key_rows())==len(expected_frames) and all(close(r[0],f) for r,f in zip(key_rows(),expected_frames)), key_rows()
        if key=='INBETWEEN': assert close(key_rows()[1][1],5)
    elif key in ('NEIGHBORS','FRAME','EASE','AMPLIFY','SMOOTH'):
        middle = {'NEIGHBORS':(1.5,5),'FRAME':(1.5,5),'EASE':(1.5,5),
            'AMPLIFY':(4.5,15),'SMOOTH':(4,5.75)}[key]
        numeric_rows([(1,0),(6,middle[0]),(11,middle[1]),(21,0)])
    elif key == 'REFERENCE':
        assert after['reference']==6, after['reference']
    elif key.startswith('HANDLE_'):
        expected = {'HANDLE_CLAMPED':'AUTO_CLAMPED'}.get(key,key[7:])
        for i,k in enumerate(curves()[0].keyframe_points):
            if i in (1,2): assert k.handle_left_type==expected and k.handle_right_type==expected
            else: assert k.handle_left_type==before['objects']['AA_Test']['curves'][0][2][i][4]
    elif key.startswith('TYPE_'):
        expected = {'TYPE_HOLD':'MOVING_HOLD'}.get(key,key[5:])
        assert [k.type for k in curves()[0].keyframe_points] == ['KEYFRAME',expected,expected,'KEYFRAME']
    elif key in ('NUDGE_LEFT','NUDGE_RIGHT','OFFSET_ACTION','OFFSET_DRAG','RIPPLE','INSERT_TIME','REMOVE_TIME','REVERSE','SNAP','DISTRIBUTE_TIME') or key.startswith('T') and key[1:].isdigit():
        expected = {'NUDGE_LEFT':[(1,0),(5,3),(10,10),(21,0)],'NUDGE_RIGHT':[(1,0),(7,3),(12,10),(21,0)],
            'OFFSET_ACTION':[(3,0),(8,3),(13,10),(23,0)], 'OFFSET_DRAG':[(11,0),(16,3),(21,10),(31,0)],
            'RIPPLE':[(1,0),(6,3),(13,10),(23,0)],'INSERT_TIME':[(1,0),(6,3),(12,10),(22,0)],
            'REMOVE_TIME':[(1,0),(6,3),(10,10),(20,0)], 'REVERSE':[(1,0),(11,10),(16,3),(21,0)],
            'SNAP':[(1,0),(6,3),(11,10),(21,0)], 'DISTRIBUTE_TIME':[(1,0),(7.66667,3),(14.33333,10),(21,0)]}
        if key.startswith('T') and key[1:].isdigit():
            factor=int(key[1:])/100
            numeric_rows([(1+(f-1)*factor,v) for f,v in baseline])
        else: numeric_rows(expected[key])
    elif key == 'SCALE_DRAG':
        # Native drag scale uses exponential sensitivity; exact formula checked separately.
        rows=key_rows()
        assert rows[0]==[1,0] and rows[-1][0]>21 and [r[1] for r in rows]==[0,3,10,0], rows
    elif key in ('ALL','RANGE','ENDS','GROW_LEFT','GROW_RIGHT','GROW_BOTH','SELECT_BREAKDOWNS'):
        selected=[i for i,k in enumerate(curves()[0].keyframe_points) if k.select_control_point]
        expected={'ALL':[0,1,2,3],'RANGE':[0,1,2,3],'ENDS':[0,3],
            'GROW_LEFT':[0,1,2],'GROW_RIGHT':[1,2,3],'GROW_BOTH':[0,1,2,3], 'SELECT_BREAKDOWNS':[1]}[key]
        assert selected==expected, f'{selected} != {expected}'
        numeric_rows(baseline)
    elif key in ('MIRROR_ACTIVE','MIRROR_SELECTED','MIRROR_FRAME','MIRROR_RANGE'):
        rig=bpy.data.objects['AA_Rig']
        assert all(close(a,b) for a,b in zip(rig.pose.bones['hand.R'].location,(-2,3,4))), list(rig.pose.bones['hand.R'].location)
    elif key == 'OPPOSITE':
        assert bpy.data.objects['AA_Rig'].pose.bones['hand.R'].select
    elif key == 'SWAP':
        assert close(bpy.data.objects['AA_Rig'].pose.bones['hand.L'].location.x,9)
        assert close(bpy.data.objects['AA_Rig'].pose.bones['hand.R'].location.x,-2)
    elif key == 'ALIGN':
        assert all(close(a,b) for a,b in zip(bpy.data.objects['AA_Follower'].matrix_world.translation,(3,0,0)))
    elif key.startswith('PROXY_'):
        new = set(after['objects'])-set(before['objects'])
        assert len(new)==1, new
        kind={'PROXY_TRANSLATION':'COPY_LOCATION','PROXY_ORIENTATION':'COPY_ROTATION',
            'PROXY_WORLD':'COPY_TRANSFORMS','PROXY_PARENT':'CHILD_OF'}[key]
        assert after['objects']['AA_Test']['constraints']==[(kind,next(iter(new)))], after['objects']['AA_Test']['constraints']
    elif key in ('BAKE_STEP','SMART_BAKE','REDUCE'):
        obj=bpy.data.objects['AA_Test']
        sample_fc=next(f for f in curves() if f.data_path=='location' and f.array_index==0)
        for frame, expected in ((1,0),(3,1.2),(5,2.4),(7,4.4),(9,7.2),(11,10),(21,0)):
            assert close(sample_fc.evaluate(frame),expected), f'Frame {frame}: {sample_fc.evaluate(frame)} != {expected}'
        if key=='BAKE_STEP':
            assert set(range(1,22,2)).issubset({round(k.co.x) for k in sample_fc.keyframe_points})
        if key=='REDUCE': assert len(sample_fc.keyframe_points)==4, 'Redundant linear key not removed'
    elif key=='BAKE_CLEANUP':
        assert set(after['objects'])=={'AA_Test','AA_Untouched'}, set(after['objects'])
        assert not after['objects']['AA_Test']['constraints']
    elif key in ('TRAIL_SHOW','TRAIL_HIDE','TRAIL_REFRESH','TRAIL_DIAGNOSE'):
        from B4_anim_assist.core.p5_draw import get_handler_ids
        assert after['overlay'] == (key!='TRAIL_HIDE')
        ids=get_handler_ids()
        assert (any(i>=0 for i in ids)) == (key!='TRAIL_HIDE'), ids
        if key in ('TRAIL_SHOW','TRAIL_REFRESH','TRAIL_DIAGNOSE'):
            # Registration alone proves no drawn geometry; keep result partial below.
            STATE['entry']['semantic_boundary']='Overlay state/handlers only; rendered trajectories and diagnostics need separate geometry checks'
    elif key=='OFFSET':
        numeric_rows([(f,v+2) for f,v in baseline])
    elif key=='OFFSET_MASK':
        assert after['mask'][0] is True
    elif key=='OFFSET_SCENE_RANGE':
        assert after['mask'][1:]==[1,21],after['mask']
    else: raise AssertionError('No semantic oracle authored for '+key)
    # Most tools must not modify the unselected sentinel's curve values/times.
    untouched_before=before['objects']['AA_Untouched']['curves']
    untouched_after=after['objects']['AA_Untouched']['curves']
    assert [[r[:2] for r in f[2]] for f in untouched_before] == [[r[:2] for r in f[2]] for f in untouched_after], 'Untargeted sentinel animation changed'
    return 'Independent numeric/structural effect and untargeted curve preservation'


def save():
    (DEST/'results.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')


def advance():
    key,cancel=CASES[STATE['index']]
    entry=STATE.get('entry')
    try:
        if STATE['phase']=='setup':
            fixture(key)
            if '--undo-native' in sys.argv:
                baseline = DEST/'undo-baseline.blend'
                bpy.ops.wm.save_as_mainfile(filepath=str(baseline))
                bpy.ops.wm.open_mainfile(filepath=str(baseline))
                STATE['phase'] = 'after_reload'
                return .3
        if STATE['phase'] in {'setup', 'after_reload'}:
            entry={'action':key,'cancel_case':cancel,'operator':'animassist.'+ACTIONS[key][0],
                'status':'NOT RUN','undo':'NOT RUN','redo':'NOT RUN'}
            STATE['entry']=entry
            STATE['before']=snapshot()
            entry['before']=STATE['before']
            native_event('MOUSEMOVE',x=400)
            STATE['phase']='invoke'
            return .15
        if STATE['phase']=='invoke':
            strip,timeline,view=areas()
            with bpy.context.temp_override(area=timeline,region=window_region(timeline)):
                entry['poll']=getattr(bpy.ops.animassist,ACTIONS[key][0]).poll()
                bpy.ops.ed.undo_push(message='Independent toolbar fixture')
            assert entry['poll'], 'Target poll failed on intended valid fixture'
            if '--more-click' in sys.argv and key=='B25':
                bpy.context.window.event_simulate(type='MOUSEMOVE',value='NOTHING',x=945,y=strip.y+17)
                entry['dispatch_result']=['NATIVE_MORE_EVENTS_QUEUED']
                STATE['phase']='more_press'
                return .2
            if '--click' in sys.argv and key=='B25':
                x,y=int(sys.argv[sys.argv.index('--click-x')+1]),strip.y+17
                bpy.context.window.event_simulate(type='MOUSEMOVE',value='NOTHING',x=x,y=y)
                entry['dispatch_result']=['NATIVE_UI_EVENTS_QUEUED']
                STATE['phase']='click_press'
                return .25
            else:
                entry['dispatch_result']=call_toolbar(key)
            assert 'CANCELLED' not in entry['dispatch_result'], 'Toolbar dispatcher returned CANCELLED'
            if key in MODALS:
                native_event('MOUSEMOVE',x=500)
                STATE['phase']='modal_finish'
            elif key=='OFFSET':
                curves()[0].keyframe_points[1].co.y+=2
                curves()[0].update()
                STATE['phase']='offset_finish'
            elif key=='MIRROR_RANGE':
                native_event('RET','PRESS')
                native_event('RET','RELEASE')
                STATE['phase']='measure'
            else: STATE['phase']='measure'
            return .25
        if STATE['phase']=='click_press':
            strip,_,_=areas()
            bpy.context.window.event_simulate(type='LEFTMOUSE',value='PRESS',x=int(sys.argv[sys.argv.index('--click-x')+1]),y=strip.y+17)
            STATE['phase']='click_release'
            return .2
        if STATE['phase'] in {'more_press','more_release','more_hover','more_action_press','more_action_release'}:
            strip,_,_=areas()
            phase=STATE['phase']
            x,y=(945,strip.y+17) if phase in {'more_press','more_release'} else (1024,555)
            kind='MOUSEMOVE' if phase=='more_hover' else 'LEFTMOUSE'
            value='NOTHING' if phase=='more_hover' else ('PRESS' if phase.endswith('press') else 'RELEASE')
            bpy.context.window.event_simulate(type=kind,value=value,x=x,y=y)
            STATE['phase']={'more_press':'more_release','more_release':'more_hover',
                'more_hover':'more_action_press','more_action_press':'more_action_release',
                'more_action_release':'measure'}[phase]
            return .25
        if STATE['phase']=='click_release':
            strip,_,_=areas()
            bpy.context.window.event_simulate(type='LEFTMOUSE',value='RELEASE',x=int(sys.argv[sys.argv.index('--click-x')+1]),y=strip.y+17)
            STATE['phase']='measure'
            return .3
        if STATE['phase']=='modal_finish':
            finish_event = 'ESC' if cancel else ('LEFTMOUSE' if key=='DRAG' else 'RET')
            if finish_event!='LEFTMOUSE': native_event(finish_event,'PRESS',x=500)
            native_event(finish_event,'RELEASE',x=500)
            STATE['phase']='measure'
            return .2
        if STATE['phase']=='offset_finish':
            call_toolbar('OFFSET')
            STATE['phase']='measure'
            return .2
        if STATE['phase']=='measure':
            bpy.context.view_layer.update()
            STATE['after']=snapshot()
            entry['after']=STATE['after']
            entry['oracle']=oracle(key,STATE['before'],STATE['after'],cancel)
            entry['status']='PARTIAL' if 'semantic_boundary' in entry else 'PASS'
            if cancel or STATE['before']==STATE['after'] or '--no-undo' in sys.argv:
                entry['undo']='NOT RUN in dispatch sweep' if '--no-undo' in sys.argv else 'NOT APPLICABLE: measured fixture unchanged'
                finish_case()
                return .1
            STATE['phase']='undo'
            return .1
        if STATE['phase']=='undo':
            if '--undo-native' in sys.argv:
                native_event('Z','PRESS',x=400, ctrl=True)
                native_event('Z','RELEASE',x=400, ctrl=True)
                STATE['phase']='undo_measure'
                return .25
            view=next(a for a in bpy.context.window.screen.areas if a.type=='VIEW_3D')
            with bpy.context.temp_override(area=view,region=window_region(view)):
                entry['undo_operator_result']=sorted(bpy.ops.ed.undo())
            STATE['phase']='undo_measure'
            return .15
        if STATE['phase']=='undo_measure':
            actual=snapshot()
            # Read stored data before redo. frame_set here changes the scene
            # and can invalidate Blender's redo buffer; loc/rot are evaluated
            # caches, not the key data this Breakdown check changes.
            def stored_data(value):
                return {name:{k:v for k,v in obj.items() if k not in {'loc','rot'}}
                        for name,obj in value['objects'].items()}
            entry['undo']='PASS' if stored_data(actual)==stored_data(STATE['before']) else 'FAIL'
            entry['undo_oracle'] = 'Stored animation/object data; transform cache excluded before redo'
            if entry['undo']=='FAIL': entry['undo_after']=actual
            if '--redo-api' in sys.argv:
                view=next(a for a in bpy.context.window.screen.areas if a.type=='VIEW_3D')
                with bpy.context.temp_override(area=view,region=window_region(view)):
                    entry['redo_operator_result']=sorted(bpy.ops.ed.redo())
            elif '--undo-native' in sys.argv:
                native_event('Z','PRESS',x=400,ctrl=True,shift=True)
                native_event('Z','RELEASE',x=400,ctrl=True,shift=True)
            else:
                view=next(a for a in bpy.context.window.screen.areas if a.type=='VIEW_3D')
                with bpy.context.temp_override(area=view,region=window_region(view)):
                    entry['redo_operator_result']=sorted(bpy.ops.ed.redo())
            STATE['phase']='redo_measure'
            return .15
        if STATE['phase']=='redo_measure':
            bpy.context.scene.frame_set(bpy.context.scene.frame_current)
            bpy.context.view_layer.update()
            entry['redo_after'] = snapshot()
            entry['redo']='PASS' if entry['redo_after']==STATE['after'] else 'FAIL'
            finish_case()
            return .1
    except Exception:
        if not entry:
            entry={'action':key,'cancel_case':cancel,'status':'HARNESS ERROR'}
        else:
            entry['status']='FAIL' if STATE['phase'] not in ('setup','undo','undo_measure','redo_measure') else 'HARNESS ERROR'
        entry['error']=traceback.format_exc()
        STATE['entry']=entry
        native_event('ESC','PRESS')
        native_event('ESC','RELEASE')
        finish_case()
        return .3


def finish_case():
    RESULT['checks'].append(STATE['entry'])
    print(STATE['entry']['action'],STATE['entry']['cancel_case'],STATE['entry']['status'],STATE['entry'].get('undo'),flush=True)
    save()
    STATE['index']+=1
    STATE['phase']='setup'
    STATE['entry']=None
    if STATE['index']==len(CASES):
        bpy.app.timers.register(finish,first_interval=.2)


def tick():
    if STATE['index']>=len(CASES): return None
    if STATE['phase']=='setup' and not any(is_strip(a) and strip_module_pair(a)
            for a in bpy.context.window_manager.windows[0].screen.areas):
        return .5
    if bpy.context.window is None:
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            return advance()
    return advance()


def finish():
    from collections import Counter
    RESULT['summary']=dict(Counter(c['status'] for c in RESULT['checks']))
    RESULT['catalogue_presets_attempted']=len({c['action'] for c in RESULT['checks']})
    RESULT['unique_operators_attempted']=len({ACTIONS[c['action']][0] for c in RESULT['checks']})
    strip, timeline, _ = areas()
    RESULT['native_layout'] = {'ui_scale':bpy.context.preferences.system.ui_scale,
        'strip_width':strip.width,'strip_height':strip.height,
        'strip_count':sum(is_strip(a) for a in bpy.context.window.screen.areas),
        'paired':strip_module_pair(strip)==timeline}
    RESULT['layout_checks'] = layout_checks()
    save()
    if '--show-more' in sys.argv:
        x, y = int(sys.argv[sys.argv.index('--menu-x')+1]), strip.y+17
        window = bpy.context.window
        window.event_simulate(type='MOUSEMOVE', value='NOTHING',x=x,y=y)
        def press():
            window.event_simulate(type='LEFTMOUSE',value='PRESS',x=x,y=y)
            return None
        def release():
            window.event_simulate(type='LEFTMOUSE',value='RELEASE',x=x,y=y)
            return None
        bpy.app.timers.register(press,first_interval=.2)
        bpy.app.timers.register(release,first_interval=.4)
        bpy.app.timers.register(capture_and_quit,first_interval=.8)
        return None
    capture_and_quit()


def capture_and_quit():
    bpy.ops.screen.screenshot(filepath=str(DEST/'toolbar.png'))
    addon_utils.disable('B4_anim_assist',default_set=True)
    bpy.ops.wm.quit_blender()


def layout_checks():
    from B4_anim_assist.prefs import get_prefs
    from B4_anim_assist.ui.timeline_catalog import selected_quick_actions, quick_clusters
    prefs = get_prefs()
    assert len(quick_clusters(selected_quick_actions(prefs))) == 7
    # Native matrix and all70 recorded drawing are separate fixtures.
    RESULT['layout'] = {'families': 7, 'native_matrix': 'separate evidence',
                        'selected': sorted(selected_quick_actions(prefs))}


def strip_module_pair(strip):
    from B4_anim_assist.ui.timeline_strip import timeline_below
    return timeline_below(bpy.context.window.screen,strip)


# Native GUI matrix uses the application's event queue, never OS automation.
MATRIX = {'mode': 0, 'phase': 'start', 'event': 0, 'steps': 0, 'rows': []}
MATRIX_MODES = ('defaults', 'custom', 'all70', 'empty')

def header_extent():
    strip, _timeline, _view = areas()
    header = next(r for r in strip.regions if r.type == 'HEADER')
    return header, [round(header.view2d.region_to_view(x, 0)[0], 3) for x in (0, header.width)]


def pan_event(direction, index):
    header, _extent = header_extent()
    start, end = (header.x + header.width - 35, header.x + 35)
    if direction == 'left': start, end = end, start
    sequence = [('MOUSEMOVE', 'NOTHING', start), ('MIDDLEMOUSE', 'PRESS', start),
                ('MOUSEMOVE', 'NOTHING', end), ('MIDDLEMOUSE', 'RELEASE', end)]
    kind, value, x = sequence[index]
    bpy.context.window.event_simulate(type=kind, value=value, x=x, y=header.y+header.height//2)


def matrix_tick():
    from B4_anim_assist.prefs import get_prefs
    from B4_anim_assist.ui.timeline_catalog import DEFAULT_QUICK_ACTIONS, quick_property_name, selected_quick_actions
    if not any(is_strip(a) and strip_module_pair(a) for a in bpy.context.window.screen.areas): return .3
    mode = MATRIX_MODES[MATRIX['mode']]
    prefs = get_prefs()
    phase = MATRIX['phase']
    if phase == 'start':
        fixture('B50')
        choices = set(DEFAULT_QUICK_ACTIONS) if mode == 'defaults' else {'PUSH_PREV','SWAP','OFFSET','TRAIL_DIAGNOSE'} if mode == 'custom' else set(ACTIONS) if mode == 'all70' else set()
        for action in ACTIONS: setattr(prefs, quick_property_name(action), action in choices)
        MATRIX.update(phase='reset', event=0, steps=0, previous=None)
        return .3
    if phase in ('reset', 'pan'):
        pan_event('left' if phase == 'reset' else 'right', MATRIX['event'])
        MATRIX['event'] += 1
        if MATRIX['event'] == 4: MATRIX.update(phase=phase+'_measure', event=0)
        return .035
    if phase in ('reset_measure', 'pan_measure'):
        header, extent = header_extent()
        MATRIX['steps'] += 1
        unchanged = MATRIX.get('previous') == extent
        if not unchanged and MATRIX['steps'] < 80:
            MATRIX.update(previous=extent, phase='reset' if phase == 'reset_measure' else 'pan')
            return .035
        if phase == 'reset_measure':
            bpy.ops.screen.screenshot(filepath=str(DEST/(mode+'-initial.png')))
            MATRIX['row']={'mode':mode, 'selected':sorted(selected_quick_actions(prefs)),
                           'initial_extent':extent, 'header_width':header.width, 'ui_scale':bpy.context.preferences.system.ui_scale}
            MATRIX.update(phase='pan', previous=None, steps=0)
            return .15
        bpy.ops.screen.screenshot(filepath=str(DEST/(mode+'-rightmost.png')))
        MATRIX['row'].update(rightmost_extent=extent, pan_gesture='middle-mouse drag left over native header', pan_steps=MATRIX['steps'])
        assert unchanged, 'Native pan did not reach a stable boundary within 80 gestures'
        MATRIX['rows'].append(MATRIX['row'])
        (DEST/'matrix.json').write_text(json.dumps({'host':bpy.app.version_string, 'binary':bpy.app.binary_path,
            'actual_bforartists':'show_toolshelf_tabs' in bpy.types.SpaceView3D.bl_rna.properties,
            'installed_package':__import__('B4_anim_assist').__file__, 'rows':MATRIX['rows']},indent=2),encoding='utf-8')
        MATRIX['mode'] += 1
        if MATRIX['mode'] == len(MATRIX_MODES):
            if '--interactive' in sys.argv:
                MATRIX['phase']='done'
                fixture('B50')
                for action in ACTIONS: setattr(prefs,quick_property_name(action),action in DEFAULT_QUICK_ACTIONS)
                bpy.app.timers.register(interactive_tick,first_interval=.5)
            else: bpy.ops.wm.quit_blender()
            return None
        MATRIX['phase']='start'
        return .2


def interactive_tick():
    global MATRIX_TARGET
    if bpy.context.window is None:
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            return interactive_tick()
    request = DEST/'request.json'
    if not request.exists(): return .2
    data=json.loads(request.read_text(encoding='utf-8')); request.unlink()
    from B4_anim_assist.prefs import get_prefs
    from B4_anim_assist.ui.timeline_catalog import DEFAULT_QUICK_ACTIONS, quick_property_name, selected_quick_actions
    prefs=get_prefs()
    if 'fixture' in data:
        fixture(data['fixture'])
        bpy.ops.ed.undo_push(message='Disposable native UI baseline')
    if 'baseline' in data:
        MATRIX_TARGET=None
        baseline=DEST/'native-input-baseline.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(baseline))
        bpy.ops.wm.open_mainfile(filepath=str(baseline))
        if not bpy.app.timers.is_registered(interactive_tick):
            bpy.app.timers.register(interactive_tick,first_interval=.2,persistent=True)
        return .2

    if 'pins' in data:
        choices=DEFAULT_QUICK_ACTIONS if data['pins']=='defaults' else data['pins']
        for action in ACTIONS: setattr(prefs,quick_property_name(action),action in choices)
    if 'family' in data: prefs.timeline_quick_family=data['family']
    if 'overlay' in data:
        call_toolbar('TRAIL_SHOW' if data['overlay'] else 'TRAIL_HIDE')
        if data['overlay']:
            from B4_anim_assist.core.p5_draw import _state
            paths=[{'coords':[list(c) for c in path.coords], 'frames':list(path.key_frames)} for path in _state.paths]
            (DEST/'trail-path.json').write_text(json.dumps(paths,indent=2),encoding='utf-8')
    if 'quit' in data: bpy.ops.wm.quit_blender(); return None
    (DEST/'state.json').write_text(json.dumps({'pins':sorted(selected_quick_actions(prefs)),
        'snapshot':snapshot(), 'header_extent':header_extent()[1], 'areas':[{'type':a.type,'x':a.x,'y':a.y,'w':a.width,'h':a.height} for a in bpy.context.window.screen.areas]},indent=2),encoding='utf-8')
    return .2


def demo_boot():
    if not any(is_strip(a) and strip_module_pair(a) for a in bpy.context.window.screen.areas): return .3
    fixture('B50')
    from B4_anim_assist.prefs import get_prefs
    from B4_anim_assist.ui.timeline_catalog import DEFAULT_QUICK_ACTIONS, quick_property_name
    prefs=get_prefs()
    for action in ACTIONS: setattr(prefs,quick_property_name(action),action in DEFAULT_QUICK_ACTIONS)
    bpy.app.timers.register(interactive_tick,first_interval=.2,persistent=True)
    print('DEMO READY',flush=True)
    return None


bpy.app.timers.register(demo_boot if '--demo' in sys.argv else matrix_tick if '--matrix' in sys.argv else inspect_runtime if '--inspect' in sys.argv else tick,
                        first_interval=2.0, persistent=True)

