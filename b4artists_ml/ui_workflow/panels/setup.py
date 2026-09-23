"""Setup panel for B4Artists ML.

Plan §3 "Setup" subsection.
Contract states: NO_RIG, UNSUPPORTED_RIG, MAPPED.

bl_order = 0; drawn first in the B4Artists ML sidebar category.

Verified facts (2026-09-22):
  copy.py:66-80  BUTTONS['setup.inspect'] = 'Check Rig'
  copy.py:100-104 FAMILY dict keys: 'HUMANOID', 'QUADRUPED', ''
  copy.py:110-121 CARDS['NO_RIG'], CARDS['UNSUPPORTED_RIG']
  stage.py:73-86  Snapshot.mapped, .mapping_error, .family
  header.py:82-150 prelude(layout, context) -> (rig, snap, st)
  ui.py:926-928   rig.b4ml.status set by INSPECT to one-line mapping summary
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
    _panels_dir  = os.path.dirname(os.path.abspath(__file__))
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

class B4ML_PT_setup(_Panel):  # type: ignore[valid-type]
    """Character setup card: rig identity, mapping status, and Check Rig action.

    Plan §3 "Setup"; contract states NO_RIG, UNSUPPORTED_RIG, MAPPED.
    """

    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'B4Artists ML'
    bl_label       = 'Setup'
    bl_order       = 0

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def draw(self, context) -> None:
        rig, snap, st = header.prelude(self.layout, context, full=True, stage_key='SETUP')

        box = self.layout.box()

        # 1. Rig name, or no-rig guidance
        if rig is None:
            box.label(text=copy.CARDS['NO_RIG'])
        else:
            box.label(text=rig.name, icon='ARMATURE_DATA')

        # 2. Family badge
        box.label(text=copy.FAMILY.get(snap.family, copy.FAMILY['']))

        # 3. Mapping result line
        if snap.mapped:
            b4ml_state = getattr(rig, 'b4ml', None) if rig is not None else None
            box.label(text=getattr(b4ml_state, 'status', ''))
        else:
            err_box = box.box()
            err_box.alert = True
            header.wrap_label(err_box, snap.mapping_error, icon='ERROR',
                              width_px=getattr(getattr(context, 'region', None), 'width', 220))

        # 4. Check Rig — only when rig is mapped; the error card's fix button
        #    already offers INSPECT in the unsupported-rig state, so showing it
        #    again here would produce a redundant third button on screen.
        if rig is not None and snap.mapped:
            op = box.operator('b4ml.action', text=copy.BUTTONS['setup.inspect'], icon='VIEWZOOM')
            op.operation = 'INSPECT'


CLASSES = (B4ML_PT_setup,)
