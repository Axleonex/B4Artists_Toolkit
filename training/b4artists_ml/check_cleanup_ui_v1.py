"""Real-window cleanup modal, Escape, Undo/Redo, Keep and source recovery."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TAG = os.environ.get('B4ML_CLEANUP_UI_TAG', 'v1')


def run():
    import bpy
    import numpy as np
    sys.path[:0] = [str(ROOT), str(ROOT/'tests')]
    import b4artists_ml
    from b4artists_ml import cleanup, contacts, flight, posing, workflow as w
    from test_b4artists_ml_cleanup_v1 import add_reducible_motion, select_only
    from test_b4artists_ml_contacts import fixture

    b4artists_ml.register()
    obj, source, source_signature, modes = fixture('boneforge', transformed=True)
    scene = bpy.context.scene
    obj.b4ml.contacts.clear()
    root = posing.bindings(obj)[1]
    add_reducible_motion(obj, obj.b4ml.candidate_action, root)
    select_only(obj, root)
    obj.b4ml.cleanup_scope = 'SELECTED'
    obj.b4ml.cleanup_tolerance = .025
    original = obj.b4ml.candidate_action
    input_token = flight._curve_token(obj, original)
    state = dict(name=obj.name, source=source.name, input=original.name, phase='dismiss',
                 started=time.monotonic(), events=[], step_ms=[])
    actual_step = cleanup.step

    def timed(value):
        started = time.perf_counter()
        try:
            return actual_step(value)
        finally:
            state['step_ms'].append((time.perf_counter()-started)*1000)
    cleanup.step = timed

    def tick():
        try:
            if time.monotonic()-state['started'] > 180:
                raise AssertionError('Cleanup UI workflow timeout')
            window = bpy.context.window_manager.windows[0]
            area = next(item for item in window.screen.areas if item.type == 'VIEW_3D')
            region = next(item for item in area.regions if item.type == 'WINDOW')
            area.spaces.active.show_region_ui = True
            for item in area.regions:
                if item.type == 'UI' and hasattr(item, 'active_panel_category'):
                    item.active_panel_category = 'B4Artists ML'
            obj = bpy.data.objects[state['name']]
            window.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                phase = state['phase']
                if phase == 'dismiss':
                    window.event_simulate(type='ESC', value='PRESS')
                    bpy.ops.view3d.view_axis(type='FRONT')
                    state['phase'] = 'start_cancel'
                elif phase == 'start_cancel':
                    obj.b4ml.show_cleanup = True
                    bpy.ops.ed.undo_push(message='Cleanup inputs ready')
                    assert bpy.ops.b4ml.cleanup_solve('INVOKE_DEFAULT') == {'RUNNING_MODAL'}
                    state['phase'] = 'escape'
                elif phase == 'escape':
                    if not obj.b4ml.cleanup_progress.startswith('Cleaning'):
                        return .02
                    window.event_simulate(type='ESC', value='PRESS')
                    state['phase'] = 'cancelled'
                elif phase == 'cancelled':
                    if obj.b4ml.cleanup_running:
                        return .02
                    assert obj.b4ml.candidate_action == original
                    assert obj.animation_data.action == original
                    assert flight._curve_token(obj, original) == input_token
                    state['events'].append('Escape cancelled cleanup and retained the exact input candidate')
                    assert bpy.ops.b4ml.cleanup_solve('INVOKE_DEFAULT') == {'RUNNING_MODAL'}
                    state['phase'] = 'completed'
                elif phase == 'completed':
                    if obj.b4ml.cleanup_running:
                        return .03
                    output = obj.b4ml.candidate_action
                    assert output != original and obj.animation_data.action == output
                    state['output'] = output.name
                    state['metrics'] = json.loads(obj.b4ml.cleanup_metrics)
                    state['output_signature'] = contacts._action_signature(obj)
                    screenshot = ROOT/f'training/b4artists_ml/cache/cleanup-ui-{TAG}.png'
                    bpy.ops.screen.screenshot(filepath=str(screenshot))
                    state['screenshot'] = str(screenshot.relative_to(ROOT))
                    assert bpy.ops.ed.undo() == {'FINISHED'}
                    state['phase'] = 'undo'
                elif phase == 'undo':
                    assert obj.b4ml.candidate_action.name == state['input']
                    assert flight._curve_token(obj, obj.b4ml.candidate_action) == input_token
                    assert bpy.ops.ed.redo() == {'FINISHED'}
                    state['phase'] = 'redo'
                elif phase == 'redo':
                    assert obj.b4ml.candidate_action.name == state['output']
                    assert contacts._action_signature(obj) == state['output_signature']
                    state['events'].append('Undo and Redo restored the cleanup transaction')
                    assert bpy.ops.b4ml.action(operation='KEEP') == {'FINISHED'}
                    assert bpy.ops.b4ml.action(operation='RESTORE_SOURCE') == {'FINISHED'}
                    assert obj.animation_data.action.name == state['source']
                    assert contacts._action_signature(obj) == source_signature
                    state['events'].append('Keep and Restore Source recovered the original animation')
                    report = dict(passed=True, events=state['events'], metrics=state['metrics'],
                                  screenshot=state['screenshot'], step_count=len(state['step_ms']),
                                  step_p95_ms=float(np.percentile(state['step_ms'], 95)),
                                  step_max_ms=max(state['step_ms']), elapsed_seconds=time.monotonic()-state['started'],
                                  scope='Automated real-window controls and events; independent animator visual assessment remains unverified.')
                    (ROOT/f'docs/b4artists_ml/cleanup-ui-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
                    print('CLEANUP_UI_RESULT: '+json.dumps(report), flush=True)
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            report = dict(passed=False, phase=state['phase'], events=state['events'], error=traceback.format_exc())
            (ROOT/f'docs/b4artists_ml/cleanup-ui-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
            print('CLEANUP_UI_RESULT: '+json.dumps(report), flush=True)
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
        started = time.perf_counter()
        log = ROOT/f'training/b4artists_ml/cache/cleanup-ui-{TAG}.log'
        with log.open('w') as stream:
            process = subprocess.run(
                ['X:/5.1.0/bforartists.exe', '--factory-startup', '--no-window-focus',
                 '--enable-event-simulate', '--python', str(HERE), '--', '--host'],
                stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='4'), timeout=240)
        report = dict(exit_code=process.returncode, seconds=time.perf_counter()-started,
                      log=str(log.relative_to(ROOT)))
        (ROOT/f'training/b4artists_ml/results/cleanup-ui-process-{TAG}.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report), flush=True)
