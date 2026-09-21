"""Real-window Undo/Redo verification for bulk contact-review metadata."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TAG = os.environ.get('B4ML_CONTACT_REVIEW_UI_TAG', 'v1')


def run(scenario):
    import addon_utils
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
    import b4artists_ml
    from b4artists_ml import contacts, quadruped_contacts, ui
    from test_b4artists_ml_contact_review_v1 import add_contact
    from test_b4artists_ml_contacts import fixture
    from test_b4artists_ml_quadruped_contacts import _signature
    from test_b4artists_ml_quadruped_suggestions import prepared as quadruped_prepared

    addon_utils.enable('rigify', default_set=True, persistent=False)
    b4artists_ml.register()
    if scenario == 'humanoid':
        obj, source, _, _ = fixture('boneforge')
        rows = (('leg-L', 2.0), ('leg-R', 5.0))
        foreign_limb = 'fore-L'
        obj.b4ml.show_contacts = True
    elif scenario == 'quadruped':
        scene, obj, source, _, _, _, _ = quadruped_prepared('cat')
        rows = tuple(zip(quadruped_contacts.LIMBS, (1.0, 3.0, 5.0, 7.0)))
        foreign_limb = 'leg-L'
        obj.b4ml.show_quadruped_contacts = True
    else:
        raise ValueError('Unknown contact-review UI scenario')
    scene = bpy.context.scene
    candidate = obj.b4ml.candidate_action
    obj.b4ml.contacts.clear()
    proposed = [add_contact(obj, limb, 'PROPOSED', frame) for limb, frame in rows]
    foreign = add_contact(obj, foreign_limb, 'PROPOSED', 8.5)
    before_contacts = contacts._contact_signature(obj)
    before_candidate = _signature(obj, candidate)
    before_source = _signature(obj, source)
    state = dict(
        phase='apply', started=time.monotonic(), name=obj.name,
        candidate=candidate.name, source=source.name, proposed=proposed, foreign=foreign,
        before_contacts=before_contacts, before_candidate=before_candidate,
        before_source=before_source, events=[],
    )

    def tick():
        try:
            if time.monotonic() - state['started'] > 180:
                raise AssertionError('Contact-review UI workflow timeout')
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
                if state['phase'] == 'apply':
                    bpy.ops.ed.undo_push(message=f'{scenario.title()} contact-review inputs ready')
                    assert bpy.ops.b4ml.contact('INVOKE_DEFAULT', operation='ACCEPT_ALL') == {'FINISHED'}
                    assert all(obj.b4ml.contacts[index].review_state == 'ACCEPTED'
                               and obj.b4ml.contacts[index].enabled
                               for index in state['proposed'])
                    assert obj.b4ml.contacts[state['foreign']].review_state == 'PROPOSED'
                    assert _signature(obj, obj.animation_data.action) == state['before_candidate']
                    assert _signature(obj, bpy.data.actions[state['source']]) == state['before_source']
                    state['after_contacts'] = contacts._contact_signature(obj)
                    # Timer-driven bpy calls do not receive Blender's normal UI operator
                    # transaction boundary, so bracket the completed operator state explicitly.
                    bpy.ops.ed.undo_push(message=f'{scenario.title()} bulk contact review applied')
                    screenshot = ROOT / f'training/b4artists_ml/cache/contact-review-ui-{scenario}-{TAG}.png'
                    bpy.ops.screen.screenshot(filepath=str(screenshot))
                    state['screenshot'] = str(screenshot.relative_to(ROOT))
                    assert bpy.ops.ed.undo() == {'FINISHED'}
                    state['phase'] = 'undo'
                elif state['phase'] == 'undo':
                    assert contacts._contact_signature(obj) == state['before_contacts']
                    assert obj.animation_data.action.name == state['candidate']
                    assert _signature(obj, obj.animation_data.action) == state['before_candidate']
                    assert _signature(obj, bpy.data.actions[state['source']]) == state['before_source']
                    state['events'].append('Undo restored every review state and enabled flag')
                    assert bpy.ops.ed.redo() == {'FINISHED'}
                    state['phase'] = 'redo'
                elif state['phase'] == 'redo':
                    assert contacts._contact_signature(obj) == state['after_contacts']
                    assert all(obj.b4ml.contacts[index].review_state == 'ACCEPTED'
                               and obj.b4ml.contacts[index].enabled
                               for index in state['proposed'])
                    assert obj.b4ml.contacts[state['foreign']].review_state == 'PROPOSED'
                    assert obj.animation_data.action.name == state['candidate']
                    assert _signature(obj, obj.animation_data.action) == state['before_candidate']
                    assert _signature(obj, bpy.data.actions[state['source']]) == state['before_source']
                    state['events'].append('Redo restored the family-filtered bulk acceptance')
                    report = dict(
                        passed=True, scenario=scenario,
                        accepted=len(state['proposed']), foreign_preserved=True,
                        candidate_unchanged=True, source_unchanged=True,
                        operator_undo_flag='UNDO' in ui.B4ML_OT_contact.bl_options,
                        undo_boundary='explicit foreground test boundary for timer-driven invocation',
                        events=state['events'], screenshot=state['screenshot'],
                        elapsed_seconds=time.monotonic() - state['started'],
                    )
                    output = ROOT / f'training/b4artists_ml/results/contact-review-ui-{scenario}-{TAG}.json'
                    output.write_text(json.dumps(report, indent=2) + '\n')
                    print('CONTACT_REVIEW_UI_RESULT: ' + json.dumps(report), flush=True)
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            report = dict(passed=False, scenario=scenario, phase=state['phase'],
                          events=state['events'], error=traceback.format_exc())
            output = ROOT / f'training/b4artists_ml/results/contact-review-ui-{scenario}-{TAG}.json'
            output.write_text(json.dumps(report, indent=2) + '\n')
            print('CONTACT_REVIEW_UI_RESULT: ' + json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None
        return .05

    bpy.app.timers.register(tick, first_interval=.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    rows = []
    for scenario in ('humanoid', 'quadruped'):
        output = ROOT / f'training/b4artists_ml/results/contact-review-ui-{scenario}-{TAG}.json'
        if output.exists():
            raise RuntimeError('Evidence exists: ' + str(output))
        log = ROOT / f'training/b4artists_ml/cache/contact-review-ui-{scenario}-{TAG}.log'
        started = time.perf_counter()
        with log.open('w') as stream:
            process = subprocess.run(
                ['X:/5.1.0/bforartists.exe', '--factory-startup', '--no-window-focus',
                 '--enable-event-simulate', '--python', str(HERE), '--', '--host', scenario],
                stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='4'),
                timeout=240,
            )
        report = json.loads(output.read_text()) if output.exists() else {
            'passed': False, 'scenario': scenario, 'error': 'Missing host report'
        }
        report['process_exit'] = process.returncode
        report['process_seconds'] = time.perf_counter() - started
        report['log'] = str(log.relative_to(ROOT))
        rows.append(report)
        if not report['passed']:
            break
    aggregate = dict(
        passed=len(rows) == 2 and all(row['passed'] for row in rows),
        scenarios=rows,
        scope=('Automated real-window events for family-filtered bulk review; '
               'independent animator usability remains unverified.'),
    )
    destination = ROOT / f'docs/b4artists_ml/contact-review-ui-{TAG}.json'
    destination.write_text(json.dumps(aggregate, indent=2) + '\n')
    print(json.dumps(aggregate), flush=True)
    if not aggregate['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    if '--host' in sys.argv:
        run(sys.argv[sys.argv.index('--host') + 1])
    else:
        launch()
