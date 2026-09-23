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

_RUNNING_PROGRESS_PROP mirrors stage.snapshot() running-flag detection order (stage.py:199-211);
keeps the mapping local so stage.py stays pure-data with no UI dependency.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re as _re
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

# Maps snap.running values → B4ML_PG_settings progress-text property.
# Mirrors stage.snapshot() running-flag detection order (stage.py:199-211).
# BODY has no dedicated progress property (not in verified B4ML_PG_settings props).
_RUNNING_PROGRESS_PROP: dict[str, str] = {
    'TEMPORAL':  'temporal_progress',
    'BODY':      '',
    'CONTACT':   'contact_progress',
    'FLIGHT':    'flight_progress',
    'SECONDARY': 'secondary_progress',
    'CLEANUP':   'cleanup_progress',
}

# Matches "frame 34" or "frame 34.5" in progress-text strings (temporal_preview.py:57 format).
_FRAME_RE = _re.compile(r'frame (\d+(?:\.\d+)?)', _re.IGNORECASE)


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


def running_card(layout, rig, snap, width_px=None) -> None:
    """Draw a progress card for the active running task; no-op when snap.running is falsy.

    Contract §SOLVE_RUNNING: panel reduces to this card while a solve is active.
    Progress text from B4ML_PG_settings.*_progress — phase strings such as
    'Solving at frame 34' (temporal_preview.py:57); NOT fractions.

    Fraction: parses 'frame N' from text; if derivable from anchor range draws a
    BAR progress widget.  Falls back to wrap_label with icon='TIME'.
    Cancel operator drawn only for TEMPORAL; all others show a no-cancel note.
    All string literals here pass copy_.check (no forbidden terms).
    """
    if not snap.running:
        return

    box = layout.box()

    # ── Progress text ───────────────────────────────────────────────────────
    prog_text = ''
    if rig is not None:
        b4ml = getattr(rig, 'b4ml', None)
        if b4ml is not None:
            prop = _RUNNING_PROGRESS_PROP.get(snap.running, '')
            if prop:
                prog_text = str(getattr(b4ml, prop, '') or '')
    if not prog_text:
        prog_text = copy_.BADGES.get('SOLVE_RUNNING', 'Generating\u2026')

    # ── Fraction from frame text + anchor range ─────────────────────────────
    # Anchor frames read via min/max over rig.b4ml.anchors (mirrors motion.py:112-113,
    # review.py:100-101).
    factor = None
    if rig is not None:
        b4ml = getattr(rig, 'b4ml', None)
        if b4ml is not None:
            anchors = getattr(b4ml, 'anchors', [])
            first_f = min((a.frame for a in anchors), default=None)
            last_f  = max((a.frame for a in anchors), default=None)
            if first_f is not None and last_f is not None and abs(last_f - first_f) >= 1e-5:
                m = _FRAME_RE.search(prog_text)
                if m:
                    cur = float(m.group(1))
                    raw = (cur - first_f) / (last_f - first_f)
                    factor = max(0.0, min(1.0, raw))

    if factor is not None:
        box.progress(text=prog_text, factor=factor, type='BAR')
    else:
        wrap_label(box, prog_text, icon='TIME', width_px=width_px)

    # ── Cancel / no-cancel ──────────────────────────────────────────────────
    if snap.running == 'TEMPORAL':
        box.operator('b4ml.temporal_cancel', text='Cancel', icon='X')
    else:
        box.label(text='Runs to completion (cannot be interrupted)', icon='INFO')


def prelude(layout, context, full: bool = False, stage_key: str = '') -> tuple:
    """Draw the shared panel prelude; return (rig, snap, st).

    stage_key: STAGES key for this panel ('SETUP','POSE','MOTION','POLISH','REVIEW').
    Pass '' (default) to draw all steps unconditionally — preserves existing behaviour.

    full=False (default): compact — icon strip + stage line, WARNING/ERROR
    feedback card only, Next button without card sentence.
    full=True: complete — same strip, all feedback levels (wrapped), card
    sentence (wrapped) then Next button.  Pass full=True from setup.py.

    Drawing order (contract §STATE MAP, §BEHAVIORAL SUCCESS items 3, 7, 8):
      1. Stage strip   — icon-only row: ALWAYS drawn in every panel (orientation anchor).
                         'Stage N of 5 — Label' text line: only when is_current.
      2. Feedback card — current-panel: all levels (wrapped); non-current: WARNING/ERROR only. ALWAYS drawn
                         (contract §BEHAVIORAL SUCCESS item 8: never scroll to learn outcome).
      2b. Running card — only when is_current; progress bar + Cancel/note.
      3. Next line     — only when is_current; full: wrapped card sentence first; both: verb
                         button. Next button suppressed while TEMPORAL running (Cancel shown).
                         Next button also suppressed when the feedback fix-button IS the next
                         action (same idname + props) — prevents the duplicate shown in QA #1/#2.

    Returns the active rig object (or None), the Snapshot, and the StageState.
    """
    snap = stage.snapshot(context)
    st = stage.evaluate(snap)
    is_current = (stage_key == '' or stage_key == st.current)

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

    # Resolve next action early so the feedback card can detect duplicates.
    next_label, next_idname, next_props = st.next_action

    # ── 1. STAGE STRIP ─────────────────────────────────────────────────────
    # Icon-only row fits narrow sidebars; one text line names current stage
    # via copy_.STAGE_LINE (gaps-2).
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
    if is_current:
        layout.label(text=copy_.fmt(copy_.STAGE_LINE, n=current_idx,
                                    total=len(copy_.STAGES), label=current_stage_label))

    # ── 2. FEEDBACK CARD ───────────────────────────────────────────────────
    # compact: WARNING/ERROR only; full: all levels, text word-wrapped.
    # box.alert = True for ERROR level triggers Bforartists red highlight.
    # Drawn in every panel regardless of is_current (item 8: never scroll to learn outcome).
    fix_is_next = False
    if rig is not None and getattr(rig, 'b4ml_ui', None) is not None:
        fb = feedback.current(rig)
        show_all = is_current if stage_key else full
        if fb['text'] and (show_all or fb['level'] in ('WARNING', 'ERROR')):
            box = layout.box()
            box.alert = (fb['level'] == 'ERROR')
            icon = _LEVEL_ICON.get(fb['level'], 'INFO')
            wrap_label(box, fb['text'], icon=icon, width_px=width_px)
            if fb['fix']:
                op = box.operator(fb['fix'], text=fb['fix_label'] or 'Fix')
                for k, v in json.loads(fb['fix_props'] or '{}').items():
                    setattr(op, k, v)
                fix_is_next = (
                    fb['fix'] == next_idname
                    and json.loads(fb['fix_props'] or '{}') == next_props
                )

    # ── 2b. RUNNING CARD ───────────────────────────────────────────────────
    # Only for the current stage's panel — running state is stage-specific.
    if is_current:
        running_card(layout, rig, snap, width_px=width_px)

    # ── 3. NEXT LINE ───────────────────────────────────────────────────────
    # full: wrapped card sentence first; both modes: verb on button
    # (§BEHAVIORAL SUCCESS item 1).
    # Suppressed in non-current panels and when fix button already IS the next action.
    if is_current:
        card_text = copy_.CARDS.get(st.state_name, '')
        if full and card_text:
            wrap_label(layout, card_text, icon='INFO', width_px=width_px)
        if next_idname and snap.running != 'TEMPORAL' and not fix_is_next:
            row = layout.row()
            row.scale_y = 1.3
            op = row.operator(next_idname, text=copy_.NEXT_PREFIX + ' ' + next_label, icon='PLAY')
            for k, v in next_props.items():
                setattr(op, k, v)
        elif next_label and not fix_is_next:
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
        wrap_label(layout, reason, icon='LOCKED')
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
    wrap_label(layout, copy_.fmt(template, name=name))


def lock_description(st, key: str) -> str:
    """Return the lock reason for *key* in *st*, or '' if available.

    Pure function; wired into operator dynamic description() classmethods
    during Phase 1 cut-over.
    """
    return stage.locked(st, key)
