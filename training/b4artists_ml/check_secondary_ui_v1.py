"""Real-window selected-control secondary-motion operator lifecycle."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TAG = os.environ.get('B4ML_SECONDARY_UI_TAG', 'secondary-source-v1')
SELF_COLLISION_UI = os.environ.get('B4ML_SELF_COLLISION_UI', '0') == '1'


def run():
    import bpy
    import numpy as np
    sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT/'tests')]
    import b4artists_ml
    from b4artists_ml import secondary_motion as secondary, workflow as w
    from test_b4artists_ml_secondary_motion import fixture
    from mathutils import Vector

    b4artists_ml.register()
    obj, source, _, _, control, _ = fixture('rigify_default')
    scene = bpy.context.scene
    original = obj.b4ml.candidate_action
    controls = [control]

    if SELF_COLLISION_UI:
        captured = set(json.loads(obj.b4ml.anchors[0].payload)['pose'])
        curves = w.action_curves(
            obj.b4ml.candidate_action,
            getattr(obj.animation_data, 'action_slot', None))
        eligible = []
        for name in captured:
            bone = obj.pose.bones[name]
            if len(w._channels(bone)['location']) != 3:
                continue
            path = bone.path_from_id('location')
            if all(curves.find(path, index=index) is not None
                   for index in range(3)):
                eligible.append(name)
        pairs = [(first, second)
                 for index, first in enumerate(eligible[:-1])
                 for second in eligible[index+1:]
                 if obj.pose.bones[first].parent == obj.pose.bones[second].parent]
        if not pairs:
            raise AssertionError('fixture needs two editable sibling location controls')
        controls = sorted(pairs[0])
        scene.frame_set(1)
        displayed = w.display_world(obj)
        center = (displayed @ obj.pose.bones[controls[0]].matrix).translation.copy()

        def set_world(name, target, frame):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            displayed = w.display_world(obj)
            bone = obj.pose.bones[name]
            desired = displayed @ bone.matrix
            desired.translation = Vector(target)
            local = obj.convert_space(
                pose_bone=bone, matrix=displayed.inverted() @ desired,
                from_space='POSE', to_space='LOCAL')
            bone.location = local.to_translation()
            bone.keyframe_insert(data_path='location', frame=frame)

        offset = Vector((.11, 0., 0.))
        set_world(controls[0], center - offset*.5, 1)
        set_world(controls[1], center + offset*.5, 1)
        set_world(controls[0], center + offset*.5, 11)
        set_world(controls[1], center - offset*.5, 11)
        for pose_bone in obj.pose.bones:
            if hasattr(pose_bone, 'select'):
                pose_bone.select = pose_bone.name in controls
            else:
                pose_bone.bone.select = pose_bone.name in controls
        obj.data.bones.active = obj.data.bones[controls[0]]
    else:
        control_bone = obj.pose.bones[control]
        heights = []
        for frame in (1, 11):
            scene.frame_set(frame)
            heights.append(float((w.display_world(obj) @ control_bone.matrix).translation.z))
        obj.b4ml.support_plane_point = (0., 0., min(heights)-.04)
        obj.b4ml.support_plane_normal = (0., 0., 1.)
    obj.b4ml.secondary_space = 'WORLD'
    obj.b4ml.secondary_rotation = not SELF_COLLISION_UI
    obj.b4ml.secondary_location = True
    obj.b4ml.secondary_frequency = .5
    obj.b4ml.secondary_strength = 1.
    obj.b4ml.secondary_gravity = 4.
    obj.b4ml.secondary_collision = not SELF_COLLISION_UI
    obj.b4ml.secondary_collision_clearance = .01
    obj.b4ml.secondary_restitution = .2
    obj.b4ml.secondary_surface_friction = .4
    obj.b4ml.secondary_self_collision = SELF_COLLISION_UI
    obj.b4ml.secondary_self_collision_radius = .05
    scene.frame_set(6)
    state = dict(name=obj.name, source=source.name, input=original.name, control=control,
                 controls=controls,
                 phase='dismiss', started=time.monotonic(), events=[])
    steps = []
    native_step = secondary.step

    def timed(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return native_step(value)
        finally:
            steps.append(dict(ms=(time.perf_counter()-began)*1000,
                              before=before, after=value.b4ml.secondary_progress))
    secondary.step = timed

    def tick():
        try:
            if time.monotonic()-state['started'] > 180:
                raise AssertionError('Secondary-motion UI workflow timeout')
            win = bpy.context.window_manager.windows[0]
            area = next(area for area in win.screen.areas if area.type == 'VIEW_3D')
            region = next(region for region in area.regions if region.type == 'WINDOW')
            area.spaces.active.show_region_ui = True
            for ui_region in area.regions:
                if ui_region.type == 'UI' and hasattr(ui_region, 'active_panel_category'):
                    try:
                        ui_region.active_panel_category = 'B4Artists ML'
                    except (AttributeError, TypeError, RuntimeError):
                        pass
            obj = bpy.data.objects[state['name']]
            win.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=win, area=area, region=region):
                phase = state['phase']
                if phase == 'dismiss':
                    win.event_simulate(type='ESC', value='PRESS')
                    bpy.ops.view3d.view_axis(type='FRONT')
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    obj.b4ml.show_secondary = True
                    state['phase'] = 'start_cancel'
                elif phase == 'start_cancel':
                    bpy.ops.ed.undo_push(message='Secondary motion input ready')
                    assert bpy.ops.b4ml.secondary_solve('INVOKE_DEFAULT') == {'RUNNING_MODAL'}
                    state['phase'] = 'escape'
                elif phase == 'escape':
                    if not steps:
                        return .02
                    win.event_simulate(type='ESC', value='PRESS')
                    state['phase'] = 'cancelled'
                elif phase == 'cancelled':
                    if obj.b4ml.secondary_running:
                        return .02
                    assert obj.b4ml.candidate_action == original
                    assert obj.animation_data.action == original
                    state['events'].append('Escape cancelled generation and retained the input candidate')
                    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=region.x+20, y=region.y+20)
                    state['phase'] = 'cancel_cleanup'
                    return .12
                elif phase == 'cancel_cleanup':
                    state['phase'] = 'restart'
                    return .12
                elif phase == 'restart':
                    bpy.ops.ed.undo_push(message='Secondary motion retained input')
                    assert bpy.ops.b4ml.secondary_solve('INVOKE_DEFAULT') == {'RUNNING_MODAL'}
                    state['phase'] = 'completed'
                elif phase == 'completed':
                    if obj.b4ml.secondary_running:
                        return .02
                    output = obj.b4ml.candidate_action
                    if output == original or obj.b4ml.secondary_input != original:
                        raise AssertionError('Second modal ended without output: '+repr(dict(
                            status=obj.b4ml.status, progress=obj.b4ml.secondary_progress,
                            metrics=obj.b4ml.secondary_metrics, output=output.name if output else None,
                            retained=obj.b4ml.secondary_input.name if obj.b4ml.secondary_input else None,
                            active=obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None)))
                    metrics = json.loads(obj.b4ml.secondary_metrics)
                    if SELF_COLLISION_UI:
                        assert metrics['schema'] == 19
                        assert metrics['backend'] == 'implicit_selected_control_secondary_self_collision_v1'
                        assert metrics['controls'] == state['controls']
                        assert metrics['self_collision'] and metrics['self_collision_samples'] > 0
                        assert metrics['max_self_collision_penetration'] > 0
                        assert metrics['max_penetration_after'] <= 1e-6
                        assert metrics['self_collision_target_space'] == 'selected-control finite volumes'
                        assert metrics['priority_poses_preserved'] and metrics['editable_linear_keys']
                        assert metrics['space'] == 'WORLD'
                        assert metrics['max_world_location_error'] <= 2e-4
                    else:
                        assert metrics['backend'] == 'implicit_selected_control_secondary_v2'
                        assert metrics['controls'] == [state['control']]
                        assert metrics['priority_poses_preserved'] and metrics['editable_linear_keys']
                        assert metrics['max_rotation_correction_radians'] > .01
                        assert metrics['space'] == 'WORLD' and metrics['gravity_influence'] == 4.
                        assert metrics['collision'] and metrics['collision_samples'] > 0
                        assert metrics['max_raw_penetration'] > 0 and metrics['max_penetration_after'] <= 1e-8
                        assert metrics['max_world_location_error'] <= 2e-4
                        assert metrics['max_world_rotation_error_radians'] <= 2e-3
                    state['metrics'] = metrics
                    state['output'] = output.name
                    state['events'].append(
                        'Selected-control self-collision completed as editable candidate curves'
                        if SELF_COLLISION_UI else
                        'Selected-control rotation completed as editable candidate curves')
                    screenshot = ROOT/f'training/b4artists_ml/cache/secondary-ui-{TAG}.png'
                    bpy.ops.screen.screenshot(filepath=str(screenshot))
                    state['screenshot'] = str(screenshot.relative_to(ROOT))
                    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=region.x+24, y=region.y+24)
                    state['phase'] = 'completion_cleanup'
                    return .12
                elif phase == 'completion_cleanup':
                    assert bpy.ops.ed.undo() == {'FINISHED'}
                    state['phase'] = 'undo'
                elif phase == 'undo':
                    assert obj.b4ml.candidate_action and obj.b4ml.candidate_action.name == state['input']
                    assert obj.animation_data.action == obj.b4ml.candidate_action
                    assert bpy.ops.ed.redo() == {'FINISHED'}
                    state['phase'] = 'redo'
                elif phase == 'redo':
                    assert obj.b4ml.candidate_action.name == state['output']
                    state['events'].append('Undo and Redo restored the secondary-motion candidate')
                    assert bpy.ops.b4ml.secondary(operation='RESET') == {'FINISHED'}
                    assert obj.b4ml.candidate_action and obj.b4ml.candidate_action.name == state['input']
                    assert obj.animation_data.action == obj.b4ml.candidate_action
                    state['events'].append('Restore Before Secondary Motion returned to the retained input')
                    assert bpy.ops.b4ml.secondary_solve() == {'FINISHED'}
                    assert bpy.ops.b4ml.action(operation='KEEP') == {'FINISHED'}
                    assert bpy.ops.b4ml.action(operation='RESTORE_SOURCE') == {'FINISHED'}
                    assert obj.animation_data.action.name == state['source']
                    state['events'].append('Keep and Restore Source preserved the generated action and restored source animation')
                    runtime = {'b4artists_ml/'+path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in Path(b4artists_ml.__file__).parent.glob('*.py')}
                    durations = [row['ms'] for row in steps]
                    report = dict(runtime_sha256=runtime, passed=True, events=state['events'],
                        module_root=str(Path(b4artists_ml.__file__).resolve().parent),
                        metrics=state['metrics'], screenshot=state['screenshot'], step_count=len(steps),
                        step_p95_ms=float(np.percentile(durations, 95)), step_max_ms=max(durations),
                        slowest_steps=sorted(steps, key=lambda row: row['ms'], reverse=True)[:5],
                        elapsed_seconds=time.monotonic()-state['started'],
                        scope='Automated real-window operators and events; independent animator usability and visual motion judgment remain unverified.')
                    (ROOT/f'docs/b4artists_ml/secondary-ui-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
                    print(json.dumps(report), flush=True)
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            report = dict(passed=False, phase=state['phase'], events=state['events'], error=traceback.format_exc())
            (ROOT/f'docs/b4artists_ml/secondary-ui-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
            print(json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None
        return .03
    bpy.app.timers.register(tick, first_interval=.5)


if __name__ == '__main__':
    if '--host' in sys.argv:
        run()
    else:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        began = time.perf_counter()
        log_path = ROOT/f'training/b4artists_ml/cache/secondary-ui-{TAG}.log'
        with log_path.open('w') as log:
            process = subprocess.run(['X:/5.1.0/bforartists.exe', '--factory-startup', '--no-window-focus',
                '--enable-event-simulate', '--python', str(HERE), '--', '--host'], stdout=log,
                stderr=subprocess.STDOUT, startupinfo=startup,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='4',
                         B4ML_PACKAGE=os.environ.get('B4ML_PACKAGE', str(ROOT))), timeout=240)
        report = dict(exit_code=process.returncode, seconds=time.perf_counter()-began, log=str(log_path.relative_to(ROOT)))
        (ROOT/f'training/b4artists_ml/results/secondary-ui-process-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report), flush=True)
