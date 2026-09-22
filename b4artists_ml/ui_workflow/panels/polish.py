"""Polish stage panel for B4Artists ML — ui_workflow/panels/polish.py

Plan §3 "Polish"; Phase 5 goal W1.
Contract §STATE MAP, §BEHAVIORAL SUCCESS items 3, 7, 8.

bl_order = 4; drawn fifth in the B4Artists ML sidebar category.

Verified source lines:
  Contacts  action_row  panels/advanced.py:1104  idname 'b4ml.contact_solve'   key 'polish.contacts'
  Airborne  action_row  panels/advanced.py:1186  idname 'b4ml.flight_solve'    key 'polish.flight'
  Cleanup   action_row  panels/advanced.py:1270  idname 'b4ml.cleanup_solve'   key 'polish.cleanup'
  Secondary action_row  panels/advanced.py:1550  idname 'b4ml.secondary_solve' key 'polish.secondary'
  PREREQ literal        panels/advanced.py:994,1145,1258,1343 — 'Needs a preview or kept result.'
  snap.running values   stage.py:87  'CONTACT' | 'FLIGHT' | 'CLEANUP' | 'SECONDARY'
  copy.PREREQ absent in this lane (gaps-2 not landed); literals used.

DESIGN DEFAULTS (assumed, pending animator session):
  Controls clustered per card (not inline per row), matching Pose panel slice 1.
  Running indicator: status line shown when snap.running matches the feature;
  no per-frame progress bar at this stage.
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

    header = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.panels.header',
        os.path.join(_panels_dir, 'header.py'),
    )


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

# Literal matching panels/advanced.py:994,1145,1258,1343
_PREREQ = 'Needs a preview or kept result.'


class B4ML_PT_polish(_Panel):  # type: ignore[valid-type]
    """Polish stage panel: Contacts, Airborne, Cleanup, Secondary Motion.

    Plan §3 "Polish"; Phase 5 goal W1.
    Promotes four procedural correction features from Advanced into first-class
    stage cards.  Full option sets remain in Advanced until duplication is
    removed in a later packet.
    """

    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'B4Artists ML'
    bl_label       = 'Polish'
    bl_order       = 4

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def draw(self, context) -> None:
        rig, snap, st = header.prelude(self.layout, context)
        layout = self.layout
        b4ml = getattr(rig, 'b4ml', None) if rig is not None else None

        # ── Contacts ───────────────────────────────────────────────────────
        # Procedural geometric contact correction.
        # Operator: b4ml.contact_solve (advanced.py:1104); key: polish.contacts.
        box = layout.box()
        box.label(text='Contacts', icon='MOD_PHYSICS')
        box.label(text=_PREREQ)
        if snap.running == 'CONTACT':
            box.label(text='Running\u2026', icon='TIME')
        else:
            if b4ml is not None:
                box.prop(b4ml, 'contact_limb')
                box.prop(b4ml, 'show_contact_overlay')
            header.action_row(box, st, 'polish.contacts', 'b4ml.contact_solve',
                              text='Preview Contact Correction')

        # ── Airborne ───────────────────────────────────────────────────────
        # Procedural COM flight arc correction.
        # Operator: b4ml.flight_solve (advanced.py:1186); key: polish.flight.
        box = layout.box()
        box.label(text='Airborne', icon='FORCE_WIND')
        box.label(text=_PREREQ)
        if snap.running == 'FLIGHT':
            box.label(text='Running\u2026', icon='TIME')
        else:
            if b4ml is not None:
                box.prop(b4ml, 'flight_backend')
            header.action_row(box, st, 'polish.flight', 'b4ml.flight_solve',
                              text='Preview COM Flight')

        # ── Cleanup ────────────────────────────────────────────────────────
        # Procedural copied-curve cleanup.
        # Operator: b4ml.cleanup_solve (advanced.py:1270); key: polish.cleanup.
        box = layout.box()
        box.label(text='Cleanup', icon='BRUSH_DATA')
        box.label(text=_PREREQ)
        if snap.running == 'CLEANUP':
            box.label(text='Running\u2026', icon='TIME')
        else:
            if b4ml is not None:
                box.prop(b4ml, 'cleanup_reduce')
                box.prop(b4ml, 'cleanup_tolerance')
            header.action_row(box, st, 'polish.cleanup', 'b4ml.cleanup_solve',
                              text='Preview Cleanup', icon='PLAY')

        # ── Secondary Motion ───────────────────────────────────────────────
        # Procedural control physics for secondary motion.
        # Operator: b4ml.secondary_solve (advanced.py:1550); key: polish.secondary.
        box = layout.box()
        box.label(text='Secondary Motion', icon='RIGID_BODY')
        box.label(text=_PREREQ)
        if snap.running == 'SECONDARY':
            box.label(text='Running\u2026', icon='TIME')
        else:
            if b4ml is not None:
                box.prop(b4ml, 'secondary_chain_propagation')
                box.prop(b4ml, 'secondary_frequency')
            header.action_row(box, st, 'polish.secondary', 'b4ml.secondary_solve',
                              text='Preview Secondary', icon='PLAY')


CLASSES = (B4ML_PT_polish,)
