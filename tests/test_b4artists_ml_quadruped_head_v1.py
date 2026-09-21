"""Bforartists evidence for a generated-Rigify quadruped Head target."""
from pathlib import Path
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
from mathutils import Matrix, Quaternion, Vector
import b4artists_ml
from b4artists_ml import quadruped_pose, workflow
from test_b4artists_ml_quadruped_pose import _action_signature, _generate


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(obj, scene):
    scene.frame_set(7)
    root = obj.pose.bones['root']
    root.location = (.011, -.006, .003)
    root.keyframe_insert('location', frame=7)
    action = obj.animation_data.action
    return workflow.raw_pose(obj), action, _action_signature(obj, action)


def _head(obj):
    profile, _, _ = quadruped_pose.binding(obj)
    return profile.roles['head']


class QuadrupedHeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest('Bforartists required')
        addon_utils.enable('rigify', default_set=True, persistent=False)
        b4artists_ml.register()

    def test_cat_horse_wolf_head_rotation_preserves_body_and_paw_pins(self):
        for name in ('cat', 'horse', 'wolf'):
            with self.subTest(profile=name):
                scene, obj = _generate(name)
                source, action, action_signature = _source(obj, scene)
                self.assertEqual(quadruped_pose.begin(obj, scene), 6)
                target = obj.b4ml.quadruped_targets['Head']
                self.assertEqual(tuple(target.target.lock_location), (True, True, True))
                self.assertTrue(target.use_orientation)
                requested = (Quaternion(Vector((.2, .6, .3)).normalized(), .16) @
                             target.target.rotation_quaternion).normalized()
                target.target.rotation_quaternion = requested
                bpy.context.view_layer.update()
                metrics = quadruped_pose.solve(obj, scene)
                self.assertIn('Head', metrics['orientation_errors'])
                self.assertLessEqual(metrics['orientation_errors']['Head'],
                                     metrics['orientation_tolerance'])
                self.assertLessEqual(metrics['max_paw_error'], metrics['tolerance'])
                self.assertLessEqual(metrics['body_error'], metrics['tolerance'])
                actual = (obj.matrix_world @ obj.pose.bones[_head(obj)].matrix).to_quaternion()
                self.assertLessEqual(actual.rotation_difference(requested).angle,
                                     metrics['orientation_tolerance'])
                quadruped_pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                RECORDS.append(dict(profile=name, head_error=metrics['orientation_errors']['Head'],
                                    paw_error=metrics['max_paw_error'], source_restored=True))

    def test_locked_or_constrained_head_fails_atomically(self):
        scene, obj = _generate('cat')
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        target = obj.b4ml.quadruped_targets['Head']
        target.target.rotation_quaternion = (
            Quaternion(Vector((0, 0, 1)), .1) @ target.target.rotation_quaternion)
        head = obj.pose.bones[_head(obj)]
        head.lock_rotation[0] = True
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, 'unlocked rotation'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        head.lock_rotation[0] = False
        constraint = head.constraints.new('COPY_ROTATION')
        constraint.name = 'Animator Head Constraint'
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, 'constrained control'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        head.constraints.remove(constraint)
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_unsupported_rig_spaces_and_driven_head_fail_before_mutation(self):
        scene, obj = _generate('cat')
        source, action, action_signature = _source(obj, scene)
        original = obj.matrix_world.copy()
        objects = set(bpy.data.objects)
        cases = []
        nonuniform = original.copy()
        nonuniform.col[0] *= 1.2
        cases.append(('nonuniform', nonuniform, 'uniform object scale without shear'))
        reflected = original.copy()
        reflected.col[0] *= -1.0
        cases.append(('reflected', reflected, 'reflected or zero object scale'))
        sheared = original.copy()
        sheared[0][1] += 0.2
        cases.append(('sheared', sheared, 'uniform object scale without shear'))
        for label, matrix, message in cases:
            with self.subTest(space=label):
                obj.matrix_world = matrix
                bpy.context.view_layer.update()
                with self.assertRaisesRegex(ValueError, message):
                    quadruped_pose.begin(obj, scene)
                self.assertFalse(obj.b4ml.quadruped_payload)
                self.assertEqual(len(obj.b4ml.quadruped_targets), 0)
                self.assertEqual(set(bpy.data.objects), objects)
                self.assertEqual(workflow.raw_pose(obj), source)
                obj.matrix_world = original
                bpy.context.view_layer.update()

        head = obj.pose.bones[_head(obj)]
        driver = head.driver_add('rotation_quaternion', 0)
        driver.driver.expression = '0.0'
        with self.assertRaisesRegex(ValueError, 'driven control'):
            quadruped_pose.begin(obj, scene)
        self.assertFalse(obj.b4ml.quadruped_payload)
        self.assertEqual(set(bpy.data.objects), objects)
        head.driver_remove('rotation_quaternion', 0)

        quadruped_pose.begin(obj, scene)
        solved_pose = workflow.raw_pose(obj)
        obj.scale.x *= 1.1
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, 'uniform object scale without shear'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), solved_pose)
        obj.matrix_world = original
        bpy.context.view_layer.update()
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_head_helper_position_and_external_ownership_fail_atomically(self):
        scene, obj = _generate('horse')
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        item = obj.b4ml.quadruped_targets['Head']
        helper = item.target
        original = helper.matrix_world.copy()
        original_location = helper.location.copy()
        preview = workflow.raw_pose(obj)

        helper.lock_location[0] = False
        with self.assertRaisesRegex(ValueError, 'location must remain locked'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.lock_location = (True, True, True)
        helper.location.x += 0.01
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, 'position changed'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.matrix_world = original
        helper.location = original_location
        bpy.context.view_layer.update()

        parent = bpy.data.objects.new('External Head Parent', None)
        scene.collection.objects.link(parent)
        helper.parent = parent
        with self.assertRaisesRegex(ValueError, 'parenting is not supported'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.parent = None
        helper.matrix_world = original
        helper.location = original_location
        constraint = helper.constraints.new('COPY_ROTATION')
        with self.assertRaisesRegex(ValueError, 'constraints are not supported'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.constraints.remove(constraint)
        driver = helper.driver_add('rotation_quaternion', 0)
        driver.driver.expression = '0.0'
        with self.assertRaisesRegex(ValueError, 'animation or drivers are not supported'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.driver_remove('rotation_quaternion', 0)
        helper.delta_location.x = 0.01
        with self.assertRaisesRegex(ValueError, 'delta transforms are not supported'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        helper.delta_location = (0.0, 0.0, 0.0)

        helper.keyframe_insert('rotation_quaternion', frame=1)
        ad = helper.animation_data
        nla_action = ad.action
        ad.action = None
        track = ad.nla_tracks.new()
        track.name = 'External Head NLA'
        track.strips.new('External Head Rotation', 1, nla_action)
        with self.assertRaisesRegex(ValueError, 'animation or drivers are not supported'):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        ad.nla_tracks.remove(track)
        bpy.data.actions.remove(nla_action)
        helper.location = original_location
        # Parenting round-trips can leave one float ULP of decomposed scale drift.
        helper.scale = (1.0, 1.0, 1.0)
        bpy.data.objects.remove(parent, do_unlink=True)

        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_head_session_native_undo_redo(self):
        scene, obj = _generate('wolf')
        source, action, action_signature = _source(obj, scene)
        action_name = action.name
        name = obj.name
        bpy.ops.ed.undo_push(message='Before quadruped Head session')
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(operation='BEGIN'), {'FINISHED'})
        bpy.ops.ed.undo_push(message='Started quadruped Head session')
        self.assertEqual(bpy.ops.ed.undo(), {'FINISHED'})
        obj = bpy.data.objects[name]
        self.assertFalse(obj.b4ml.quadruped_payload)
        self.assertEqual(len(obj.b4ml.quadruped_targets), 0)
        self.assertEqual(bpy.ops.ed.redo(), {'FINISHED'})
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        record = json.loads(obj.b4ml.quadruped_payload)
        self.assertEqual(record['schema'], 3)
        self.assertIsNotNone(obj.b4ml.quadruped_targets.get('Head'))
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)
        RECORDS.append(dict(workflow='head_session_native_undo_redo', passed=True))

    def test_schema_one_pending_preview_remains_recoverable(self):
        scene, obj = _generate('horse')
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        state = obj.b4ml
        record = json.loads(state.quadruped_payload)
        head_index = next(index for index, item in enumerate(state.quadruped_targets)
                          if item.name == 'Head')
        helper = state.quadruped_targets[head_index].target
        state.quadruped_targets.remove(head_index)
        bpy.data.objects.remove(helper, do_unlink=True)
        record['schema'] = 1
        record['origins'].pop('Head', None)
        record['orientations'].pop('Head', None)
        state.quadruped_payload = json.dumps(record, allow_nan=False)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertNotIn('Head', metrics['orientation_errors'])
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)
        RECORDS.append(dict(workflow='schema_one_pending_preview_recovery', passed=True))

    def test_solved_head_target_survives_reload_and_keeps(self):
        scene, obj = _generate('wolf')
        source, action, action_signature = _source(obj, scene)
        action_name = action.name
        quadruped_pose.begin(obj, scene)
        target = obj.b4ml.quadruped_targets['Head']
        target.target.rotation_quaternion = (
            Quaternion(Vector((.4, .1, .7)).normalized(), .08) @
            target.target.rotation_quaternion)
        bpy.context.view_layer.update()
        metrics = quadruped_pose.solve(obj, scene)
        self.assertLessEqual(metrics['orientation_errors']['Head'],
                             metrics['orientation_tolerance'])
        name = obj.name
        path = ROOT / 'training/b4artists_ml/cache/quadruped-head-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(json.loads(obj.b4ml.quadruped_payload)['schema'], 3)
        self.assertIsNotNone(obj.b4ml.quadruped_targets.get('Head'))
        quadruped_pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)
        RECORDS.append(dict(workflow='head_save_reload_keep', anchor_saved=True))


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedHeadTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(tests=result.testsRun, passed=result.wasSuccessful(),
                  failures=len(result.failures), errors=len(result.errors),
                  skips=len(result.skipped), records=RECORDS,
                  package=b4artists_ml.__file__, runtime_sha256={
                      'quadruped_pose': _sha(quadruped_pose.__file__),
                      'ui': _sha(ROOT / 'b4artists_ml/ui.py'),
                      'test': _sha(__file__)})
    (ROOT / 'training/b4artists_ml/results/quadruped-head-v1.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('QUADRUPED_HEAD_RESULT: ' + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)


def run_ui_smoke():
    QuadrupedHeadTests.setUpClass()
    scene, obj = _generate('cat')
    _source(obj, scene)
    state = dict(name=obj.name, phase='operate', started=time.monotonic(), scrolls=0,
                 events=[])

    def tick():
        try:
            if time.monotonic() - state['started'] > 45:
                raise AssertionError('Quadruped Head UI timed out')
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == 'VIEW_3D')
            region = next(value for value in area.regions if value.type == 'WINDOW')
            sidebar = next(value for value in area.regions if value.type == 'UI')
            area.spaces.active.show_region_ui = True
            if hasattr(sidebar, 'active_panel_category'):
                sidebar.active_panel_category = 'B4Artists ML'
            obj = bpy.data.objects[state['name']]
            window.view_layer.objects.active = obj
            obj.select_set(True)
            override = dict(window=window, area=area, region=region, object=obj,
                            active_object=obj, selected_objects=[obj],
                            selected_editable_objects=[obj])
            with bpy.context.temp_override(**override):
                if state['phase'] == 'operate':
                    window.event_simulate(type='ESC', value='PRESS')
                    assert bpy.ops.b4ml.quadruped_pose(operation='BEGIN') == {'FINISHED'}
                    target = obj.b4ml.quadruped_targets['Head']
                    requested = (Quaternion(Vector((.2, .6, .3)).normalized(), .16) @
                                 target.target.rotation_quaternion).normalized()
                    target.target.rotation_quaternion = requested
                    bpy.context.view_layer.update()
                    assert bpy.ops.b4ml.quadruped_pose(operation='SOLVE') == {'FINISHED'}
                    metrics = json.loads(obj.b4ml.quadruped_payload)['metrics']
                    assert metrics['orientation_errors']['Head'] <= metrics['orientation_tolerance']
                    assert tuple(target.target.lock_location) == (True, True, True)
                    state['metrics'] = metrics
                    state['events'].append('Head target rotated and solved through the visible operator')
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    state['phase'] = 'scroll'
                    return .35
                if state['phase'] == 'scroll':
                    window.cursor_warp(sidebar.x + sidebar.width // 2,
                                       sidebar.y + sidebar.height // 2)
                    window.event_simulate(type='WHEELDOWNMOUSE', value='PRESS',
                                          x=sidebar.x + sidebar.width // 2,
                                          y=sidebar.y + sidebar.height // 2)
                    state['scrolls'] += 1
                    if state['scrolls'] < 28:
                        return .035
                    state['phase'] = 'capture'
                    return .6
                path = ROOT / 'training/b4artists_ml/cache/quadruped-head-ui-v1.png'
                bpy.ops.screen.screenshot(filepath=str(path))
                metrics = state['metrics']
                report = dict(passed=True, fixture='generated Rigify cat',
                              events=state['events'], target='Head',
                              location_locked=True,
                              head_orientation_error=metrics['orientation_errors']['Head'],
                              orientation_tolerance=metrics['orientation_tolerance'],
                              max_paw_error=metrics['max_paw_error'],
                              paw_tolerance=metrics['tolerance'],
                              screenshot=str(path.relative_to(ROOT)),
                              screenshot_sha256=_sha(path),
                              elapsed_seconds=time.monotonic() - state['started'])
                quadruped_pose.finish(obj, scene, False)
                report['source_restored_after_cancel'] = not obj.b4ml.quadruped_payload
                (ROOT / 'docs/b4artists_ml/quadruped-head-ui-v1.json').write_text(
                    json.dumps(report, indent=2) + '\n')
                print('QUADRUPED_HEAD_UI_RESULT: ' + json.dumps(report), flush=True)
                bpy.ops.wm.quit_blender()
                return None
        except Exception as exc:
            report = dict(passed=False, phase=state['phase'], error=str(exc),
                          traceback=traceback.format_exc(), events=state['events'])
            (ROOT / 'docs/b4artists_ml/quadruped-head-ui-v1.json').write_text(
                json.dumps(report, indent=2) + '\n')
            print('QUADRUPED_HEAD_UI_RESULT: ' + json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None

    bpy.app.timers.register(tick, first_interval=.5)


if __name__ == '__main__' and '--ui-smoke' in sys.argv:
    run_ui_smoke()
elif __name__ == '__main__':
    run()
