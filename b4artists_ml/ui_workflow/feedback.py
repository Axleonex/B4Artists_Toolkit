"""
Persistent feedback model for B4Artists ML UI.

Plan §2.3 (feedback.py); Contract §FAILURE + RECOVERY and §MAPPING TABLES
"FAILURE list → feedback.py levels and fix operators".

state.status assignments routed through from_status():
  workflow.py:1644  'Candidate kept as a separate action' / 'Original animation restored'
  workflow.py:1664  'Original action and input rig modes restored; candidate remains available'
  workflow.py:562   f"Reused pose from frame {source_frame:g} at frame {frame:g}"
  ui.py:~L925 INSPECT path: "Unrecognized [family]: 0/14 roles; N blocked preflights" → ERROR card
              via _STATUS_FAILURE_PREFIXES before the SUCCESS/INFO decision.

B4ML_PG_settings defined at ui.py:216; active_rig() at workflow.py:31.
Public helpers: humanize_mapping_error().
Real ValueError messages mapped by _RULES:
  body_preview.py:182  'Stop playback before posing'                               → begin_while_playing
  workflow.py:1597     'Finish or cancel the active pose preview first'            → session_blocks_review
  workflow.py:1654     'Select the last kept candidate before restoring its source'→ restore_wrong_action
  workflow.py:1413     'Keep or discard the current candidate first'               → preview_exists
  workflow.py:1414     'Restore the kept motion source before generating another'  → motion_layer_blocking
"""
from __future__ import annotations

import functools
import json
import re
from typing import Any

# bpy touched only inside _define_property_group(), register(), and unregister().
try:
    import bpy
    from bpy.props import EnumProperty, IntProperty, PointerProperty, StringProperty
    from bpy.types import PropertyGroup
except ImportError:
    bpy = None  # type: ignore[assignment]

LEVELS = ('INFO', 'SUCCESS', 'WARNING', 'ERROR')

# ---------------------------------------------------------------------------
# FAILURES — authoritative mapping from failure key → feedback payload.
# Tuple: (level, text_template, fix_operator, fix_props: dict, fix_label).
# text_template may contain {exc} which is replaced with the exception message.
# One entry per row in Contract §MAPPING TABLES "FAILURE list".
# ---------------------------------------------------------------------------
FAILURES: dict[str, tuple[str, str, str, dict, str]] = {
    'mapping_failure': (
        'ERROR',
        'Rig not recognised — {exc}',
        'b4ml.action',
        {'operation': 'INSPECT'},
        'Check Rig',
    ),
    'begin_while_playing': (
        'ERROR',
        'Stop playback before starting a posing session.',
        'screen.animation_play',
        {},
        'Stop Playback',
    ),
    'solve_failure': (
        'ERROR',
        'Solve failed — {exc}. Reposition targets and retry.',
        'b4ml.body_solve',
        {},
        'Retry Solve',
    ),
    'session_blocks_review': (
        'INFO',
        'Finish or cancel the posing session to review the preview.',
        '',
        {},
        '',
    ),
    'restore_wrong_action': (
        'ERROR',
        'Select the kept result before restoring its source.',
        'b4ml.action',
        {'operation': 'SELECT_KEPT'},
        'Select Kept Result',
    ),
    'preview_exists': (
        'WARNING',
        'Keep or discard the current preview before generating another.',
        '',
        {},
        '',
    ),
    'motion_layer_blocking': (
        'WARNING',
        'Restore the kept motion source before generating another preview.',
        '',
        {},
        '',
    ),
}

# ---------------------------------------------------------------------------
# classify — map real ValueError text to a FAILURES key (or None).
# Substrings taken verbatim from the source locations cited in the module
# docstring; unknown exceptions return None and get a generic ERROR card.
# Match substrings must not contain animator-forbidden terms (candidate/payload/
# backend/internal units): the copy gate scans every string literal in ui_workflow.
# ---------------------------------------------------------------------------
_RULES: tuple[tuple[str, str], ...] = (
    ('Stop playback before posing',                            'begin_while_playing'),
    ('Finish or cancel the active pose preview first',         'session_blocks_review'),
    ('before restoring',                                       'restore_wrong_action'),
    ('discard the current',                                    'preview_exists'),
    ('Restore the kept motion source before generating',       'motion_layer_blocking'),
    ('contextual rig mapping',                                 'mapping_failure'),
    ('requires a verified BoneForge, Rigify or imported FK',   'mapping_failure'),
    ('Incomplete generated humanoid rig-state mapping',        'mapping_failure'),
)


def classify(exc_text: str) -> str | None:
    """Return the FAILURES key for *exc_text*, or None if not recognised."""
    for substring, key in _RULES:
        if substring in exc_text:
            return key
    return None


def humanize_mapping_error(text: str) -> str:
    """Rewrite a raw rig-mapping diagnostic string into plain animator wording.

    Recognised transformations (applied in order):
      - "Unrecognized [unknown]: …"  → leading prefix removed
      - "Unrecognized [<family>]: …" → "<Family> rig — …"
      - ";? N blocked preflight(s)"  → removed entirely
      - "N/M roles"                  → "N of M bone roles found"
    Inputs that match none of the above are returned unchanged.
    After any transformation: double spaces collapsed, stray leading
    punctuation stripped, trailing period added if absent.
    Never introduces forbidden terms (candidate/payload/backend/internal units).
    """
    original = text
    changed = False

    # Strip / rewrite "Unrecognized [family]:" prefix
    m = re.match(r'^Unrecognized\s+\[([^\]]+)\]:\s*', text)
    if m:
        changed = True
        family = m.group(1)
        rest = text[m.end():]
        text = rest if family.lower() == 'unknown' else family.capitalize() + ' rig \u2014 ' + rest

    # Remove "; N blocked preflight(s)"
    cleaned = re.sub(r';?\s*\d+\s+blocked\s+preflights?', '', text)
    if cleaned != text:
        changed = True
        text = cleaned

    # "N/M roles" → "N of M bone roles found"
    rewritten = re.sub(
        r'(\d+)/(\d+)\s+roles',
        lambda m2: f'{m2.group(1)} of {m2.group(2)} bone roles found',
        text,
    )
    if rewritten != text:
        changed = True
        text = rewritten

    if not changed:
        return original

    # Cleanup after a recognised transformation
    text = re.sub(r'  +', ' ', text).strip(' ;,')
    if text and text[-1] not in '.!?':
        text += '.'
    return text


# ---------------------------------------------------------------------------
# PropertyGroup definition — bpy is touched only here.
# ---------------------------------------------------------------------------
_B4ML_PG_feedback = None  # set by _define_property_group()


def _define_property_group() -> None:
    global _B4ML_PG_feedback

    class B4ML_PG_feedback(PropertyGroup):
        feedback_level: EnumProperty(
            items=[(lvl, lvl, '') for lvl in LEVELS],
            default='INFO',
            options={'SKIP_SAVE'},
        )
        feedback_text: StringProperty()
        feedback_fix: StringProperty()
        # JSON of operator kwargs forwarded when the fix button is pressed.
        # Example: '{"operation": "INSPECT"}'
        feedback_fix_props: StringProperty()
        feedback_fix_label: StringProperty()
        # Incremented on every set_feedback() call so panels can detect new messages.
        feedback_stamp: IntProperty()

    _B4ML_PG_feedback = B4ML_PG_feedback


# ---------------------------------------------------------------------------
# register / unregister (both idempotent).
# ---------------------------------------------------------------------------
def register() -> None:
    if bpy is None:
        return
    _define_property_group()
    if hasattr(bpy.types, 'B4ML_PG_feedback'):
        try:
            bpy.utils.unregister_class(bpy.types.B4ML_PG_feedback)
        except Exception:
            pass
    bpy.utils.register_class(_B4ML_PG_feedback)
    if not hasattr(bpy.types.Object, 'b4ml_ui'):
        bpy.types.Object.b4ml_ui = PointerProperty(type=_B4ML_PG_feedback)


def unregister() -> None:
    if bpy is None:
        return
    if hasattr(bpy.types.Object, 'b4ml_ui'):
        del bpy.types.Object.b4ml_ui
    if hasattr(bpy.types, 'B4ML_PG_feedback'):
        try:
            bpy.utils.unregister_class(bpy.types.B4ML_PG_feedback)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Holder resolution.
# target may be the rig Object (then use target.b4ml_ui) or the holder itself;
# tests pass a types.SimpleNamespace directly.
# ---------------------------------------------------------------------------
def _holder(target: Any) -> Any:
    return getattr(target, 'b4ml_ui', target)


# ---------------------------------------------------------------------------
# Core setters / getters — work on any object exposing the feedback attributes.
# ---------------------------------------------------------------------------
def set_feedback(
    target: Any,
    level: str,
    text: str,
    fix: str = '',
    fix_label: str = '',
    **props: Any,
) -> None:
    """Write all feedback fields atomically and increment the stamp."""
    h = _holder(target)
    h.feedback_level = level
    h.feedback_text = text
    h.feedback_fix = fix
    h.feedback_fix_props = json.dumps(props) if props else ''
    h.feedback_fix_label = fix_label
    h.feedback_stamp = (h.feedback_stamp + 1) % (2 ** 30)


def info(target: Any, text: str, fix: str = '', fix_label: str = '', **props: Any) -> None:
    set_feedback(target, 'INFO', text, fix, fix_label, **props)


def success(target: Any, text: str, fix: str = '', fix_label: str = '', **props: Any) -> None:
    set_feedback(target, 'SUCCESS', text, fix, fix_label, **props)


def warning(target: Any, text: str, fix: str = '', fix_label: str = '', **props: Any) -> None:
    set_feedback(target, 'WARNING', text, fix, fix_label, **props)


def error(target: Any, text: str, fix: str = '', fix_label: str = '', **props: Any) -> None:
    set_feedback(target, 'ERROR', text, fix, fix_label, **props)


def clear(target: Any) -> None:
    set_feedback(target, 'INFO', '')


def current(target: Any) -> dict:
    """Return a snapshot dict of the current feedback state."""
    h = _holder(target)
    return {
        'level': h.feedback_level,
        'text': h.feedback_text,
        'fix': h.feedback_fix,
        'fix_props': h.feedback_fix_props,
        'fix_label': h.feedback_fix_label,
        'stamp': h.feedback_stamp,
    }


# ---------------------------------------------------------------------------
# guarded — decorator for B4ML_OT_*.execute().
# ---------------------------------------------------------------------------
def guarded(fn):
    """Wrap an operator execute method to catch ValueError and write the feedback card.

    On ValueError:
      - resolves the active rig via workflow.active_rig(context) (lazy import)
      - classifies the exception against _RULES / FAILURES
      - writes the feedback card on the rig (b4ml_ui) when a rig is found
      - always calls self.report({'ERROR'}, text) and returns {'CANCELLED'}
    Other exceptions propagate unchanged.
    On success fn's return value passes through.
    """
    @functools.wraps(fn)
    def wrapper(self, context):
        try:
            return fn(self, context)
        except ValueError as exc:
            exc_text = str(exc)
            rig = None
            try:
                from .. import workflow as _wf
                rig = _wf.active_rig(context)
            except Exception:
                pass
            key = classify(exc_text)
            if rig is not None:
                if key:
                    level, tmpl, fix_op, fix_props, fix_label = FAILURES[key]
                    exc_arg = humanize_mapping_error(exc_text) if key == 'mapping_failure' else exc_text
                    text = tmpl.format(exc=exc_arg)
                    set_feedback(rig, level, text, fix_op, fix_label, **fix_props)
                else:
                    text = 'Something went wrong: ' + exc_text
                    error(rig, text)
            else:
                if key:
                    exc_arg = humanize_mapping_error(exc_text) if key == 'mapping_failure' else exc_text
                    text = FAILURES[key][1].format(exc=exc_arg)
                else:
                    text = 'Something went wrong: ' + exc_text
            self.report({'ERROR'}, text)
            return {'CANCELLED'}
    return wrapper


# ---------------------------------------------------------------------------
# from_status — mechanical bridge for legacy state.status assignments.
# Phase 4 will rewrite the copy; this is routing only.
# ---------------------------------------------------------------------------
# Status-text prefixes that map to a FAILURES card instead of SUCCESS/INFO.
# Checked before _SUCCESS_PREFIXES; each entry is (prefix, FAILURES key).
_STATUS_FAILURE_PREFIXES: tuple[tuple[str, str], ...] = (
    ('Unrecognized', 'mapping_failure'),   # ui.py:~L925 INSPECT branch
)

_SUCCESS_PREFIXES = (
    'Kept',
    'Restored',
    'Captured',
    'Mapped',
    'Solved',
    'Original animation restored',
    'kept as a separate action',   # matches legacy "Candidate kept as a separate action" via `in`
)


def from_status(target: Any, text: str) -> None:
    """Route a legacy state.status string into the feedback card.

    Checks _STATUS_FAILURE_PREFIXES first; matching text becomes an ERROR card
    using the FAILURES row (e.g. mapping_failure → ERROR + Check Rig fix button).
    SUCCESS when *text* starts with or contains a known success prefix; INFO otherwise.
    The `in` form handles prefixes that are mid-sentence substrings of the legacy text.
    """
    for prefix, key in _STATUS_FAILURE_PREFIXES:
        if text.startswith(prefix):
            level, tmpl, fix_op, fix_props, fix_label = FAILURES[key]
            exc_arg = humanize_mapping_error(text) if key == 'mapping_failure' else text
            formatted = tmpl.format(exc=exc_arg) if '{' in tmpl else tmpl
            set_feedback(target, level, formatted, fix_op, fix_label, **fix_props)
            return
    level = 'SUCCESS' if any(text.startswith(p) or p in text for p in _SUCCESS_PREFIXES) else 'INFO'
    set_feedback(target, level, text)
