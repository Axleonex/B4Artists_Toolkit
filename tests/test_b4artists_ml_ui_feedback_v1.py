"""
Pure tests for b4artists_ml/ui_workflow/feedback.py (feedback-2 packet).
Contract §MAPPING TABLES "FAILURE list → feedback.py levels and fix operators".

No Blender dependency — feedback.py loaded via importlib so no package import needed.
Module registered as 'b4artists_ml.ui_workflow.feedback' with the correct
__package__ so the relative import inside guarded() (`from .. import workflow`)
can resolve against sys.modules when tests need to exercise the rig-found path.
"""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Load feedback.py by path (avoids requiring the full b4artists_ml package).
# Register under the canonical dotted name so `from .. import workflow` resolves.
# ---------------------------------------------------------------------------
_FEEDBACK_PATH = Path(__file__).parent.parent / 'b4artists_ml' / 'ui_workflow' / 'feedback.py'
_spec = importlib.util.spec_from_file_location(
    'b4artists_ml.ui_workflow.feedback', _FEEDBACK_PATH,
)
fb = importlib.util.module_from_spec(_spec)
fb.__package__ = 'b4artists_ml.ui_workflow'

# Stub parent packages so Python's import machinery is satisfied.
_pkg_b4ml = types.ModuleType('b4artists_ml')
_pkg_ui = types.ModuleType('b4artists_ml.ui_workflow')
sys.modules.setdefault('b4artists_ml', _pkg_b4ml)
sys.modules.setdefault('b4artists_ml.ui_workflow', _pkg_ui)
sys.modules['b4artists_ml.ui_workflow.feedback'] = fb

_spec.loader.exec_module(fb)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ns(**kw):
    """Return a minimal feedback holder (SimpleNamespace) with default fields."""
    defaults = dict(
        feedback_level='INFO', feedback_text='', feedback_fix='',
        feedback_fix_props='', feedback_fix_label='', feedback_stamp=0,
    )
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


_VALID_FIX_OPS = frozenset({
    'b4ml.action', 'b4ml.body', 'b4ml.body_solve', 'screen.animation_play', '',
})


# ---------------------------------------------------------------------------
# Contract table assertions
# ---------------------------------------------------------------------------
class FeedbackContractTests(unittest.TestCase):
    CONTRACT_KEYS = frozenset({
        'mapping_failure', 'begin_while_playing', 'solve_failure',
        'session_blocks_review', 'restore_wrong_action',
        'preview_exists', 'motion_layer_blocking',
    })

    def test_failures_has_exactly_seven_keys(self):
        self.assertEqual(set(fb.FAILURES.keys()), self.CONTRACT_KEYS)

    def test_all_levels_valid(self):
        for key, (level, *_) in fb.FAILURES.items():
            with self.subTest(key=key):
                self.assertIn(level, fb.LEVELS)

    def test_all_fix_operators_valid(self):
        for key, (level, tmpl, fix_op, fix_props, fix_label) in fb.FAILURES.items():
            with self.subTest(key=key):
                self.assertIn(fix_op, _VALID_FIX_OPS)

    # Verbatim contract checks — Contract §MAPPING TABLES row by row.
    def test_mapping_failure_verbatim(self):
        level, tmpl, fix_op, fix_props, fix_label = fb.FAILURES['mapping_failure']
        self.assertEqual(level, 'ERROR')
        self.assertEqual(fix_op, 'b4ml.action')
        self.assertEqual(fix_props, {'operation': 'INSPECT'})
        self.assertEqual(fix_label, 'Check Rig')

    def test_begin_while_playing_verbatim(self):
        level, tmpl, fix_op, fix_props, fix_label = fb.FAILURES['begin_while_playing']
        self.assertEqual(level, 'ERROR')
        self.assertEqual(fix_op, 'screen.animation_play')
        self.assertEqual(fix_label, 'Stop Playback')

    def test_restore_wrong_action_verbatim(self):
        level, tmpl, fix_op, fix_props, fix_label = fb.FAILURES['restore_wrong_action']
        self.assertEqual(level, 'ERROR')
        self.assertEqual(fix_op, 'b4ml.action')
        self.assertEqual(fix_props, {'operation': 'SELECT_KEPT'})
        self.assertEqual(fix_label, 'Select Kept Result')

    def test_session_blocks_review_verbatim(self):
        level, tmpl, fix_op, fix_props, fix_label = fb.FAILURES['session_blocks_review']
        self.assertEqual(level, 'INFO')
        self.assertEqual(fix_op, '')
        self.assertEqual(fix_label, '')

    # classify() — real ValueError messages from source, cited by file:line.
    def test_classify_begin_while_playing(self):
        # body_preview.py:182: raise ValueError('Stop playback before posing')
        self.assertEqual(fb.classify('Stop playback before posing'), 'begin_while_playing')

    def test_classify_session_blocks_review(self):
        # workflow.py:1597: raise ValueError('Finish or cancel the active pose preview first')
        self.assertEqual(
            fb.classify('Finish or cancel the active pose preview first'),
            'session_blocks_review',
        )

    def test_classify_restore_wrong_action(self):
        # workflow.py:1654: raise ValueError('Select the last kept candidate before restoring its source')
        self.assertEqual(
            fb.classify('Select the last kept candidate before restoring its source'),
            'restore_wrong_action',
        )

    def test_classify_preview_exists(self):
        # workflow.py:1413: raise ValueError('Keep or discard the current candidate first')
        self.assertEqual(
            fb.classify('Keep or discard the current candidate first'),
            'preview_exists',
        )

    def test_classify_motion_layer_blocking(self):
        # workflow.py:1414: raise ValueError('Restore the kept motion source before generating another candidate')
        self.assertEqual(
            fb.classify('Restore the kept motion source before generating another candidate'),
            'motion_layer_blocking',
        )

    def test_classify_unknown_returns_none(self):
        self.assertIsNone(fb.classify('totally unrelated text'))

    def test_classify_empty_returns_none(self):
        self.assertIsNone(fb.classify(''))


# ---------------------------------------------------------------------------
# API surface tests
# ---------------------------------------------------------------------------
class FeedbackApiTests(unittest.TestCase):

    def test_set_feedback_writes_all_fields(self):
        h = _ns()
        fb.set_feedback(h, 'ERROR', 'oops', 'b4ml.action', 'Fix It', operation='INSPECT')
        self.assertEqual(h.feedback_level, 'ERROR')
        self.assertEqual(h.feedback_text, 'oops')
        self.assertEqual(h.feedback_fix, 'b4ml.action')
        self.assertEqual(h.feedback_fix_label, 'Fix It')
        self.assertEqual(json.loads(h.feedback_fix_props), {'operation': 'INSPECT'})

    def test_stamp_increments_on_every_set(self):
        h = _ns()
        fb.set_feedback(h, 'INFO', 'a')
        self.assertEqual(h.feedback_stamp, 1)
        fb.set_feedback(h, 'INFO', 'b')
        self.assertEqual(h.feedback_stamp, 2)
        fb.set_feedback(h, 'INFO', 'c')
        self.assertEqual(h.feedback_stamp, 3)

    def test_no_props_gives_empty_fix_props(self):
        h = _ns()
        fb.set_feedback(h, 'INFO', 'x')
        self.assertEqual(h.feedback_fix_props, '')

    def test_props_serialized_to_json(self):
        h = _ns()
        fb.set_feedback(h, 'ERROR', 'x', operation='INSPECT', count=2)
        parsed = json.loads(h.feedback_fix_props)
        self.assertEqual(parsed['operation'], 'INSPECT')
        self.assertEqual(parsed['count'], 2)

    def test_info_helper(self):
        h = _ns()
        fb.info(h, 'hello')
        self.assertEqual(h.feedback_level, 'INFO')
        self.assertEqual(h.feedback_text, 'hello')

    def test_success_helper(self):
        h = _ns()
        fb.success(h, 'done')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_warning_helper(self):
        h = _ns()
        fb.warning(h, 'watch out')
        self.assertEqual(h.feedback_level, 'WARNING')

    def test_error_helper_with_fix(self):
        h = _ns()
        fb.error(h, 'bad', fix='b4ml.action', fix_label='Fix', operation='INSPECT')
        self.assertEqual(h.feedback_level, 'ERROR')
        self.assertEqual(h.feedback_fix, 'b4ml.action')
        self.assertEqual(json.loads(h.feedback_fix_props), {'operation': 'INSPECT'})

    def test_clear_resets_to_info_empty(self):
        h = _ns()
        fb.error(h, 'bad')
        fb.clear(h)
        self.assertEqual(h.feedback_level, 'INFO')
        self.assertEqual(h.feedback_text, '')

    def test_current_returns_snapshot_dict(self):
        h = _ns()
        fb.error(h, 'x', fix='b4ml.action', fix_label='L', operation='INSPECT')
        snap = fb.current(h)
        self.assertEqual(snap['level'], 'ERROR')
        self.assertEqual(snap['fix'], 'b4ml.action')
        self.assertEqual(snap['fix_label'], 'L')
        self.assertIn('operation', json.loads(snap['fix_props']))
        self.assertIsInstance(snap['stamp'], int)

    def test_holder_resolves_b4ml_ui_attribute(self):
        """_holder returns target.b4ml_ui when present; otherwise target itself."""
        inner = _ns()
        outer = types.SimpleNamespace(b4ml_ui=inner)
        fb.set_feedback(outer, 'SUCCESS', 'via outer')
        # Writes routed to inner, not outer.
        self.assertEqual(inner.feedback_level, 'SUCCESS')
        self.assertEqual(inner.feedback_text, 'via outer')
        self.assertFalse(hasattr(outer, 'feedback_level'))


# ---------------------------------------------------------------------------
# guarded() tests — rig NOT found (relative import fails in pure context)
# ---------------------------------------------------------------------------
class GuardedTests(unittest.TestCase):
    """
    Tests for guarded() when workflow.active_rig cannot be resolved.

    guarded() does `from .. import workflow as _wf` inside a try/except.
    In a pure test that calls the wrapper before sys.modules has
    'b4artists_ml.workflow', the relative import raises ImportError → rig = None.
    The rig-found path is tested in GuardedWithRigTests below via monkeypatching.
    """

    def setUp(self):
        # Ensure no workflow stub leaks in from GuardedWithRigTests.
        sys.modules.pop('b4artists_ml.workflow', None)

    class _Op:
        def __init__(self):
            self.reported = []
        def report(self, cats, msg):
            self.reported.append((cats, msg))

    def test_value_error_returns_cancelled(self):
        @fb.guarded
        def execute(self, context):
            # body_preview.py:182 exact message
            raise ValueError('Stop playback before posing')
        op = self._Op()
        result = execute(op, types.SimpleNamespace())
        self.assertEqual(result, {'CANCELLED'})

    def test_value_error_calls_report_with_error_category(self):
        @fb.guarded
        def execute(self, context):
            raise ValueError('Stop playback before posing')
        op = self._Op()
        execute(op, types.SimpleNamespace())
        self.assertTrue(op.reported)
        cats, _ = op.reported[0]
        self.assertIn('ERROR', cats)

    def test_success_passthrough(self):
        @fb.guarded
        def execute(self, context):
            return {'FINISHED'}
        op = self._Op()
        self.assertEqual(execute(op, types.SimpleNamespace()), {'FINISHED'})

    def test_none_return_passthrough(self):
        @fb.guarded
        def execute(self, context):
            return None
        op = self._Op()
        self.assertIsNone(execute(op, types.SimpleNamespace()))

    def test_non_value_error_propagates(self):
        @fb.guarded
        def execute(self, context):
            raise RuntimeError('internal crash')
        op = self._Op()
        with self.assertRaises(RuntimeError):
            execute(op, types.SimpleNamespace())

    def test_functools_wraps_preserved(self):
        def execute(self, context):
            """original docstring"""
            return {'FINISHED'}
        wrapped = fb.guarded(execute)
        self.assertEqual(wrapped.__doc__, 'original docstring')
        self.assertEqual(wrapped.__name__, 'execute')


# ---------------------------------------------------------------------------
# guarded() tests — rig found via monkeypatched workflow
# ---------------------------------------------------------------------------
class GuardedWithRigTests(unittest.TestCase):
    """
    Tests for guarded() when workflow.active_rig successfully returns a rig.

    Monkeypatch technique:
      1. feedback.py is already in sys.modules as 'b4artists_ml.ui_workflow.feedback'
         with __package__ = 'b4artists_ml.ui_workflow'.
      2. Inject a fake 'b4artists_ml.workflow' module into sys.modules.
         Python's relative import resolves `from .. import workflow` by:
           a. stripping the last component of __package__ → 'b4artists_ml'
           b. looking up 'b4artists_ml.workflow' in sys.modules → finds the fake.
      3. The fake active_rig returns self._ctx, which has a b4ml_ui inner holder.
         _holder(ctx) → ctx.b4ml_ui → self._rig, so card writes land on self._rig.
      4. tearDown pops the fake so other test classes are unaffected.
    """

    def setUp(self):
        self._rig = _ns()
        self._ctx = types.SimpleNamespace(b4ml_ui=self._rig)
        fake_wf = types.ModuleType('b4artists_ml.workflow')
        fake_wf.active_rig = lambda ctx: ctx   # ctx IS the rig here
        sys.modules['b4artists_ml.workflow'] = fake_wf

    def tearDown(self):
        sys.modules.pop('b4artists_ml.workflow', None)

    class _Op:
        def __init__(self):
            self.reported = []
        def report(self, cats, msg):
            self.reported.append((cats, msg))

    def test_known_error_writes_card_on_rig(self):
        @fb.guarded
        def execute(self, context):
            # body_preview.py:182
            raise ValueError('Stop playback before posing')
        execute(self._Op(), self._ctx)
        self.assertEqual(self._rig.feedback_level, 'ERROR')

    def test_known_error_uses_failure_text_template(self):
        @fb.guarded
        def execute(self, context):
            # workflow.py:1413
            raise ValueError('Keep or discard the current candidate first')
        execute(self._Op(), self._ctx)
        self.assertEqual(self._rig.feedback_level, 'WARNING')
        self.assertIn('preview', self._rig.feedback_text.lower())

    def test_unknown_error_writes_generic_card(self):
        @fb.guarded
        def execute(self, context):
            raise ValueError('something completely unknown xyz')
        execute(self._Op(), self._ctx)
        self.assertEqual(self._rig.feedback_level, 'ERROR')
        self.assertIn('Something went wrong', self._rig.feedback_text)

    def test_stamp_incremented_after_error(self):
        @fb.guarded
        def execute(self, context):
            raise ValueError('Stop playback before posing')
        before = self._rig.feedback_stamp
        execute(self._Op(), self._ctx)
        self.assertGreater(self._rig.feedback_stamp, before)


# ---------------------------------------------------------------------------
# from_status() tests
# ---------------------------------------------------------------------------
class FromStatusTests(unittest.TestCase):

    def test_kept_prefix_is_success(self):
        h = _ns()
        fb.from_status(h, 'Kept as a separate action')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_candidate_kept_is_success(self):
        # workflow.py:1644: state.status = 'Candidate kept as a separate action'
        h = _ns()
        fb.from_status(h, 'Candidate kept as a separate action')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_original_animation_restored_is_success(self):
        # workflow.py:1644: state.status = 'Original animation restored'
        h = _ns()
        fb.from_status(h, 'Original animation restored')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_restored_prefix_is_success(self):
        h = _ns()
        fb.from_status(h, 'Restored original pose')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_move_pelvis_is_info(self):
        # body_preview.py:229: state.status = 'Move pelvis, chest, neck, head, hand or foot targets...'
        h = _ns()
        fb.from_status(h, 'Move pelvis, chest, neck, head, hand or foot targets')
        self.assertEqual(h.feedback_level, 'INFO')

    def test_unknown_text_is_info(self):
        h = _ns()
        fb.from_status(h, 'Some unrecognised status string')
        self.assertEqual(h.feedback_level, 'INFO')

    def test_text_stored_verbatim(self):
        h = _ns()
        fb.from_status(h, 'Captured key pose at frame 10')
        self.assertEqual(h.feedback_text, 'Captured key pose at frame 10')
        self.assertEqual(h.feedback_level, 'SUCCESS')

    def test_stamp_incremented(self):
        h = _ns()
        fb.from_status(h, 'anything')
        self.assertEqual(h.feedback_stamp, 1)


if __name__ == '__main__':
    unittest.main()
