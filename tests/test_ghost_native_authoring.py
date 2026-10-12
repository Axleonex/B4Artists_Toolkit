"""Real native transforms with auto-key. Run a factory GUI with --enable-event-simulate.

The Blender stand-in patches only the Bforartists registration gate. Unlike
the background regressions, these checks exercise native modal handlers and
keyboard events, not a mocked modal list. Results go to a disposable JSON file.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

import bpy

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(os.environ.get('GHOST_TEST_ADDON_ROOT',
                                         Path(__file__).resolve().parents[1] / 'ghost_tool')).parent))
import ghost_tool
from ghost_tool import ghost_pipeline as gp, ghost_data as gd, mesh_ghosts as mg, utils

OUTPUT = Path(os.environ.get('GHOST_NATIVE_TEST_OUTPUT',
                            str(Path(tempfile.gettempdir()) / 'ghost-native-authoring.json')))
CASES = [('OBJECT', False, False), ('OBJECT', True, False),
         ('POSE', False, False), ('POSE', True, False), ('OBJECT', False, True)]
records = []
state = {'case': 0, 'step': 0, 'samples': 0}


def snapshot(scene):
    skin = sorted((obj.name, obj.get(mg.GHOST_TOOL_FRAME_KEY),
                   tuple(v for row in obj.matrix_world for v in row),
                   tuple(tuple(v.co) for v in obj.data.vertices))
                  for obj in scene.objects if obj.get(mg.GHOST_TOOL_MESH_GHOST_KEY))
    points = [(g.object_name, g.bone_name, g.frame, tuple(g.world_position))
              for g in gd.GhostStore.get(scene)]
    return skin, points


def near(actual, expected):
    assert abs(actual - expected) < 1e-4, (actual, expected)


def setup(scene):
    assert not bpy.app.background, 'Native modal checks require a GUI engine'
    if not ghost_tool._is_bforartists():
        ghost_tool._is_bforartists = lambda: True
    ghost_tool.register()
    scene.ghost_tool.is_active = False
    cube = bpy.data.objects['Cube']
    bpy.ops.object.armature_add()
    rig = bpy.context.object
    rig.name = 'NativeAuthoringRig'
    rig.data.bones.active = rig.data.bones[0]
    modifier = cube.modifiers.new('NativeAuthoring', 'ARMATURE')
    modifier.object = rig
    group = cube.vertex_groups.new(name=rig.pose.bones[0].name)
    group.add(list(range(len(cube.data.vertices))), 1.0, 'REPLACE')
    for frame, value in ((1, 0), (30, 20)):
        cube.location.x = value
        cube.keyframe_insert('location', frame=frame)
        rig.pose.bones[0].location.x = value
        rig.pose.bones[0].keyframe_insert('location', frame=frame)
    state.update(cube=cube, rig=rig)
    original = gp.GhostPipeline._run_live_update

    def traced(self, *args):
        assert not utils.is_native_transform_active(bpy.context), 'Sampled during a native gesture'
        state['samples'] += 1
        return original(self, *args)
    gp.GhostPipeline._run_live_update = traced


def tick():
    try:
        window = bpy.context.window_manager.windows[0]
        area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=area, region=region):
            scene = bpy.context.scene
            if 'cube' not in state:
                setup(scene)
            mode, live, cancel = CASES[state['case']]
            holder = state['cube'] if mode == 'OBJECT' else state['rig'].pose.bones[0]
            settings = scene.ghost_tool
            x, y = region.x + region.width // 2, region.y + region.height // 2

            def event(kind, value='PRESS', unicode=''):
                options = {'unicode': unicode} if unicode else {}
                window.event_simulate(type=kind, value=value, x=x, y=y, **options)

            step = state['step']
            if step == 0:
                settings.is_active = False
                scene.tool_settings.use_keyframe_insert_auto = False
                if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                target = state['cube'] if mode == 'OBJECT' else state['rig']
                target.select_set(True)
                bpy.context.view_layer.objects.active = target
                if mode == 'POSE':
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.select_all(action='SELECT')
                scene.frame_set(7 + state['case'] * 2)
                settings.live_point_ghosts = settings.live_mesh_ghosts = live
                settings.paths_enabled = False
                settings.mesh_ghost_past_count = settings.mesh_ghost_future_count = 1
                settings.ghost_range_mode = 'AROUND_CURSOR'
                settings.ghost_mode = 'FRAME_STEP'
                settings.ghosts_before = settings.ghosts_after = 1
                assert bpy.ops.ghost_tool.generate_ghosts() == {'FINISHED'}
                assert bpy.ops.ghost_tool.generate_mesh_ghosts() == {'FINISHED'}
                assert settings.live_point_ghosts == settings.live_mesh_ghosts == live
                scene.tool_settings.use_keyframe_insert_auto = True
                state['origin'] = holder.location.x
                state['frame'] = scene.frame_current
                event('MOUSEMOVE', 'NOTHING')
            elif step == 1:
                state['before'] = snapshot(scene)
                state['count'] = state['samples']
                assert bpy.ops.transform.translate('INVOKE_DEFAULT') == {'RUNNING_MODAL'}
                event('X')
                event('FIVE', unicode='5')
            elif step in (2, 3, 4):
                assert utils.is_native_transform_active(bpy.context)
                near(holder.location.x, state['origin'] + 5)
                assert snapshot(scene) == state['before'], 'Ghost snapshot changed during the move'
                assert state['samples'] == state['count'], 'Backend refreshed during the move'
                if step == 4:
                    event('ESC' if cancel else 'RET')
            elif step == 5:
                assert not utils.is_native_transform_active(bpy.context)
                near(holder.location.x, state['origin'] + (0 if cancel else 5))
                assert state['samples'] == state['count'] + 1, 'Expected one settled edit refresh'
                state['after'] = snapshot(scene)
                if not cancel:
                    assert state['after'] != state['before'], 'Finished move did not refresh ghosts'
                scene.frame_set(1)
            elif step == 6:
                if not live:
                    assert snapshot(scene) == state['after'], 'Disabled scrub update changed snapshot'
                scene.frame_set(state['frame'])
            elif step == 7:
                near(holder.location.x, state['origin'] + (0 if cancel else 5))
                record = dict(mode=mode, live=live, cancel=cancel, status='PASS',
                              native_operator='TRANSFORM_OT_translate', auto_key=True,
                              held_ticks=3, refreshes_after_finish=1)
                records.append(record)
                OUTPUT.write_text(json.dumps(dict(host=bpy.app.version_string,
                                                 status='RUNNING', cases=records), indent=2))
                state['case'] += 1
                state['step'] = 0
                if state['case'] == len(CASES):
                    OUTPUT.write_text(json.dumps(dict(host=bpy.app.version_string,
                                                     status='PASS', cases=records), indent=2))
                    print('NATIVE_AUTHORING_PASS:', len(records), flush=True)
                    bpy.ops.wm.quit_blender()
                    return None
                return 0.4
            state['step'] += 1
        return 0.4
    except Exception:
        OUTPUT.write_text(json.dumps(dict(status='FAIL', cases=records, state={
            'case': state['case'], 'step': state['step']}, error=traceback.format_exc()), indent=2))
        print(traceback.format_exc(), flush=True)
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=1.0)
