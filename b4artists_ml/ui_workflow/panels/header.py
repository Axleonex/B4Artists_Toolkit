"""Shared panel prelude for B4Artists ML panels.

Plan §3 opening paragraph; Contract §STATE MAP presentation column,
§BEHAVIORAL SUCCESS items 3, 7, 8.

Import strategy: module-level relative imports (package context) with an
importlib-by-path fallback for tests that load this file directly without the
package registered in sys.modules.  The fallback registers each sibling under
its qualified name (b4artists_ml.ui_workflow.<name>) so subsequent lazy imports
inside the siblings' own guarded functions still resolve correctly.

Verified sibling names (b4artists_ml/ui_workflow/):
  stage.py    — snapshot(), evaluate(), locked(); Snapshot, StageState (stage.py:104-137)
  feedback.py — current(rig) → dict with keys level/text/fix/fix_props/fix_label (feedback.py:225-235)
  copy.py     — STAGES tuple[tuple[str,str]], BUTTONS, BADGES, CARDS, NEXT_PREFIX,
                 fmt(), check() (copy.py:46-163)
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

# ---------------------------------------------------------------------------
# Guarded bpy import
# ---------------------------------------------------------------------------
try:
    import bpy
except ImportError:
    bpy = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Sibling imports — relative inside the package; importlib fallback for tests.
# ---------------------------------------------------------------------------
try:
    from .. import stage
    from .. import feedback
    from .. import copy as copy_
except ImportError:
    _pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _load_sibling(mod_name: str) -> object:
        qualified = 'b4artists_ml.ui_workflow.' + mod_name
        if qualified in sys.modules:
            return sys.modules[qualified]
        path = os.path.join(_pkg_dir, mod_name + '.py')
        spec = importlib.util.spec_from_file_location(qualified, path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules[qualified] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    stage = _load_sibling('stage')      # type: ignore[assignment]
    feedback = _load_sibling('feedback')  # type: ignore[assignment]
    copy_ = _load_sibling('copy')       # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Stage → primary action key (used to compute the LOCKED icon in the strip).
# SETUP has no primary operator key; every other stage maps to its gating key.
# ---------------------------------------------------------------------------
STAGE_PRIMARY_KEY: dict[str, str] = {
    'SETUP':  '',
    'POSE':   'pose.begin',
    'MOTION': 'motion.preview',
    'POLISH': 'polish.contacts',
    'REVIEW': 'review.keep',
}

_LEVEL_ICON: dict[str, str] = {
    'INFO':    'INFO',
    'SUCCESS': 'CHECKMARK',
    'WARNING': 'ERROR',
    'ERROR':   'CANCEL',
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def prelude(layout, context) -> tuple:
    """Draw the shared panel prelude; return (rig, snap, st).

    Drawing order (contract §STATE MAP, §BEHAVIORAL SUCCESS items 3, 7, 8):
      1. Stage strip  — one row of stage labels with status icons.
      2. Feedback card — shown only when the rig has a non-empty feedback text.
      3. Next line    — card guidance text; rendered as an operator if clickable.

    Returns the active rig object (or None), the Snapshot, and the StageState.
    """
    snap = stage.snapshot(context)
    st = stage.evaluate(snap)

    # Lazy rig resolution — workflow.active_rig requires bpy.
    rig = None
    if bpy is not None:
        try:
            from b4artists_ml import workflow as _workflow
            rig = _workflow.active_rig(context)
        except Exception:
            pass

    # ── 1. STAGE STRIP ─────────────────────────────────────────────────────
    # One aligned row; each stage label carries a status icon.
    # Icons: CHECKMARK = completed, RADIOBUT_ON = current,
    #        LOCKED = primary key locked, RADIOBUT_OFF = future.
    row = layout.row(align=True)
    for key, label in copy_.STAGES:
        primary_key = STAGE_PRIMARY_KEY.get(key, '')
        if key in st.completed:
            icon = 'CHECKMARK'
        elif key == st.current:
            icon = 'RADIOBUT_ON'
        elif primary_key and stage.locked(st, primary_key):
            icon = 'LOCKED'
        else:
            icon = 'RADIOBUT_OFF'
        row.label(text=label, icon=icon)

    # ── 2. FEEDBACK CARD ───────────────────────────────────────────────────
    # Shown only when the rig has a b4ml_ui holder with non-empty text.
    # box.alert = True for ERROR level to trigger Bforartists red highlight.
    if rig is not None and getattr(rig, 'b4ml_ui', None) is not None:
        fb = feedback.current(rig)
        if fb['text']:
            box = layout.box()
            box.alert = (fb['level'] == 'ERROR')
            icon = _LEVEL_ICON.get(fb['level'], 'INFO')
            box.label(text=fb['text'], icon=icon)
            if fb['fix']:
                op = box.operator(fb['fix'], text=fb['fix_label'] or 'Fix')
                for k, v in json.loads(fb['fix_props'] or '{}').items():
                    setattr(op, k, v)

    # ── 3. NEXT LINE ───────────────────────────────────────────────────────
    # Label = NEXT_PREFIX + ' ' + card guidance text for the current state.
    # Rendered as an operator button when next_action carries an idname,
    # otherwise as a plain label (e.g. NO_RIG, SOLVE_RUNNING wait states).
    card_text = copy_.CARDS.get(st.state_name, '')
    label = copy_.NEXT_PREFIX + (' ' + card_text if card_text else '')
    _next_label, next_idname, next_props = st.next_action
    if next_idname:
        op = layout.operator(next_idname, text=label)
        for k, v in next_props.items():
            setattr(op, k, v)
    else:
        layout.label(text=label)

    return (rig, snap, st)


def action_row(layout, st, key: str, idname: str, text: str | None = None,
               icon: str = 'NONE', **props):
    """Draw one action button row.

    This is the ONLY function in the panels package that may set .enabled.
    When a key is locked, the row is disabled and the lock reason appears
    beneath as a label — contract §BEHAVIORAL SUCCESS item 7.

    Returns the operator return value from layout.operator().
    """
    reason = stage.locked(st, key)
    row = layout.row()
    row.enabled = not reason
    op = row.operator(idname, text=text or copy_.BUTTONS.get(key, key), icon=icon)
    for k, v in props.items():
        setattr(op, k, v)
    if reason:
        layout.label(text=reason, icon='LOCKED')
    return op


def badge(layout, st, rig) -> None:
    """Draw the state badge for review/motion panels.

    Formats copy_.BADGES[st.state_name] with {name} = the kept or
    preview action name from rig.b4ml, falling back to ''.
    """
    template = copy_.BADGES.get(st.state_name, '')
    if not template:
        return
    name = ''
    if rig is not None:
        b4ml = getattr(rig, 'b4ml', None)
        if b4ml is not None:
            action = (getattr(b4ml, 'kept_action', None)
                      or getattr(b4ml, 'candidate_action', None))
            if action is not None:
                name = getattr(action, 'name', '')
    layout.label(text=copy_.fmt(template, name=name))


def lock_description(st, key: str) -> str:
    """Return the lock reason for *key* in *st*, or '' if available.

    Pure function; wired into operator dynamic description() classmethods
    during Phase 1 cut-over.
    """
    return stage.locked(st, key)
