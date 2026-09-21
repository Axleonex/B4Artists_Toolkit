"""Bforartists behavioral tests for contact overlays and blend review."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import math
import os
import sys
import time
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT / 'tests')]

import addon_utils
import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contact_math, contact_visualization, contacts, posing, rig_state, ui, workflow
from test_b4artists_ml_contacts import fixture
from test_b4artists_ml_moving_platforms_v1 import _setup as moving_platform_fixture
from test_b4artists_ml_quadruped_contacts import _candidate as quadruped_candidate, _signature as quadruped_signature


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _contact_state(obj):
    return [(item.name, item.enabled, item.review_state, item.limb,
             item.start, item.end, item.blend, item.strength,
             tuple(item.point), tuple(item.rotation), tuple(item.offset),
             item.lock_rotation, item.prop_bound, item.prop_name)
            for item in obj.b4ml.contacts]


def _protected(obj):
    return dict(action=obj.animation_data.action,
                action_signature=contacts._action_signature(obj),
                pose=workflow.raw_pose(obj), modes=rig_state.mode_values(obj),
                matrix=tuple(value for row in obj.matrix_world for value in row),
                contacts=_contact_state(obj))


def _assert_protected(case, obj, before):
    case.assertIs(obj.animation_data.action, before['action'])
    case.assertEqual(contacts._action_signature(obj), before['action_signature'])
    case.assertEqual(workflow.raw_pose(obj), before['pose'])
    case.assertEqual(rig_state.mode_values(obj), before['modes'])
    case.assertEqual(tuple(value for row in obj.matrix_world for value in row), before['matrix'])
    case.assertEqual(_contact_state(obj), before['contacts'])


class ContactVisualizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest('Bforartists required')
        addon_utils.enable('rigify', default_set=True, persistent=False)
        b4artists_ml.register()

    def test_timing_matches_solver_weight_and_four_boundaries(self):
        item = SimpleNamespace(start=3.25, end=8.5, blend=1.5, strength=.8)
        expected = {
            1.0: 'Before', 2.5: 'Blend In', 3.25: 'Hold',
            7.0: 'Hold', 9.0: 'Blend Out', 10.0: 'After'}
        row = dict(start=item.start, end=item.end, blend=item.blend,
                   strength=item.strength)
        for frame, phase in expected.items():
            result = contact_visualization.timing(item, frame)
            self.assertEqual(result['phase'], phase)
            self.assertAlmostEqual(result['influence'], contact_math.weight(row, frame))
        self.assertEqual(
            [contact_visualization.review_frame(item, operation) for operation in
             ('GO_BLEND_IN', 'GO_START', 'GO_END', 'GO_BLEND_OUT')],
            [1.75, 3.25, 8.5, 10.0])
        RECORDS.append(dict(workflow='exact_timing_and_boundaries',
                            boundaries=[1.75, 3.25, 8.5, 10.0]))

    def test_review_buttons_move_only_the_playhead(self):
        obj, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        item = obj.b4ml.contacts[0]
        item.start = 3.25
        item.end = 8.5
        item.blend = 1.5
        obj.b4ml.contact_index = 0
        original_frame = posing._frame(scene)
        before = _protected(obj)
        frames = []
        for operation in ('GO_BLEND_IN', 'GO_START', 'GO_END', 'GO_BLEND_OUT'):
            self.assertEqual(bpy.ops.b4ml.contact(operation=operation), {'FINISHED'})
            frames.append(posing._frame(scene))
            scene.frame_set(math.floor(original_frame),
                            subframe=original_frame - math.floor(original_frame))
            _assert_protected(self, obj, before)
        self.assertEqual(frames, [1.75, 3.25, 8.5, 10.0])
        operations = {row[0] for row in
                      ui.B4ML_OT_contact.__annotations__['operation'].keywords['items']}
        self.assertTrue({'GO_BLEND_IN', 'GO_BLEND_OUT'} <= operations)
        RECORDS.append(dict(workflow='non_mutating_blend_review', frames=frames))

    def test_moving_platform_overlay_follows_evaluated_target(self):
        obj, scene, item, platform, _, _, _ = moving_platform_fixture()
        obj.b4ml.show_contacts = True
        obj.b4ml.show_contact_overlay = True
        obj.b4ml.show_all_contact_overlays = False
        original_frame = posing._frame(scene)
        before = _protected(obj)
        targets = []
        for frame in (3.0, 6.5, 9.0):
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            payload = contact_visualization.build_payload(obj, scene)
            self.assertEqual(len(payload), 1)
            expected = platform.matrix_world @ Vector(item.prop_point)
            self.assertLess((Vector(payload[0]['target']) - expected).length, 1e-7)
            self.assertTrue(math.isfinite(payload[0]['distance']))
            targets.append(payload[0]['target'])
        self.assertGreater((Vector(targets[-1]) - Vector(targets[0])).length, 1e-5)
        scene.frame_set(math.floor(original_frame),
                        subframe=original_frame - math.floor(original_frame))
        _assert_protected(self, obj, before)
        RECORDS.append(dict(workflow='moving_platform_overlay',
                            sampled_frames=[3.0, 6.5, 9.0], target_motion=True))

    def test_selected_and_all_review_colors_are_read_only(self):
        obj, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        first = obj.b4ml.contacts[0]
        first.start = 3.0
        first.end = 5.0
        first.blend = 1.0
        other = obj.b4ml.contacts.add()
        other.name = 'Rejected review marker'
        other.limb = 'arm-R'
        other.start = 7.0
        other.end = 8.0
        other.blend = 1.0
        other.strength = 1.0
        other.point = first.point
        other.rotation = first.rotation
        other.offset = first.offset
        other.review_state = 'REJECTED'
        other.enabled = False
        obj.b4ml.show_contacts = True
        obj.b4ml.show_contact_overlay = True
        obj.b4ml.contact_index = 0
        scene.frame_set(4)
        before = _protected(obj)
        selected = contact_visualization.build_payload(obj, scene)
        self.assertEqual([row['index'] for row in selected], [0])
        obj.b4ml.show_all_contact_overlays = True
        before_all = _protected(obj)
        payload = contact_visualization.build_payload(obj, scene)
        self.assertEqual({row['review_state'] for row in payload}, {'ACCEPTED', 'REJECTED'})
        self.assertGreater(next(row for row in payload if row['review_state'] == 'ACCEPTED')['color'][1], .8)
        self.assertGreater(next(row for row in payload if row['review_state'] == 'REJECTED')['color'][0], .8)
        _assert_protected(self, obj, before_all)
        obj.b4ml.show_all_contact_overlays = False
        _assert_protected(self, obj, before)

    def test_generated_quadruped_uses_its_normal_panel_state(self):
        scene, obj, source, source_signature, candidate, candidate_signature, _ = quadruped_candidate('cat')
        state = obj.b4ml
        state.show_contacts = False
        state.show_quadruped_contacts = True
        state.show_contact_overlay = True
        state.show_all_contact_overlays = False
        state.contact_index = 0
        scene.frame_set(5)
        before = _contact_state(obj)
        payload = contact_visualization.build_payload(obj, scene)
        self.assertEqual(len(payload), 1)
        self.assertIn(payload[0]['review_state'], {'ACCEPTED', 'PROPOSED', 'REJECTED'})
        self.assertTrue(math.isfinite(payload[0]['distance']))
        self.assertEqual(_contact_state(obj), before)
        self.assertEqual(quadruped_signature(obj, candidate), candidate_signature)
        self.assertEqual(quadruped_signature(obj, source), source_signature)
        state.show_quadruped_contacts = False
        self.assertEqual(contact_visualization.build_payload(obj, scene), [])
        RECORDS.append(dict(workflow='generated_quadruped_normal_panel_overlay', passed=True))

    def test_overlay_preferences_survive_save_reload(self):
        obj, _, _, _ = fixture('boneforge')
        obj.b4ml.show_contacts = True
        obj.b4ml.show_contact_overlay = False
        obj.b4ml.show_all_contact_overlays = True
        name = obj.name
        path = ROOT / 'training/b4artists_ml/cache/contact-visualization-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        self.assertTrue(obj.b4ml.show_contacts)
        self.assertFalse(obj.b4ml.show_contact_overlay)
        self.assertTrue(obj.b4ml.show_all_contact_overlays)
        RECORDS.append(dict(workflow='overlay_preferences_save_reload', passed=True))


def run_ui_smoke():
    ContactVisualizationTests.setUpClass()
    obj, _, _, _ = fixture('boneforge')
    scene = bpy.context.scene
    item = obj.b4ml.contacts[0]
    item.start = 3.0
    item.end = 7.0
    item.blend = 2.0
    item.strength = 1.0
    item.point = Vector(item.point) + Vector((.45, 0.0, .18))
    obj.b4ml.show_contacts = True
    obj.b4ml.show_contact_overlay = True
    obj.b4ml.show_all_contact_overlays = False
    obj.b4ml.contact_index = 0
    state = dict(name=obj.name, phase='operate', started=time.monotonic(), events=[])

    def tick():
        try:
            if time.monotonic() - state['started'] > 45:
                raise AssertionError('Contact visualization UI timed out')
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == 'VIEW_3D')
            region = next(value for value in area.regions if value.type == 'WINDOW')
            sidebar = next(value for value in area.regions if value.type == 'UI')
            area.spaces.active.show_region_ui = True
            for value in area.regions:
                if value.type == 'UI' and hasattr(value, 'active_panel_category'):
                    value.active_panel_category = 'B4Artists ML'
            obj = bpy.data.objects[state['name']]
            window.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=obj, active_object=obj,
                                           selected_objects=[obj], selected_editable_objects=[obj]):
                if state['phase'] == 'operate':
                    window.event_simulate(type='ESC', value='PRESS')
                    assert bpy.ops.b4ml.contact(operation='GO_BLEND_IN') == {'FINISHED'}
                    assert math.isclose(posing._frame(scene), 1.0)
                    assert bpy.ops.b4ml.contact(operation='GO_BLEND_OUT') == {'FINISHED'}
                    assert math.isclose(posing._frame(scene), 9.0)
                    scene.frame_set(2)
                    result = contact_visualization.build_payload(obj, scene)
                    assert len(result) == 1 and result[0]['phase'] == 'Blend In'
                    assert math.isclose(result[0]['influence'], .5)
                    state['events'].append('Blend boundaries and exact 50% influence reviewed')
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    state['phase'] = 'scroll'
                    state['scrolls'] = 0
                    return .25
                if state['phase'] == 'scroll':
                    window.cursor_warp(sidebar.x + sidebar.width // 2,
                                       sidebar.y + sidebar.height // 2)
                    window.event_simulate(type='WHEELDOWNMOUSE', value='PRESS',
                                          x=sidebar.x + sidebar.width // 2,
                                          y=sidebar.y + sidebar.height // 2)
                    state['scrolls'] += 1
                    if state['scrolls'] < 13:
                        return .04
                    state['phase'] = 'capture'
                    return .5
                path = ROOT / 'training/b4artists_ml/cache/contact-visualization-ui-v1.png'
                bpy.ops.screen.screenshot(filepath=str(path))
                result = contact_visualization.build_payload(obj, scene)[0]
                report = dict(passed=True, fixture='boneforge', events=state['events'],
                              phase=result['phase'], influence=result['influence'],
                              distance=result['distance'], handler_active=contact_visualization._HANDLER is not None,
                              screenshot=str(path.relative_to(ROOT)),
                              elapsed_seconds=time.monotonic() - state['started'])
                (ROOT / 'docs/b4artists_ml/contact-visualization-ui-v1.json').write_text(
                    json.dumps(report, indent=2) + '\n')
                print('CONTACT_VISUALIZATION_UI_RESULT: ' + json.dumps(report), flush=True)
                bpy.ops.wm.quit_blender()
                return None
        except Exception as exc:
            report = dict(passed=False, phase=state['phase'], error=str(exc),
                          traceback=traceback.format_exc(), events=state['events'])
            (ROOT / 'docs/b4artists_ml/contact-visualization-ui-v1.json').write_text(
                json.dumps(report, indent=2) + '\n')
            print('CONTACT_VISUALIZATION_UI_RESULT: ' + json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None
        return .05

    bpy.app.timers.register(tick, first_interval=.5)


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContactVisualizationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(tests=result.testsRun, passed=result.wasSuccessful(),
                  failures=len(result.failures), errors=len(result.errors),
                  skips=len(result.skipped), records=RECORDS,
                  package=b4artists_ml.__file__, runtime_sha256={
                      'contacts': _sha(contacts.__file__),
                      'contact_visualization': _sha(contact_visualization.__file__),
                      'ui': _sha(ROOT / 'b4artists_ml/ui.py'),
                      'test': _sha(__file__)})
    (ROOT / 'training/b4artists_ml/results/contact-visualization-v1.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('CONTACT_VISUALIZATION_RESULT: ' + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__' and '--ui-smoke' in sys.argv:
    run_ui_smoke()
elif __name__ == '__main__':
    run()
