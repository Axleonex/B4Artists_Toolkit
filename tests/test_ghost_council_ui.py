"""Council regression coverage, run in Bforartists with --python-exit-code 1."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import GhostPaths, _cube, bpy, ghost_tool, mp


class CouncilUI(unittest.TestCase):
    setUp = GhostPaths.setUp
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def tearDown(self):
        from ghost_tool.session_state import SessionState
        SessionState.clear_all_instances()
        self._drop_deferred_timer()

    def pin(self, obj):
        entry = self.settings.motion_paths.add()
        entry.object_name = obj.name
        self.settings.motion_paths_index = len(self.settings.motion_paths) - 1
        return entry

    def test_custom_easing_operator_uses_all_four_offsets(self):
        from ghost_tool.ghost_data import Ghost, GhostStore
        obj = _cube()
        store = GhostStore.get(self.scene)
        store.clear()
        store.add(Ghost(frame=10, object_name=obj.name, channel='location.x', parent_frame_a=1, parent_frame_b=20))
        result = bpy.ops.ghost_tool.apply_easing(preset='CUSTOM', custom_left_x=.2,
                    custom_left_y=.4, custom_right_x=-.25, custom_right_y=-.3)
        self.assertEqual(result, {'FINISHED'})
        fc = ghost_tool.fcurve_utils.resolve_fcurve(obj, '', 'location.x')
        a, b = fc.keyframe_points
        self.assertAlmostEqual(a.handle_right.x, 1 + 19*.2, places=4)
        self.assertAlmostEqual(a.handle_right.y, 4*.4, places=4)
        self.assertAlmostEqual(b.handle_left.x, 20 - 19*.25, places=4)
        self.assertAlmostEqual(b.handle_left.y, 4 - 4*.3, places=4)

    def test_custom_easing_ui_routes_values(self):
        from ghost_tool.ui_panel import _draw_edit_motion
        from test_ghost_paths_folders import _Layout
        _cube()
        self.scene.ghost_tool_easing.active_preset = 'CUSTOM'
        layout = _Layout()
        _draw_edit_motion(layout, bpy.context)
        applied = next(c[4] for c in layout.calls if c[:2] == ('op', 'ghost_tool.apply_easing'))
        for name in ('custom_left_x','custom_left_y','custom_right_x','custom_right_y'):
            self.assertEqual(getattr(applied, name), getattr(self.scene.ghost_tool_easing, name))

    def test_named_handle_action_without_prototype_entry(self):
        from ghost_tool.ui_panel import _draw_motion_paths
        from test_ghost_paths_folders import _Layout
        layout = _Layout()
        _draw_motion_paths(layout, bpy.context)
        operators = [c for c in layout.calls if c[0] == 'op']
        self.assertTrue(any('ghost_tool.path_handle_drag' in c for c in operators))
        self.assertFalse(any('ghost_tool.open_settings_editor' in c for c in operators))
        prop = bpy.ops.ghost_tool.path_handle_drag.get_rna_type().properties['wait_for_click']
        self.assertTrue(prop.is_hidden)

    def test_target_survives_selection_and_row_reordering(self):
        from ghost_tool.settings_editor import capture_target, resolve_target
        first = _cube('First')
        self.pin(first)
        target = capture_target(bpy.context)
        second = _cube('Second')
        self.pin(second)
        self.settings.motion_paths.move(0, 1)
        entry, reason = resolve_target(target, self.scene)
        self.assertEqual(reason, '')
        self.assertEqual(entry.object_name, first.name)
        self.assertEqual(bpy.context.active_object, second)
        # Deliberate refresh captures the selected row rather than silently changing the old target.
        self.settings.motion_paths_index = 0
        new = capture_target(bpy.context)
        self.assertEqual(new.obj, second)

    def test_deleted_path_does_not_retarget_to_replacement(self):
        from ghost_tool.settings_editor import capture_target, resolve_target
        obj = _cube()
        self.pin(obj)
        target = capture_target(bpy.context)
        self.settings.motion_paths.clear()
        self.pin(obj)
        entry, reason = resolve_target(target, self.scene)
        self.assertIsNone(entry)
        self.assertIn('removed', reason)

    def test_scene_switch_and_object_deletion_disable_target(self):
        from ghost_tool.settings_editor import capture_target, resolve_target
        obj = _cube()
        self.pin(obj)
        target = capture_target(bpy.context)
        other = bpy.data.scenes.new('Other')
        self.assertIn('Scene changed', resolve_target(target, other)[1])
        bpy.data.scenes.remove(other)
        bpy.data.objects.remove(obj)
        self.assertTrue(resolve_target(target, self.scene)[1])

    def test_one_gesture_owner_and_only_owner_can_release(self):
        from ghost_tool.session_state import SessionState as S
        a, b = object(), object()
        self.assertTrue(S.begin_gesture(a, self.scene))
        self.assertFalse(S.begin_gesture(b, self.scene))
        S.end_gesture(b)
        self.assertTrue(S.owns_gesture(a, self.scene))
        S.get(self.scene).clear_all()
        self.assertTrue(S.get(self.scene).drag_active)
        S.end_gesture(a)
        self.assertTrue(S.available())
        self.assertFalse(S.get(self.scene).drag_active)

    def test_all_editing_gestures_reject_competing_owner_before_work(self):
        from ghost_tool.session_state import SessionState as S
        from ghost_tool.modal_operator import GhostDragOperator
        from ghost_tool.selection_operators import GHOST_OT_box_select
        from ghost_tool.path_handle_drag import GHOST_OT_path_handle_drag
        from ghost_tool.physics_suggest import GHOST_OT_physics_suggest
        owner = object()
        S.begin_gesture(owner, self.scene)
        contender = SimpleNamespace(report=lambda *args: None)
        for operator in (GhostDragOperator, GHOST_OT_box_select, GHOST_OT_path_handle_drag, GHOST_OT_physics_suggest):
            self.assertEqual(operator.invoke(contender, bpy.context, None), {'CANCELLED'})
            self.assertTrue(S.owns_gesture(owner, self.scene))

    def test_armed_handle_cancel_releases_without_edit(self):
        from ghost_tool.path_handle_drag import GHOST_OT_path_handle_drag as Op
        from ghost_tool.session_state import SessionState as S
        owner = SimpleNamespace(_drag=None)
        owner._finish = lambda context: Op._finish(owner, context)
        owner._modal_inner = lambda context, event: Op._modal_inner(owner, context, event)
        context = SimpleNamespace(scene=self.scene, workspace=SimpleNamespace(status_text_set=lambda _: None))
        S.begin_gesture(owner, self.scene)
        with patch('ghost_tool.path_handle_drag.tag_viewport_redraw'):
            self.assertEqual(Op.modal(owner, context, SimpleNamespace(type='ESC',value='PRESS')), {'CANCELLED'})
        self.assertTrue(S.available())

    def test_file_load_clears_editor_and_gesture_runtime(self):
        from ghost_tool import settings_editor as editor
        from ghost_tool.session_state import SessionState as S
        obj = _cube()
        self.pin(obj)
        editor._targets[123] = editor.capture_target(bpy.context)
        S.begin_gesture(object(), self.scene)
        editor._clear_on_load()
        S.clear_all_instances()
        self.assertFalse(editor._targets)
        self.assertTrue(S.available())
        self.assertEqual(self.settings.motion_paths[0].object_name, obj.name)

    def test_stale_window_pointer_cannot_claim_unowned_window(self):
        from ghost_tool import settings_editor as editor
        _cube()
        target = editor.capture_target(bpy.context)
        pointer = bpy.context.window.as_pointer()
        editor._targets[pointer] = target
        try:
            self.assertFalse(editor.is_editor(bpy.context))
            target.editor_window = bpy.context.window
            self.assertTrue(editor.is_editor(bpy.context))
        finally:
            editor._targets.pop(pointer, None)

    def test_editor_draws_only_real_properties_and_disabled_targets_draw_no_fields(self):
        from ghost_tool import settings_editor as editor
        from test_ghost_paths_folders import _Layout
        obj = _cube()
        self.pin(obj)
        target = editor.capture_target(bpy.context)
        target.editor_window = bpy.context.window
        pointer = bpy.context.window.as_pointer()
        editor._targets[pointer] = target
        class Layout(_Layout):
            def row(self, **kw):
                return Layout(self.calls)
            column = row
            box = row
            def panel(self, *args, **kw):
                return self, self
            def prop(self, data, name, **kw):
                getattr(data, name)  # fail on a stale field or RNA property
                super().prop(data, name, **kw)
        try:
            layout = Layout()
            editor.draw_editor(layout, bpy.context)
            self.assertTrue(any(c[0] == 'prop' for c in layout.calls))
            self.settings.motion_paths.clear()
            invalid = Layout()
            editor.draw_editor(invalid, bpy.context)
            self.assertFalse(any(c[0] == 'prop' for c in invalid.calls))
        finally:
            editor._targets.pop(pointer, None)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CouncilUI))
    if not result.wasSuccessful():
        raise RuntimeError('Council regressions failed')
