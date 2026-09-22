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

_CHAR_PX = 9.0  # Blender UI font at default ui_scale; 7.0 over-estimated and clipped (QA 2026-09-22)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def wrap_label(layout, text: str, icon: str = 'NONE',
               width_px: int | None = None) -> None:
    """Word-wrap *text* into successive label rows at sidebar width.

    chars per line = max(18, int(((width_px or 220) - 16) / _CHAR_PX))
    Subtracts 16 px gutter for icon column and panel padding before dividing.
    Icon on first row; BLANK1 on subsequent rows to preserve alignment.
    """
    cpl = max(18, int(((width_px or 220) - 16) / _CHAR_PX))
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        wlen = len(word)
        if length and length + 1 + wlen > cpl:
            lines.append(' '.join(current))
            current = [word]
            length = wlen
        else:
            current.append(word)
            length = (length + 1 + wlen) if length else wlen
    if current:
        lines.append(' '.join(current))
    for i, line in enumerate(lines or ['']):
        layout.label(text=line, icon=icon if i == 0 else 'BLANK1')


def prelude(layout, context, full: bool = False) -> tuple:
    """Draw the shared panel prelude; return (rig, snap, st).

    full=False (default): compact — icon strip + stage line, WARNING/ERROR
    feedback card only, Next button without card sentence.
    full=True: complete — same strip, all feedback levels (wrapped), card
    sentence (wrapped) then Next button.  Pass full=True from setup.py.

    Drawing order (contract §STATE MAP, §BEHAVIORAL SUCCESS items 3, 7, 8):
      1. Stage strip  — icon-only row + 'Stage N of 5 — Label' text line.
      2. Feedback card — compact: WARNING/ERROR; full: all levels, wrapped.
      3. Next line    — full: wrapped card sentence; both: verb button.

    Returns the active rig object (or None), the Snapshot, and the StageState.
    """
    snap = stage.snapshot(context)
    st = stage.evaluate(snap)

    # Region width for wrap_label; fallback 220 when no region attribute.
    width_px: int = getattr(getattr(context, 'region', None), 'width', 220) or 220

    # Lazy rig resolution — workflow.active_rig requires bpy.
    rig = None
    if bpy is not None:
        try:
            from b4artists_ml import workflow as _workflow
            rig = _workflow.active_rig(context)
        except Exception:
            pass

    # ── 1. STAGE STRIP ─────────────────────────────────────────────────────
    # Icon-only row fits narrow sidebars; one text line names current stage.
    # 'Stage %d of 5 — %s': literal template; no copy_.fmt entry yet —
    # flagged for Phase 4 copy audit (contains no forbidden term).
    # Icons: CHECKMARK = completed, RADIOBUT_ON = current,
    #        LOCKED = primary key locked, RADIOBUT_OFF = future.
    current_idx = 1
    current_stage_label = ''
    row = layout.row(align=True)
    for i, (key, lbl) in enumerate(copy_.STAGES, 1):
        primary_key = STAGE_PRIMARY_KEY.get(key, '')
        if key in st.completed:
            icon = 'CHECKMARK'
        elif key == st.current:
            icon = 'RADIOBUT_ON'
            current_idx = i
            current_stage_label = lbl
        elif primary_key and stage.locked(st, primary_key):
            icon = 'LOCKED'
        else:
            icon = 'RADIOBUT_OFF'
        row.label(text='', icon=icon)
    layout.label(text='Stage %d of 5 — %s' % (current_idx, current_stage_label))

    # ── 2. FEEDBACK CARD ───────────────────────────────────────────────────
    # compact: WARNING/ERROR only; full: all levels, text word-wrapped.
    # box.alert = True for ERROR level triggers Bforartists red highlight.
    if rig is not None and getattr(rig, 'b4ml_ui', None) is not None:
        fb = feedback.current(rig)
        if fb['text'] and (full or fb['level'] in ('WARNING', 'ERROR')):
            box = layout.box()
            box.alert = (fb['level'] == 'ERROR')
            icon = _LEVEL_ICON.get(fb['level'], 'INFO')
            wrap_label(box, fb['text'], icon=icon, width_px=width_px)
            if fb['fix']:
                op = box.operator(fb['fix'], text=fb['fix_label'] or 'Fix')
                for k, v in json.loads(fb['fix_props'] or '{}').items():
                    setattr(op, k, v)

    # ── 3. NEXT LINE ───────────────────────────────────────────────────────
    # full: wrapped card sentence first; both modes: verb on button
    # (§BEHAVIORAL SUCCESS item 1).
    card_text = copy_.CARDS.get(st.state_name, '')
    next_label, next_idname, next_props = st.next_action
    if full and card_text:
        wrap_label(layout, card_text, icon='INFO', width_px=width_px)
    if next_idname:
        row = layout.row()
        row.scale_y = 1.3
        op = row.operator(next_idname, text=copy_.NEXT_PREFIX + ' ' + next_label, icon='PLAY')
        for k, v in next_props.items():
            setattr(op, k, v)
    elif next_label:
        layout.label(text=copy_.NEXT_PREFIX + ' ' + next_label)

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
