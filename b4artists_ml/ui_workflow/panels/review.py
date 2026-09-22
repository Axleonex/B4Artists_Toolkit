"""Review panel for B4Artists ML.

Plan §3 "Review" subsection.
Contract states: PREVIEW_ACTIVE, KEPT, RESTORED.
Contract §FAILURE rows: "Keep / Discard with active posing session",
  "Restore with wrong active action" — handled via header.action_row lock gate.

bl_order = 3; drawn fourth in the B4Artists ML sidebar category.

Verified facts (2026-09-22):
  ui.py:15       B4ML_PG_anchor.frame: FloatProperty
  ui.py:378-386  state.anchors (CollectionProperty), state.candidate_action,
                 state.kept_action (PointerProperty(Action))
  ui.py:910      b4ml.action operations: KEEP, DISCARD, RESTORE_SOURCE
  ui.py:2774-75  first/last anchor frame pattern: min/max over state.anchors
  ui.py:2801-06  KEEP / DISCARD drawn when state.candidate_action
  ui.py:2826-27  RESTORE_SOURCE drawn when state.kept_action and not candidate
  copy.py:66-80  BUTTONS['review.keep/discard/restore'], VOCAB['candidate action']
  copy.py:86-98  BADGES keys for PREVIEW_ACTIVE, KEPT, RESTORED
  header.py:174  badge(layout, st, rig)
  header.py:153  action_row(layout, st, key, idname, *, icon, **props)
"""
from __future__ import annotations

import importlib.util
import os
import sys

# ---------------------------------------------------------------------------
# Guarded bpy import
# ---------------------------------------------------------------------------
try:
    import bpy
except ImportError:
    bpy = None  # type: ignore[assignment]

_Panel = bpy.types.Panel if bpy is not None else object

# ---------------------------------------------------------------------------
# Sibling imports — relative inside the package; importlib fallback for tests.
# ---------------------------------------------------------------------------
try:
    from .. import copy
    from . import header
except ImportError:
    _panels_dir   = os.path.dirname(os.path.abspath(__file__))
    _workflow_dir = os.path.dirname(_panels_dir)

    def _load_mod(qualified: str, path: str) -> object:
        if qualified in sys.modules:
            return sys.modules[qualified]
        spec = importlib.util.spec_from_file_location(qualified, path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules[qualified] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    copy = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.copy',
        os.path.join(_workflow_dir, 'copy.py'),
    )
    header = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.panels.header',
        os.path.join(_panels_dir, 'header.py'),
    )


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class B4ML_PT_review(_Panel):  # type: ignore[valid-type]
    """Generate-and-review card: badge, range, keep/discard/restore actions.

    Plan §3 "Review"; contract states PREVIEW_ACTIVE, KEPT, RESTORED.
    """

    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'B4Artists ML'
    bl_label       = 'Review'
    bl_order       = 3

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def draw(self, context) -> None:
        rig, snap, st = header.prelude(self.layout, context)
        layout = self.layout

        # 1. State badge: Original animation / Previewing: name / Kept: name
        header.badge(layout, st, rig)

        # 2. Frame range from key-pose anchors + preview-range indicator
        if rig is not None:
            b4ml_props = getattr(rig, 'b4ml', None)
            if b4ml_props is not None:
                anchors = getattr(b4ml_props, 'anchors', [])
                first_f = min((a.frame for a in anchors), default=None)
                last_f  = max((a.frame for a in anchors), default=None)
                if first_f is not None:
                    row = layout.row()
                    row.label(text=f'Frames {first_f:g}\u2013{last_f:g}')
                    scene = getattr(context, 'scene', None)
                    if getattr(scene, 'use_preview_range', False):
                        row.label(text='Preview range active', icon='PREVIEW_RANGE')

        # 3-5. State-specific controls
        if st.state_name == 'PREVIEW_ACTIVE':
            # Indicator: which animation is currently visible on the rig
            anim_data   = getattr(rig, 'animation_data', None) if rig is not None else None
            b4ml_props  = getattr(rig, 'b4ml', None) if rig is not None else None
            current_act = getattr(anim_data, 'action', None)
            preview_act = getattr(b4ml_props, 'candidate_action', None)
            if current_act is not None and current_act is preview_act:
                layout.label(text=copy.VOCAB['candidate action'])   # 'Preview'
            else:
                layout.label(text=copy.VOCAB['source action'])      # 'Original animation'
            header.action_row(layout, st, 'review.keep',    'b4ml.action',
                              icon='CHECKMARK', operation='KEEP')
            header.action_row(layout, st, 'review.discard', 'b4ml.action',
                              icon='X', operation='DISCARD')

        elif st.state_name == 'KEPT':
            header.action_row(layout, st, 'review.restore', 'b4ml.action',
                              icon='LOOP_BACK', operation='RESTORE_SOURCE')

        else:
            # RESTORED, MAPPED, ANCHORS_CAPTURED, etc. — keep panel non-blank
            card_text = copy.CARDS.get(st.state_name, '')
            if card_text:
                layout.label(text=card_text)


CLASSES = (B4ML_PT_review,)
