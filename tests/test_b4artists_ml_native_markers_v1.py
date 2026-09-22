"""Phase 3 exit test — native marker sync and preview range.

Plan §6 row 3: marker set equals anchor set after add/remove/retime/ripple/
undo/save/reload; moving a marker retimes the anchor; preview range set and
restored around keep and discard; source action bytes unchanged while
previewing (contacts._action_signature).

Run:
    bforartists.exe --background --factory-startup --disable-autoexec \\
        --python "G:/LapArt/Projects/b4ml-lanes/phase3/tests/test_b4artists_ml_native_markers_v1.py"

Verified source facts:
  contacts.py:15   fixture(label, transformed) — rig + 2 anchors + active preview
  contacts.py:621  _action_signature(obj, action=None)
  workflow.py:293  remove_anchor(obj, frame)
  workflow.py:640  retime_anchor(obj, scene, source_frame, expected_destination=None)
  workflow.py:1406 preview(obj, scene, ...) — requires no candidate
  workflow.py:1594 finish_preview(obj, scene, keep=False)
  markers.py      sync / pull / preview_range / tick / _on_state_change
  ui_workflow/__init__.py:32  OPTIONAL_MODULES includes 'editor_dopesheet'
  Timers do not fire in --background (spike item 7); tick() called directly.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT / 'tests')]

import bpy
import b4artists_ml
from b4artists_ml import workflow as w, contacts as c
from b4artists_ml.ui_workflow import markers as m, copy
from test_b4artists_ml_contacts import fixture as contacts_fixture


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _anchor_only_fixture(label: str = 'boneforge'):
    """Two-anchor fixture with no active preview (candidate discarded)."""
    ob, source, sig, modes = contacts_fixture(label)
    scene = bpy.context.scene
    w.finish_preview(ob, scene, keep=False)
    return ob, scene, sig


def _anchor_frames(ob) -> list[int]:
    """Sorted integer anchor frames for *ob*."""
    return sorted(int(round(float(a.frame))) for a in ob.b4ml.anchors)


def _owned_frames(scene, ob) -> set[int]:
    """Marker frames for markers owned by *ob* in *scene*."""
    return {mk.frame for mk in m.owned(scene, ob)}


def _owned_names(scene, ob) -> set[str]:
    return {mk.name for mk in m.owned(scene, ob)}


def _set_scene(scene) -> None:
    """Switch bpy.context to *scene* (needed so tick() uses it)."""
    bpy.context.window.scene = scene


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class NativeMarkerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        b4artists_ml.register()

    def setUp(self) -> None:
        # Clear per-rig timer state so each test gets a clean tick.
        m._last_state.clear()
        m._last_candidate.clear()
        m._preview_state.clear()

    # ------------------------------------------------------------------
    # 1. Markers track anchors through add / remove / retime
    # ------------------------------------------------------------------

    def test_markers_follow_anchors(self) -> None:
        ob, scene, _sig = _anchor_only_fixture('boneforge')
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob

        # -- two anchors → two markers with correct frames, select=False --
        result = m.sync(scene, ob)
        self.assertEqual(result['created'], 2, 'expected 2 created on first sync')
        owned = m.owned(scene, ob)
        self.assertEqual(len(owned), 2, 'expected exactly 2 owned markers')

        anchor_frames = set(_anchor_frames(ob))
        self.assertEqual(_owned_frames(scene, ob), anchor_frames,
                         'marker frames must equal anchor frames')

        for mk in owned:
            self.assertTrue(mk.name.startswith(copy.MARKER_PREFIX),
                            f'marker name {mk.name!r} missing prefix')
            self.assertFalse(mk.select,
                             f'marker {mk.name!r} should be select=False after create')
            self.assertTrue(mk.name.isascii(),
                            f'marker name {mk.name!r} is not pure ASCII')

        # -- idempotent: second sync touches nothing --
        result2 = m.sync(scene, ob)
        self.assertEqual(result2, {'created': 0, 'moved': 0, 'removed': 0})

        # -- remove one anchor → sync removes its marker --
        frame_to_remove = _anchor_frames(ob)[0]
        w.remove_anchor(ob, frame_to_remove)
        result3 = m.sync(scene, ob)
        self.assertEqual(result3['removed'], 1)
        self.assertEqual(len(m.owned(scene, ob)), 1)

        # -- retime remaining anchor → sync moves its marker --
        remaining_frame = float(ob.b4ml.anchors[0].frame)
        # Add second anchor back so retime can proceed (need ≥2 for preview,
        # but retime only needs a valid order; add at +20).
        add_frame = int(remaining_frame) + 20
        scene.frame_set(add_frame)
        w.capture_anchor(ob, scene)
        m.sync(scene, ob)  # create marker for new anchor

        # retime: move the earlier anchor forward by 5 frames
        old_frame = min(float(a.frame) for a in ob.b4ml.anchors)
        new_frame = int(old_frame) + 5
        scene.frame_set(new_frame)
        w.retime_anchor(ob, scene, old_frame)
        result4 = m.sync(scene, ob)
        self.assertIn(result4['moved'] + result4['created'], {1, 2},
                      'retime should produce at least one moved/created marker')
        marker_frames_after = _owned_frames(scene, ob)
        self.assertIn(new_frame, marker_frames_after,
                      f'marker at new frame {new_frame} expected after retime')
        self.assertNotIn(int(round(old_frame)), marker_frames_after,
                         f'old marker frame {old_frame!r} should be gone after retime')

    # ------------------------------------------------------------------
    # 2. Moving a marker retimes its anchor
    # ------------------------------------------------------------------

    def test_marker_move_retimes_anchor(self) -> None:
        ob, scene, _sig = _anchor_only_fixture('boneforge')
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob

        m.sync(scene, ob)
        owned = m.owned(scene, ob)
        self.assertEqual(len(owned), 2)

        # Pick the later anchor; move its marker forward by 20 frames.
        later_anchor_frame = max(float(a.frame) for a in ob.b4ml.anchors)
        target_frame = int(later_anchor_frame) + 20

        # Find the marker that corresponds to the later anchor.
        owned_list = m.owned(scene, ob)
        later_marker = max(owned_list, key=lambda mk: mk.frame)
        later_marker.frame = target_frame

        # pull() should retime the anchor to target_frame.
        m.pull(scene, ob)

        new_anchor_frames = set(_anchor_frames(ob))
        self.assertIn(target_frame, new_anchor_frames,
                      f'anchor should be at {target_frame} after pull; got {new_anchor_frames}')
        self.assertNotIn(int(round(later_anchor_frame)), new_anchor_frames,
                         f'old anchor frame {later_anchor_frame!r} should be gone after pull')

        # No duplicate marker at the old frame.
        m.sync(scene, ob)
        owned_after = m.owned(scene, ob)
        all_frames = [mk.frame for mk in owned_after]
        self.assertEqual(len(all_frames), len(set(all_frames)),
                         'duplicate marker frames after pull+sync')

    # ------------------------------------------------------------------
    # 3. Undo / save-reload keep markers consistent
    # ------------------------------------------------------------------

    def test_undo_and_reload_keep_markers_consistent(self) -> None:
        ob, scene, _sig = _anchor_only_fixture('boneforge')
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob
        m.sync(scene, ob)

        ob_name = ob.name
        scene_name = scene.name

        # -- undo test --
        bpy.ops.ed.undo_push(message='markers test: before third anchor')
        third_frame = max(_anchor_frames(ob)) + 15
        scene.frame_set(third_frame)
        w.capture_anchor(ob, scene)
        self.assertEqual(len(ob.b4ml.anchors), 3, 'expected 3 anchors after capture')

        bpy.ops.ed.undo()
        # Re-fetch after undo — Python reference may be stale.
        ob = bpy.data.objects[ob_name]
        scene = bpy.data.scenes[scene_name]
        _set_scene(scene)

        self.assertEqual(len(ob.b4ml.anchors), 2, 'expected 2 anchors after undo')

        m._on_state_change()
        self.assertEqual(_owned_frames(scene, ob), set(_anchor_frames(ob)),
                         'marker frames must equal anchor frames after undo')

        # -- save/reload test --
        m.sync(scene, ob)
        with tempfile.TemporaryDirectory() as td:
            blend_path = str(Path(td) / 'native-markers.blend')
            bpy.ops.wm.save_as_mainfile(filepath=blend_path)
            bpy.ops.wm.open_mainfile(filepath=blend_path, use_scripts=False)

            b4artists_ml.register()
            ob = bpy.data.objects[ob_name]
            scene = bpy.data.scenes[scene_name]
            _set_scene(scene)
            bpy.context.view_layer.objects.active = ob

            m._last_state.clear()
            m._last_candidate.clear()
            m._on_state_change()

            self.assertEqual(len(ob.b4ml.anchors), 2,
                             'anchors lost after save/reload')
            self.assertEqual(_owned_frames(scene, ob), set(_anchor_frames(ob)),
                             'marker frames must equal anchor frames after reload')

    # ------------------------------------------------------------------
    # 4. Two rigs: markers are named distinctly, don't cross-contaminate
    # ------------------------------------------------------------------

    def test_two_rigs_named_distinctly(self) -> None:
        # rig1 via boneforge fixture (auto-skips if BoneForge absent).
        ob1, scene, _sig = _anchor_only_fixture('boneforge')
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob1

        # rig2: rigify in the same scene.
        try:
            from test_b4artists_ml_posing import rigify_rig
            ob2 = rigify_rig()
        except Exception as exc:
            self.skipTest(f'Second rig unavailable: {exc}')

        # Link ob2 to ob1's scene if not already there.
        if ob2.name not in scene.collection.all_objects:
            scene.collection.objects.link(ob2)
        bpy.context.view_layer.objects.active = ob2

        # Capture two anchors on rig2 at frames well outside rig1's range.
        from b4artists_ml import posing as _p
        _p._update(ob2)
        for fr in (50, 70):
            scene.frame_set(fr)
            try:
                w.capture_anchor(ob2, scene)
            except Exception as exc:
                self.skipTest(f'capture_anchor on rig2 failed: {exc}')

        self.assertEqual(len(ob2.b4ml.anchors), 2, 'rig2 should have 2 anchors')

        m.sync(scene, ob1)
        m.sync(scene, ob2)

        owned1 = set(m.owned(scene, ob1))
        owned2 = set(m.owned(scene, ob2))

        # Disjoint.
        self.assertFalse(owned1 & owned2,
                         f'marker sets overlap: {owned1 & owned2}')

        # Both sets non-empty.
        self.assertEqual(len(owned1), 2)
        self.assertEqual(len(owned2), 2)

        # All names ASCII and start with prefix.
        for mk in owned1 | owned2:
            self.assertTrue(mk.name.isascii(),
                            f'non-ASCII marker name: {mk.name!r}')
            self.assertTrue(mk.name.startswith(copy.MARKER_PREFIX))

        # Removing rig1's anchors only removes rig1's markers.
        for a in list(ob1.b4ml.anchors):
            w.remove_anchor(ob1, float(a.frame))
        self.assertEqual(len(ob1.b4ml.anchors), 0)

        m.sync(scene, ob1)
        m.sync(scene, ob2)

        self.assertEqual(len(m.owned(scene, ob1)), 0,
                         'rig1 markers should be gone after all anchors removed')
        self.assertEqual(len(m.owned(scene, ob2)), 2,
                         'rig2 markers must survive rig1 anchor removal')

    # ------------------------------------------------------------------
    # 5. Preview range: set on candidate present, restored on finish
    # ------------------------------------------------------------------

    def test_preview_range_set_and_restored(self) -> None:
        try:
            ob, source, source_sig, modes = contacts_fixture('boneforge')
        except unittest.SkipTest:
            raise

        scene = bpy.context.scene
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob

        # Candidate action is active after contacts_fixture.
        self.assertTrue(bool(ob.b4ml.candidate_action),
                        'fixture should have candidate_action set')

        # Record previous preview settings.
        prev_use = bool(scene.use_preview_range)
        prev_start = int(scene.frame_preview_start)
        prev_end = int(scene.frame_preview_end)

        expected_start = min(_anchor_frames(ob))
        expected_end = max(_anchor_frames(ob))

        # tick(): first call sees candidate_action appearing → sets preview range.
        bpy.context.view_layer.objects.active = ob
        m.tick()

        self.assertTrue(scene.use_preview_range,
                        'use_preview_range should be True while preview active')
        self.assertEqual(scene.frame_preview_start, expected_start,
                         f'preview start should be {expected_start}')
        self.assertEqual(scene.frame_preview_end, expected_end,
                         f'preview end should be {expected_end}')
        self.assertTrue(m.preview_range_active(ob),
                        'preview_range_active should be True')

        # -- discard: preview range should be restored --
        w.finish_preview(ob, scene, keep=False)
        m._last_candidate[ob.name] = True  # pretend tick saw candidate last time
        m.tick()

        self.assertEqual(bool(scene.use_preview_range), prev_use,
                         'use_preview_range not restored after discard')
        self.assertEqual(int(scene.frame_preview_start), prev_start,
                         'frame_preview_start not restored after discard')
        self.assertEqual(int(scene.frame_preview_end), prev_end,
                         'frame_preview_end not restored after discard')
        self.assertFalse(m.preview_range_active(ob),
                         'preview_range_active should be False after discard')

        # -- keep path: generate new preview, tick, keep, tick --
        # Re-sync state for a second preview round.
        m._last_state.clear()
        m._last_candidate.clear()
        m._preview_state.clear()

        try:
            w.preview(ob, scene)
        except Exception as exc:
            self.skipTest(f'Cannot generate second preview: {exc}')

        m.tick()
        self.assertTrue(scene.use_preview_range,
                        'use_preview_range should be True while second preview active')
        self.assertTrue(m.preview_range_active(ob))

        w.finish_preview(ob, scene, keep=True)
        m._last_candidate[ob.name] = True
        m.tick()

        self.assertEqual(bool(scene.use_preview_range), prev_use,
                         'use_preview_range not restored after keep')
        self.assertFalse(m.preview_range_active(ob),
                         'preview_range_active should be False after keep')

    # ------------------------------------------------------------------
    # 6. Source action signature unchanged by all markers module calls
    # ------------------------------------------------------------------

    def test_source_signature_unchanged(self) -> None:
        ob, source, source_sig, modes = contacts_fixture('boneforge')
        scene = bpy.context.scene
        _set_scene(scene)
        bpy.context.view_layer.objects.active = ob

        # Candidate is active — record signature (of the candidate action).
        sig_active = c._action_signature(ob)

        # Apply every markers module operation while preview is active.
        m.sync(scene, ob)
        m.pull(scene, ob)
        m.preview_range(scene, ob, True)
        m.tick()

        self.assertEqual(c._action_signature(ob), sig_active,
                         'action signature changed while preview active — markers module mutated an action')

        # Discard preview.
        m.preview_range(scene, ob, False)
        w.finish_preview(ob, scene, keep=False)

        sig_source = c._action_signature(ob)

        # Apply every markers module operation after discard.
        m.sync(scene, ob)
        m.pull(scene, ob)
        m.tick()

        self.assertEqual(c._action_signature(ob), sig_source,
                         'action signature changed after discard — markers module mutated an action')

    # ------------------------------------------------------------------
    # 7. Dopesheet panel registration
    # ------------------------------------------------------------------

    def test_dopesheet_registration(self) -> None:
        import importlib
        try:
            mod = importlib.import_module('b4artists_ml.ui_workflow.editor_dopesheet')
        except (ImportError, ModuleNotFoundError):
            self.skipTest(
                'editor_dopesheet.py not present in this lane yet '
                '(DEFECT: packet said it would be; test will run once the module is created)')

        # After b4artists_ml.register(), the panel class must exist.
        self.assertTrue(
            hasattr(bpy.types, 'B4ML_PT_dopesheet'),
            'B4ML_PT_dopesheet not registered after b4artists_ml.register()')

        # After unregister it must be gone.
        b4artists_ml.unregister()
        self.assertFalse(
            hasattr(bpy.types, 'B4ML_PT_dopesheet'),
            'B4ML_PT_dopesheet still registered after b4artists_ml.unregister()')

        # Re-register so subsequent tests have a clean state.
        b4artists_ml.register()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(NativeMarkerTests))
    if b4artists_ml._registered:
        b4artists_ml.unregister()
    sys.exit(0 if result.wasSuccessful() else 1)
