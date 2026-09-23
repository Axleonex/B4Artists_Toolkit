"""Pure stage engine — no bpy at import time.

Implements UI-EXPERIENCE-CONTRACT-v1.md §STATE MAP, §MAPPING TABLES.

B4ML_PG_settings property names read here (verified ui.py 2026-09-22):
  body_payload:       StringProperty — non-empty while whole-body posing session active
  posing_payload:     StringProperty — non-empty while assisted-posing session active
  quadruped_payload:  StringProperty — non-empty while quadruped-posing session active
  candidate_action:   PointerProperty(Action) — set while a preview candidate exists
  kept_action:        PointerProperty(Action) — set after finish_preview(keep=True)
  anchors:            CollectionProperty — len() is the captured key-pose count
  temporal_running:   BoolProperty — True while temporal/whole-body generate is running
  body_running:       BoolProperty — True while body solve is running
  contact_running:    BoolProperty — True while contact solve is running
  flight_running:     BoolProperty — True while flight solve is running
  secondary_running:  BoolProperty — True while secondary-motion solve is running
  cleanup_running:    BoolProperty — True while cleanup solve is running

Rig mapping fields come from rig_mapping.status(obj) → (RigProfile, rows, error_str).
  profile.family:   'humanoid' | 'quadruped' | 'unknown'
  profile.missing:  tuple of missing required role names; empty = fully mapped

Active-rig resolution delegates to workflow.active_rig(context) (workflow.py:31),
which resolves EMPTY→owner, MESH→find_armature(), and checks view_layer visibility.
"""
from __future__ import annotations

import sys as _sys
import types as _types

# Python 3.12 dataclasses._is_type requires the class module to be in
# sys.modules. Self-register so the module is loadable via
# importlib.util.spec_from_file_location without the caller pre-registering.
if __name__ not in _sys.modules:
    _sys.modules[__name__] = _types.ModuleType(__name__)

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGES: tuple[str, ...] = ('SETUP', 'POSE', 'MOTION', 'POLISH', 'REVIEW')

ACTION_KEYS: tuple[str, ...] = (
    'pose.begin',
    'pose.solve',
    'pose.keep',
    'pose.cancel',
    'motion.preview',
    'review.keep',
    'review.discard',
    'review.restore',
    'polish.contacts',
    'polish.cleanup',
    'polish.flight',
    'polish.secondary',
)

_POLISH_KEYS: tuple[str, ...] = (
    'polish.contacts',
    'polish.cleanup',
    'polish.flight',
    'polish.secondary',
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Snapshot:
    """Plain data snapshot built from bpy context; no bpy types retained."""
    has_rig:       bool
    family:        str          # 'humanoid' | 'quadruped' | 'unknown' | ''
    mapped:        bool
    mapping_error: str
    posing:        str          # '' | 'BODY' | 'ASSISTED' | 'QUADRUPED'
    anchors:       int
    candidate:     bool
    kept:          bool
    running:       str          # '' | 'BODY' | 'TEMPORAL' | 'CONTACT' | 'FLIGHT' | 'SECONDARY' | 'CLEANUP'
    mode:          str          # context.mode e.g. 'OBJECT' | 'POSE'
    playing:       bool


@dataclass(frozen=True)
class StageState:
    """Evaluation result for driving the UI; contains no bpy objects."""
    current:       str                         # one of STAGES
    completed:     frozenset[str]              # stages already passed
    next_action:   tuple[str, str, dict]       # (label, operator idname, props)
    locks:         dict[str, str]              # key → reason; '' = available
    required_mode: str | None                  # 'OBJECT' while posing, else None
    state_name:    str                         # contract STATE MAP name


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate(snapshot: Snapshot) -> StageState:
    """Map a Snapshot to a StageState implementing the contract MAPPING TABLES.

    Precedence: running → posing/mode → candidate → kept → anchors≥2 → mapped → unsupported → no_rig.
    """
    base = _base_evaluate(snapshot)
    if not snapshot.running:
        return base

    # SOLVE_RUNNING: overlay all keys with the wait reason; preserve current.
    reason = "Wait for the current task to finish"
    locks = {k: reason for k in ACTION_KEYS}
    if snapshot.running == 'TEMPORAL':
        na: tuple[str, str, dict] = ('Cancel', 'b4ml.temporal_cancel', {})
    else:
        na = ('Wait', '', {})
    return StageState(
        current=base.current,
        completed=base.completed,
        next_action=na,
        locks=locks,
        required_mode=None,
        state_name='SOLVE_RUNNING',
    )


def locked(state: StageState, key: str) -> str:
    """Return the lock reason for *key*, or '' if the action is available."""
    return state.locks.get(key, '')


def reason_for(snapshot: Snapshot, key: str) -> str:
    """Convenience: evaluate snapshot and return the lock reason for *key*."""
    return locked(evaluate(snapshot), key)


def snapshot(context) -> Snapshot:
    """Build a Snapshot from a live Bforartists context.

    Lazy-imports bpy so the module stays importable in --background tests.
    Rig resolution via workflow.active_rig (workflow.py:31).
    Mapping info via rig_mapping.status (rig_mapping.py:137).
    Never raises: returns a no-rig Snapshot on any exception.
    """
    _default = Snapshot(
        has_rig=False, family='', mapped=False, mapping_error='',
        posing='', anchors=0, candidate=False, kept=False,
        running='', mode='OBJECT', playing=False,
    )
    try:
        import bpy  # noqa: PLC0415 — intentional lazy import
        from b4artists_ml import workflow as _workflow
        from b4artists_ml import rig_mapping as _rig_mapping

        obj = _workflow.active_rig(context)
        if obj is None:
            return _default

        state = obj.b4ml

        # Mapping
        try:
            profile, _rows, correction_error = _rig_mapping.status(obj)
        except Exception:
            profile = None
            correction_error = 'Mapping unavailable'

        if profile is not None:
            family = profile.family
            missing_str = (', '.join(profile.missing[:3]) + (' …' if len(profile.missing) > 3 else '')
                           if profile.missing else '')
            mapping_error = correction_error or (
                f"Missing roles: {missing_str}" if missing_str else ''
            )
            mapped = family in ('humanoid', 'quadruped') and not profile.missing
        else:
            family = 'unknown'
            mapping_error = correction_error
            mapped = False

        # Posing
        if state.body_payload:
            posing = 'BODY'
        elif state.posing_payload:
            posing = 'ASSISTED'
        elif getattr(state, 'quadruped_payload', ''):
            posing = 'QUADRUPED'
        else:
            posing = ''

        # Running
        if state.temporal_running:
            running = 'TEMPORAL'
        elif getattr(state, 'body_running', False):
            running = 'BODY'
        elif state.contact_running:
            running = 'CONTACT'
        elif state.flight_running:
            running = 'FLIGHT'
        elif state.secondary_running:
            running = 'SECONDARY'
        elif state.cleanup_running:
            running = 'CLEANUP'
        else:
            running = ''

        return Snapshot(
            has_rig=True,
            family=family,
            mapped=mapped,
            mapping_error=mapping_error,
            posing=posing,
            anchors=len(state.anchors),
            candidate=bool(state.candidate_action),
            kept=bool(state.kept_action),
            running=running,
            mode=context.mode,
            playing=bool(getattr(getattr(context, 'screen', None), 'is_animation_playing', False)),
        )
    except Exception:
        return _default


# ---------------------------------------------------------------------------
# Internal evaluation
# ---------------------------------------------------------------------------

_NO_RIG            = "Select an armature or bound mesh"
_CHECK_RIG         = "Check Rig first"
_SESSION_BLOCKS    = "Finish or cancel the posing session"
_OBJECT_MODE_REQ   = "Switch to Object Mode to move targets"
_NO_PREVIEW        = "No preview to keep"
_NO_DISCARD        = "No preview to discard"
_NO_RESTORE        = "No kept result to restore"
_KEEP_FIRST        = "Keep the preview first, then restore"
_PREVIEW_BLOCKS    = "Discard or keep the preview first"
_ALREADY_KEPT      = "Already kept — restore or start a new posing session"
_NEED_SECOND_POSE  = "Capture a second key pose to generate motion"
_POLISH_LOCKED     = "Available after a preview or kept result (Advanced)"


def _polish_locks(s: Snapshot) -> dict[str, str]:
    """Return per-feature polish lock reasons.

    Precedence per key: no_rig → not_mapped → posing → no_result → available.
    has_rig / mapped are guaranteed True at all call sites (checked upstream).
    """
    def _reason(key: str) -> str:
        if not s.has_rig:
            return _NO_RIG
        if not s.mapped:
            return _CHECK_RIG
        if s.posing:
            return _SESSION_BLOCKS
        if not (s.candidate or s.kept):
            return _POLISH_LOCKED
        return ''
    return {k: _reason(k) for k in _POLISH_KEYS}


def _completed(s: Snapshot) -> frozenset[str]:
    c = {'SETUP'} if s.mapped else set()
    if s.mapped and (s.anchors >= 2 or s.candidate or s.kept):
        c.add('POSE')
    if s.candidate or s.kept:
        c.add('MOTION')
    return frozenset(c)


def _base_evaluate(s: Snapshot) -> StageState:  # noqa: C901 — intentional flat dispatch
    # ── NO_RIG ─────────────────────────────────────────────────────────────
    if not s.has_rig:
        return StageState(
            current='SETUP',
            completed=frozenset(),
            next_action=('Select a rig', '', {}),
            locks={k: _NO_RIG for k in ACTION_KEYS},
            required_mode=None,
            state_name='NO_RIG',
        )

    # ── UNSUPPORTED_RIG ────────────────────────────────────────────────────
    if not s.mapped:
        return StageState(
            current='SETUP',
            completed=frozenset(),
            next_action=('Check Rig', 'b4ml.action', {'operation': 'INSPECT'}),
            locks={k: _CHECK_RIG for k in ACTION_KEYS},
            required_mode=None,
            state_name='UNSUPPORTED_RIG',
        )

    comp = _completed(s)

    # ── POSING / Pose Mode ─────────────────────────────────────────────────
    if s.posing and s.mode == 'POSE':
        locks: dict[str, str] = {
            'pose.begin':      _SESSION_BLOCKS,
            'pose.solve':      _OBJECT_MODE_REQ,
            'pose.keep':       '',
            'pose.cancel':     '',
            'motion.preview':  _SESSION_BLOCKS,
            'review.keep':     _SESSION_BLOCKS,
            'review.discard':  _SESSION_BLOCKS,
            'review.restore':  _SESSION_BLOCKS,
        }
        locks.update(_polish_locks(s))
        return StageState(
            current='POSE',
            completed=comp,
            next_action=('Switch to Object Mode', 'object.mode_set', {'mode': 'OBJECT'}),
            locks=locks,
            required_mode='OBJECT',
            state_name='POSING_POSE_MODE',
        )

    # ── POSING / Object Mode (or any other mode while body_payload set) ────
    if s.posing:
        locks = {
            'pose.begin':      _SESSION_BLOCKS,
            'pose.solve':      '',
            'pose.keep':       '',
            'pose.cancel':     '',
            'motion.preview':  _SESSION_BLOCKS,
            'review.keep':     _SESSION_BLOCKS,
            'review.discard':  _SESSION_BLOCKS,
            'review.restore':  _SESSION_BLOCKS,
        }
        locks.update(_polish_locks(s))
        return StageState(
            current='POSE',
            completed=comp,
            next_action=('Solve', 'b4ml.body_solve', {}),
            locks=locks,
            required_mode='OBJECT',
            state_name='POSING_OBJECT',
        )

    # ── PREVIEW_ACTIVE ─────────────────────────────────────────────────────
    if s.candidate:
        locks = {
            'pose.begin':      _PREVIEW_BLOCKS,
            'pose.solve':      _PREVIEW_BLOCKS,
            'pose.keep':       '',
            'pose.cancel':     '',
            'motion.preview':  _PREVIEW_BLOCKS,
            'review.keep':     '',
            'review.discard':  '',
            'review.restore':  _KEEP_FIRST,
        }
        locks.update(_polish_locks(s))
        return StageState(
            current='REVIEW',
            completed=comp,
            next_action=('Keep preview', 'b4ml.action', {'operation': 'KEEP'}),
            locks=locks,
            required_mode=None,
            state_name='PREVIEW_ACTIVE',
        )

    # ── KEPT ───────────────────────────────────────────────────────────────
    if s.kept:
        locks = {
            'pose.begin':      '',
            'pose.solve':      '',
            'pose.keep':       _ALREADY_KEPT,
            'pose.cancel':     '',
            'motion.preview':  '',
            'review.keep':     _ALREADY_KEPT,
            'review.discard':  _ALREADY_KEPT,
            'review.restore':  '',
        }
        locks.update(_polish_locks(s))
        return StageState(
            current='REVIEW',
            completed=comp,
            next_action=('Restore original', 'b4ml.action', {'operation': 'RESTORE_SOURCE'}),
            locks=locks,
            required_mode=None,
            state_name='KEPT',
        )

    # ── ANCHORS_CAPTURED (≥2, no posing/candidate/kept) ───────────────────
    if s.anchors >= 2:
        locks = {
            'pose.begin':      '',
            'pose.solve':      '',
            'pose.keep':       '',
            'pose.cancel':     '',
            'motion.preview':  '',
            'review.keep':     _NO_PREVIEW,
            'review.discard':  _NO_DISCARD,
            'review.restore':  _NO_RESTORE,
        }
        locks.update(_polish_locks(s))
        return StageState(
            current='MOTION',
            completed=comp,
            next_action=('Generate preview', 'b4ml.action', {'operation': 'PREVIEW'}),
            locks=locks,
            required_mode=None,
            state_name='ANCHORS_CAPTURED',
        )

    # ── MAPPED (anchors < 2, nothing active) ──────────────────────────────
    locks = {
        'pose.begin':      '',
        'pose.solve':      '',
        'pose.keep':       '',
        'pose.cancel':     '',
        'motion.preview':  _NEED_SECOND_POSE,
        'review.keep':     _NO_PREVIEW,
        'review.discard':  _NO_DISCARD,
        'review.restore':  _NO_RESTORE,
    }
    locks.update(_polish_locks(s))
    return StageState(
        current='POSE',
        completed=comp,
        next_action=('Start posing', 'b4ml.body', {'operation': 'BEGIN'}),
        locks=locks,
        required_mode=None,
        state_name='MAPPED',
    )
