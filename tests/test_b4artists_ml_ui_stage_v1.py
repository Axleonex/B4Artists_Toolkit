"""Host-independent tests for b4artists_ml/ui_workflow/stage.py.

Tests the evaluate() matrix and locked() helper against every state
named in UI-EXPERIENCE-CONTRACT-v1.md § STATE MAP.

No Blender module dependency — runs under plain pytest.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

# ---------------------------------------------------------------------------
# Load stage.py without the Blender module in the environment
# ---------------------------------------------------------------------------

_STAGE_PATH = pathlib.Path(__file__).parent.parent / "b4artists_ml" / "ui_workflow" / "stage.py"


def _load_stage():
    spec = importlib.util.spec_from_file_location("b4artists_ml.ui_workflow.stage", _STAGE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


stage = _load_stage()
Snapshot = stage.Snapshot
evaluate = stage.evaluate
locked = stage.locked
ACTION_KEYS = stage.ACTION_KEYS


# ---------------------------------------------------------------------------
# Snapshot factories — one per STATE MAP state
# ---------------------------------------------------------------------------

def _snap(**kw) -> Snapshot:
    """Base snapshot: mapped humanoid rig, nothing active."""
    base = dict(
        has_rig=True, family="humanoid", mapped=True, mapping_error="",
        posing="", anchors=0, candidate=False, kept=False,
        running="", mode="OBJECT", playing=False,
    )
    base.update(kw)
    return Snapshot(**base)


def snap_no_rig() -> Snapshot:
    return _snap(has_rig=False, family="", mapped=False)


def snap_unsupported() -> Snapshot:
    return _snap(mapped=False, mapping_error="Missing roles: spine")


def snap_mapped() -> Snapshot:
    return _snap()


def snap_posing_object() -> Snapshot:
    return _snap(posing="BODY", mode="OBJECT")


def snap_posing_pose_mode() -> Snapshot:
    return _snap(posing="BODY", mode="POSE")


def snap_anchors_captured() -> Snapshot:
    return _snap(anchors=2)


def snap_preview_active() -> Snapshot:
    return _snap(anchors=2, candidate=True)


def snap_kept() -> Snapshot:
    return _snap(anchors=2, kept=True)


def snap_solve_running_temporal() -> Snapshot:
    return _snap(anchors=2, running="TEMPORAL")


def snap_solve_running_body() -> Snapshot:
    return _snap(posing="BODY", running="BODY", mode="OBJECT")


def snap_solve_running_contact() -> Snapshot:
    return _snap(anchors=2, kept=True, running="CONTACT")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_locked(state) -> list[str]:
    """Return keys that are locked (reason != '')."""
    return [k for k in ACTION_KEYS if locked(state, k)]


def _all_available(state) -> list[str]:
    """Return keys that are available (reason == '')."""
    return [k for k in ACTION_KEYS if not locked(state, k)]


# ---------------------------------------------------------------------------
# NO_RIG
# ---------------------------------------------------------------------------

class TestNoRig:
    def setup_method(self):
        self.state = evaluate(snap_no_rig())

    def test_state_name(self):
        assert self.state.state_name == "NO_RIG"

    def test_current_stage(self):
        assert self.state.current == "SETUP"

    def test_all_locked(self):
        assert set(_all_locked(self.state)) == set(ACTION_KEYS)

    def test_no_action_operator(self):
        _, idname, _ = self.state.next_action
        assert idname == ""

    def test_completed_empty(self):
        assert self.state.completed == frozenset()


# ---------------------------------------------------------------------------
# UNSUPPORTED_RIG
# ---------------------------------------------------------------------------

class TestUnsupportedRig:
    def setup_method(self):
        self.state = evaluate(snap_unsupported())

    def test_state_name(self):
        assert self.state.state_name == "UNSUPPORTED_RIG"

    def test_current_stage(self):
        assert self.state.current == "SETUP"

    def test_all_locked(self):
        assert set(_all_locked(self.state)) == set(ACTION_KEYS)

    def test_next_action_operator(self):
        _, idname, props = self.state.next_action
        assert idname == "b4ml.action"
        assert props.get("operation") == "INSPECT"


# ---------------------------------------------------------------------------
# MAPPED (anchors < 2, nothing active)
# ---------------------------------------------------------------------------

class TestMapped:
    def setup_method(self):
        self.state = evaluate(snap_mapped())

    def test_state_name(self):
        assert self.state.state_name == "MAPPED"

    def test_current_stage(self):
        assert self.state.current == "POSE"

    def test_pose_begin_available(self):
        assert locked(self.state, "pose.begin") == ""

    def test_motion_preview_locked(self):
        assert locked(self.state, "motion.preview") != ""

    def test_review_keys_locked(self):
        for k in ("review.keep", "review.discard", "review.restore"):
            assert locked(self.state, k) != "", f"{k} should be locked"

    def test_polish_keys_locked(self):
        for k in ("polish.contacts", "polish.cleanup", "polish.flight", "polish.secondary"):
            assert locked(self.state, k) != "", f"{k} should be locked"

    def test_next_action_operator(self):
        _, idname, props = self.state.next_action
        assert idname == "b4ml.body"
        assert props.get("operation") == "BEGIN"

    def test_completed_has_setup(self):
        assert "SETUP" in self.state.completed


# ---------------------------------------------------------------------------
# POSING_OBJECT
# ---------------------------------------------------------------------------

class TestPosingObject:
    def setup_method(self):
        self.state = evaluate(snap_posing_object())

    def test_state_name(self):
        assert self.state.state_name == "POSING_OBJECT"

    def test_current_stage(self):
        assert self.state.current == "POSE"

    def test_pose_solve_available(self):
        assert locked(self.state, "pose.solve") == ""

    def test_pose_keep_available(self):
        assert locked(self.state, "pose.keep") == ""

    def test_pose_cancel_available(self):
        assert locked(self.state, "pose.cancel") == ""

    def test_pose_begin_locked(self):
        assert locked(self.state, "pose.begin") != ""

    def test_motion_preview_locked(self):
        assert locked(self.state, "motion.preview") != ""

    def test_review_keys_locked(self):
        for k in ("review.keep", "review.discard", "review.restore"):
            assert locked(self.state, k) != "", f"{k} should be locked"

    def test_next_action_operator(self):
        _, idname, _ = self.state.next_action
        assert idname == "b4ml.body_solve"

    def test_required_mode(self):
        assert self.state.required_mode == "OBJECT"


# ---------------------------------------------------------------------------
# POSING_POSE_MODE
# ---------------------------------------------------------------------------

class TestPosingPoseMode:
    def setup_method(self):
        self.state = evaluate(snap_posing_pose_mode())

    def test_state_name(self):
        assert self.state.state_name == "POSING_POSE_MODE"

    def test_current_stage(self):
        assert self.state.current == "POSE"

    def test_required_mode(self):
        assert self.state.required_mode == "OBJECT"

    def test_pose_solve_locked_object_mode_message(self):
        reason = locked(self.state, "pose.solve")
        assert reason == "Switch to Object Mode to move targets"

    def test_pose_keep_available(self):
        assert locked(self.state, "pose.keep") == ""

    def test_pose_cancel_available(self):
        assert locked(self.state, "pose.cancel") == ""

    def test_pose_begin_locked(self):
        assert locked(self.state, "pose.begin") != ""

    def test_motion_preview_locked(self):
        assert locked(self.state, "motion.preview") != ""

    def test_review_keys_locked(self):
        for k in ("review.keep", "review.discard", "review.restore"):
            assert locked(self.state, k) != "", f"{k} should be locked"

    def test_next_action_switches_mode(self):
        _, idname, props = self.state.next_action
        assert idname == "object.mode_set"
        assert props.get("mode") == "OBJECT"

    def test_verification_fixture(self):
        """Exact match of the verification run output."""
        assert self.state.state_name == "POSING_POSE_MODE"
        assert self.state.current == "POSE"
        assert self.state.required_mode == "OBJECT"
        assert self.state.locks["pose.solve"] == "Switch to Object Mode to move targets"


# ---------------------------------------------------------------------------
# ANCHORS_CAPTURED
# ---------------------------------------------------------------------------

class TestAnchorsCaptured:
    def setup_method(self):
        self.state = evaluate(snap_anchors_captured())

    def test_state_name(self):
        assert self.state.state_name == "ANCHORS_CAPTURED"

    def test_current_stage(self):
        assert self.state.current == "MOTION"

    def test_motion_preview_available(self):
        assert locked(self.state, "motion.preview") == ""

    def test_pose_begin_available(self):
        assert locked(self.state, "pose.begin") == ""

    def test_review_keep_locked(self):
        assert locked(self.state, "review.keep") != ""

    def test_review_discard_locked(self):
        assert locked(self.state, "review.discard") != ""

    def test_review_restore_locked(self):
        assert locked(self.state, "review.restore") != ""

    def test_polish_keys_locked(self):
        for k in ("polish.contacts", "polish.cleanup", "polish.flight", "polish.secondary"):
            assert locked(self.state, k) != "", f"{k} should be locked (no preview/kept)"

    def test_next_action_operator(self):
        _, idname, props = self.state.next_action
        assert idname == "b4ml.action"
        assert props.get("operation") == "PREVIEW"

    def test_completed_has_setup_and_pose(self):
        assert "SETUP" in self.state.completed
        assert "POSE" in self.state.completed


# ---------------------------------------------------------------------------
# PREVIEW_ACTIVE
# ---------------------------------------------------------------------------

class TestPreviewActive:
    def setup_method(self):
        self.state = evaluate(snap_preview_active())

    def test_state_name(self):
        assert self.state.state_name == "PREVIEW_ACTIVE"

    def test_current_stage(self):
        assert self.state.current == "REVIEW"

    def test_review_keep_available(self):
        assert locked(self.state, "review.keep") == ""

    def test_review_discard_available(self):
        assert locked(self.state, "review.discard") == ""

    def test_review_restore_locked(self):
        # Must keep first before restore
        assert locked(self.state, "review.restore") != ""

    def test_pose_keep_available(self):
        assert locked(self.state, "pose.keep") == ""

    def test_pose_cancel_available(self):
        assert locked(self.state, "pose.cancel") == ""

    def test_pose_begin_locked(self):
        assert locked(self.state, "pose.begin") != ""

    def test_polish_keys_available(self):
        for k in ("polish.contacts", "polish.cleanup", "polish.flight", "polish.secondary"):
            assert locked(self.state, k) == "", f"{k} should be available with candidate"

    def test_next_action_operator(self):
        _, idname, props = self.state.next_action
        assert idname == "b4ml.action"
        assert props.get("operation") == "KEEP"

    def test_completed_includes_motion(self):
        assert "MOTION" in self.state.completed


# ---------------------------------------------------------------------------
# KEPT
# ---------------------------------------------------------------------------

class TestKept:
    def setup_method(self):
        self.state = evaluate(snap_kept())

    def test_state_name(self):
        assert self.state.state_name == "KEPT"

    def test_current_stage(self):
        assert self.state.current == "REVIEW"

    def test_review_restore_available(self):
        assert locked(self.state, "review.restore") == ""

    def test_review_keep_locked(self):
        assert locked(self.state, "review.keep") != ""

    def test_review_discard_locked(self):
        assert locked(self.state, "review.discard") != ""

    def test_pose_keep_locked(self):
        assert locked(self.state, "pose.keep") != ""

    def test_pose_begin_available(self):
        assert locked(self.state, "pose.begin") == ""

    def test_motion_preview_available(self):
        assert locked(self.state, "motion.preview") == ""

    def test_polish_keys_available(self):
        for k in ("polish.contacts", "polish.cleanup", "polish.flight", "polish.secondary"):
            assert locked(self.state, k) == "", f"{k} should be available with kept result"

    def test_next_action_operator(self):
        _, idname, props = self.state.next_action
        assert idname == "b4ml.action"
        assert props.get("operation") == "RESTORE_SOURCE"

    def test_completed_includes_motion(self):
        assert "MOTION" in self.state.completed


# ---------------------------------------------------------------------------
# SOLVE_RUNNING overlay
# ---------------------------------------------------------------------------

class TestSolveRunning:
    def test_temporal_cancel_offered(self):
        state = evaluate(snap_solve_running_temporal())
        assert state.state_name == "SOLVE_RUNNING"
        _, idname, _ = state.next_action
        assert idname == "b4ml.temporal_cancel"

    def test_body_running_wait(self):
        state = evaluate(snap_solve_running_body())
        assert state.state_name == "SOLVE_RUNNING"
        _, idname, _ = state.next_action
        assert idname == ""

    def test_contact_running_all_locked(self):
        state = evaluate(snap_solve_running_contact())
        assert state.state_name == "SOLVE_RUNNING"
        assert set(_all_locked(state)) == set(ACTION_KEYS)

    def test_running_preserves_base_current(self):
        # base state is KEPT (current=REVIEW) — overlay must not change current
        state = evaluate(snap_solve_running_contact())
        base = evaluate(snap_kept())
        assert state.current == base.current

    def test_required_mode_none_during_running(self):
        state = evaluate(snap_solve_running_temporal())
        assert state.required_mode is None


# ---------------------------------------------------------------------------
# Cross-cutting invariants
# ---------------------------------------------------------------------------

_ALL_SNAPS = [
    snap_no_rig(), snap_unsupported(), snap_mapped(),
    snap_posing_object(), snap_posing_pose_mode(), snap_anchors_captured(),
    snap_preview_active(), snap_kept(),
    snap_solve_running_temporal(), snap_solve_running_body(),
    snap_solve_running_contact(),
]


class TestInvariants:
    @pytest.mark.parametrize("snap", _ALL_SNAPS)
    def test_current_is_valid_stage(self, snap):
        state = evaluate(snap)
        assert state.current in stage.STAGES

    @pytest.mark.parametrize("snap", _ALL_SNAPS)
    def test_all_action_keys_present_in_locks(self, snap):
        state = evaluate(snap)
        for k in ACTION_KEYS:
            assert k in state.locks, f"Key {k!r} missing from locks"

    @pytest.mark.parametrize("snap", _ALL_SNAPS)
    def test_lock_values_are_strings(self, snap):
        state = evaluate(snap)
        for k, v in state.locks.items():
            assert isinstance(v, str), f"locks[{k!r}] is not a str"

    @pytest.mark.parametrize("snap", _ALL_SNAPS)
    def test_next_action_is_triple(self, snap):
        state = evaluate(snap)
        label, idname, props = state.next_action
        assert isinstance(label, str)
        assert isinstance(idname, str)
        assert isinstance(props, dict)

    @pytest.mark.parametrize("snap", _ALL_SNAPS)
    def test_completed_is_frozenset_of_stages(self, snap):
        state = evaluate(snap)
        assert isinstance(state.completed, frozenset)
        assert state.completed.issubset(set(stage.STAGES))


# ---------------------------------------------------------------------------
# reason_for convenience wrapper
# ---------------------------------------------------------------------------

class TestReasonFor:
    def test_locked_key_returns_reason(self):
        reason = stage.reason_for(snap_no_rig(), "pose.begin")
        assert reason != ""

    def test_available_key_returns_empty(self):
        reason = stage.reason_for(snap_kept(), "review.restore")
        assert reason == ""


# ---------------------------------------------------------------------------
# Polish key lock reasons (polishtest-1)
# ---------------------------------------------------------------------------

_TEST_POLISH_KEYS = (
    'polish.contacts', 'polish.cleanup', 'polish.flight', 'polish.secondary',
)

_SESSION_BLOCKING_REASON = "Finish or cancel the posing session"


class TestPolishLocks:
    """Lock reason is non-empty in every blocked situation; empty with preview or kept."""

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_no_rig_locked_with_specific_reason(self, key):
        assert locked(evaluate(snap_no_rig()), key) == "Select an armature or bound mesh"

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_rig_not_mapped_locked_with_specific_reason(self, key):
        assert locked(evaluate(snap_unsupported()), key) == "Check Rig first"

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_mapped_no_result_locked(self, key):
        assert locked(evaluate(snap_mapped()), key) != ""

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_anchors_no_result_locked(self, key):
        assert locked(evaluate(snap_anchors_captured()), key) != ""

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_posing_active_locked_with_specific_reason(self, key):
        assert locked(evaluate(snap_posing_object()), key) == _SESSION_BLOCKING_REASON

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_solve_running_locked(self, key):
        assert locked(evaluate(snap_solve_running_contact()), key) != ""

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_preview_active_available(self, key):
        assert locked(evaluate(snap_preview_active()), key) == ""

    @pytest.mark.parametrize("key", _TEST_POLISH_KEYS)
    def test_kept_available(self, key):
        assert locked(evaluate(snap_kept()), key) == ""


# ---------------------------------------------------------------------------
# Quadruped posing path (polishtest-1)
# ---------------------------------------------------------------------------

def _snap_quadruped_posing() -> Snapshot:
    return _snap(posing='QUADRUPED', mode='OBJECT', family='quadruped')


class TestQuadrupedPosing:
    """posing='QUADRUPED' must produce the same session-blocking locks as posing='BODY'."""

    def setup_method(self):
        self.quad_state = evaluate(_snap_quadruped_posing())
        self.body_state = evaluate(snap_posing_object())

    def test_current_is_pose(self):
        assert self.quad_state.current == 'POSE'

    def test_required_mode_is_object(self):
        assert self.quad_state.required_mode == 'OBJECT'

    def test_required_mode_matches_humanoid(self):
        assert self.quad_state.required_mode == self.body_state.required_mode

    def test_motion_preview_locked(self):
        assert locked(self.quad_state, 'motion.preview') != ""

    def test_motion_preview_lock_matches_humanoid(self):
        assert (locked(self.quad_state, 'motion.preview')
                == locked(self.body_state, 'motion.preview'))

    def test_review_keys_locked_match_humanoid(self):
        for k in ('review.keep', 'review.discard', 'review.restore'):
            assert locked(self.quad_state, k) == locked(self.body_state, k), \
                f"quadruped {k!r} lock reason differs from humanoid BODY"


# ---------------------------------------------------------------------------
# ACTION_KEYS covers every key any panel calls action_row with
# ---------------------------------------------------------------------------

class TestActionKeysCompleteness:
    def test_panel_keys_all_in_action_keys(self):
        import re
        import pathlib as _pl
        panels_dir = (
            _pl.Path(__file__).parent.parent
            / "b4artists_ml" / "ui_workflow" / "panels"
        )
        panel_keys: set[str] = set()
        _pat = re.compile(r",\s*st,\s*['\"]([^'\"]+)['\"]")
        for py_file in panels_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            for m in _pat.finditer(source):
                panel_keys.add(m.group(1))
        unknown = panel_keys - set(ACTION_KEYS)
        assert not unknown, f"Keys used in panels but absent from ACTION_KEYS: {unknown}"
