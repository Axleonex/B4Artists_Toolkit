"""Pose panel for B4Artists ML.

Plan §3 "Pose"; Contract §STATE MAP states MAPPED, POSING_OBJECT,
POSING_POSE_MODE, SOLVE_RUNNING; §FAILURE rows "Begin posing while
playing", "Solve failure".

Verified property names (ui.py 2026-09-22):
  B4ML_PG_settings.body_payload         StringProperty  (ui.py:349)
  B4ML_PG_settings.body_targets         CollectionProperty  (ui.py:~350)
  B4ML_PG_settings.show_body_targets    BoolProperty  (ui.py:347)
  B4ML_PG_settings.body_live            BoolProperty  (ui.py:363)
  B4ML_PG_settings.body_running         BoolProperty  (ui.py:364)
  B4ML_PG_settings.body_progress        StringProperty  (ui.py:365)
  B4ML_PG_settings.body_balance         BoolProperty  (ui.py:299)
  B4ML_PG_settings.body_balance_*       various  (ui.py:300-304)
  B4ML_PG_settings.body_limits          CollectionProperty  (ui.py:342)
  B4ML_PG_settings.show_body_limits     BoolProperty  (ui.py:348)
  B4ML_PG_settings.body_limit_preset    EnumProperty  (ui.py:~343)
  B4ML_PG_settings.body_limit_control   StringProperty  (ui.py:~344)
  B4ML_PG_settings.body_strength        FloatProperty  (ui.py:362)
  B4ML_PG_settings.body_influence       FloatProperty  (ui.py:361)
  B4ML_PG_settings.temporal_progress    StringProperty  (ui.py:218)
  B4ML_PG_body_target.enabled           BoolProperty  (ui.py:~140)
  B4ML_PG_body_target.use_orientation   BoolProperty  ("Rot")
  B4ML_PG_body_target.use_pole          BoolProperty  (ui.py:~24)
  B4ML_PG_body_target.pole              PointerProperty(Object)  (ui.py:20)
  B4ML_PG_body_target.pole_distance     FloatProperty  (ui.py:26)

Operators used (verified ui.py):
  b4ml.body          operation=BEGIN|KEEP|CANCEL|MIRROR_TARGETS|
                               ALIGN_POLE|FLIP_POLE|SET_POLE_DISTANCE|
                               SAVE_POSE_ASSET|APPLY_POSE_ASSET|
                               APPLY_LIMIT_PRESET|CALIBRATE_BEND
  b4ml.body_solve    (ui.py:1084)
  b4ml.body_live     (ui.py:1220)
  object.mode_set    mode='OBJECT'

Pole-supporting target names derived from body_preview.POLE_JOINTS
  {7:6,10:9,13:12,16:15} × TARGETS → Hand L, Hand R, Foot L, Foot R
  (body_preview.py:17-21,45-46).
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
    from .. import copy as copy_
except ImportError:
    _panels_dir = os.path.dirname(os.path.abspath(__file__))
    _pkg_dir = os.path.dirname(_panels_dir)

    def _load_module(qualified: str, path: str) -> object:
        if qualified in sys.modules:
            return sys.modules[qualified]
        spec = importlib.util.spec_from_file_location(qualified, path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules[qualified] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    header = _load_module(                                   # type: ignore[assignment]
        'b4artists_ml.ui_workflow.panels.header',
        os.path.join(_panels_dir, 'header.py'),
    )
    copy_ = _load_module(                                    # type: ignore[assignment]
        'b4artists_ml.ui_workflow.copy',
        os.path.join(_pkg_dir, 'copy.py'),
    )

# ---------------------------------------------------------------------------
# Target names that support pole helpers (body_preview.POLE_JOINTS indices
# 7, 10, 13, 16 → Hand L, Hand R, Foot L, Foot R).
# ---------------------------------------------------------------------------
_POLE_LABELS: frozenset[str] = frozenset({'Hand L', 'Hand R', 'Foot L', 'Foot R'})


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class B4ML_PT_pose(_Panel):  # type: ignore[valid-type]
    """Pose panel — whole-body posing session controls.

    Plan §3 "Pose"; contract states MAPPED, POSING_OBJECT, POSING_POSE_MODE,
    SOLVE_RUNNING.
    """

    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'B4Artists ML'
    bl_label       = 'Pose'
    bl_order       = 1

    @classmethod
    def poll(cls, context) -> bool:
        return bpy is not None

    def draw(self, context) -> None:
        rig, snap, st = header.prelude(self.layout, context)
        layout = self.layout

        # ── SOLVE_RUNNING ──────────────────────────────────────────────────
        # Prelude already drew next_action (cancel or wait label).
        # Show progress string if the rig exposes one.
        if snap.running:
            if rig is not None:
                b4ml = getattr(rig, 'b4ml', None)
                if b4ml is not None:
                    if snap.running == 'TEMPORAL':
                        progress = getattr(b4ml, 'temporal_progress', '')
                    else:
                        progress = getattr(b4ml, 'body_progress', '')
                    if progress:
                        layout.label(text=progress)
            return

        # ── Non-whole-body posing modes ────────────────────────────────────
        # ASSISTED and QUADRUPED are handled in the full panel.
        if snap.posing not in ('', 'BODY'):
            layout.label(text='Procedural or assisted posing — use the full panel.')
            return

        # ── Idle (no active session) ───────────────────────────────────────
        if snap.posing == '':
            header.action_row(layout, st, 'pose.begin', 'b4ml.body',
                              icon='ARMATURE_DATA', operation='BEGIN')
            return

        # ── Active whole-body session (snap.posing == 'BODY') ─────────────
        b4ml = getattr(rig, 'b4ml', None) if rig is not None else None

        # 1. Mode guard: warn when not in Object Mode (contract POSING_POSE_MODE).
        if snap.mode != 'OBJECT':
            row = layout.row()
            row.alert = True
            row.label(text=copy_.HUD['mode_alert'], icon='ERROR')
            row.operator('object.mode_set',
                         text=copy_.BUTTONS['pose.mode_fix']).mode = 'OBJECT'

        # 2. Compact target list.
        if b4ml is not None:
            box_t = layout.box()
            show_targets = getattr(b4ml, 'show_body_targets', True)
            box_t.prop(b4ml, 'show_body_targets',
                       icon='TRIA_DOWN' if show_targets else 'TRIA_RIGHT')
            if show_targets:
                for item in getattr(b4ml, 'body_targets', []):
                    row = box_t.row(align=True)
                    # Pelvis is always pinned; show label only (no toggle).
                    if item.name != 'Pelvis':
                        row.prop(item, 'enabled', text=item.name)
                    else:
                        row.label(text=item.name)
                    # Rot toggle present on all targets; solver respects controls_version.
                    row.prop(item, 'use_orientation', text='Rot')
                    # Per-target pole foldout for Hand / Foot targets with a linked pole.
                    if item.name in _POLE_LABELS and getattr(item, 'pole', None):
                        pole_label = (
                            'Elbow Direction'
                            if item.name.startswith('Hand')
                            else 'Knee Direction'
                        )
                        use_pole = getattr(item, 'use_pole', False)
                        box_t.prop(
                            item, 'use_pole', text=pole_label,
                            icon='TRIA_DOWN' if use_pole else 'TRIA_RIGHT',
                        )
                        if use_pole:
                            p_row = box_t.row(align=True)
                            op_a = p_row.operator('b4ml.body', text='Align Bend')
                            op_a.operation = 'ALIGN_POLE'
                            op_a.target_name = item.name
                            op_f = p_row.operator('b4ml.body', text='Flip Side')
                            op_f.operation = 'FLIP_POLE'
                            op_f.target_name = item.name
                            d_row = box_t.row(align=True)
                            d_row.prop(item, 'pole_distance', text='')
                            op_d = d_row.operator('b4ml.body', text='Set Distance')
                            op_d.operation = 'SET_POLE_DISTANCE'
                            op_d.target_name = item.name

        # 3. Task controls in one aligned row.
        task = layout.row(align=True)
        header.action_row(task, st, 'pose.solve', 'b4ml.body_solve', icon='PLAY')
        # Live toggle — port from ui.py L2704: operator text/icon reflects live state.
        if b4ml is not None:
            live = getattr(b4ml, 'body_live', False)
            task.operator(
                'b4ml.body_live',
                text='Stop Live' if live else 'Live',
                icon='PAUSE' if live else 'PLAY',
            )
        header.action_row(task, st, 'pose.keep', 'b4ml.body',
                          icon='KEYFRAME_HLT', operation='KEEP')
        header.action_row(task, st, 'pose.cancel', 'b4ml.body',
                          icon='X', operation='CANCEL')

        # 4. "More" box: balance, limits, mirror, pose-asset controls.
        if b4ml is not None:
            more = layout.box()
            more.label(text='More')

            # Mirror targets.
            mirror = more.row(align=True)
            op_l = mirror.operator('b4ml.body', text='Mirror L to R')
            op_l.operation = 'MIRROR_TARGETS'
            op_l.mirror_direction = 'LEFT_TO_RIGHT'
            op_r = mirror.operator('b4ml.body', text='Mirror R to L')
            op_r.operation = 'MIRROR_TARGETS'
            op_r.mirror_direction = 'RIGHT_TO_LEFT'

            # Pose asset.
            more.label(text='Pose Asset')
            asset = more.row(align=True)
            op_save = asset.operator('b4ml.body', text='Save Solved Pose')
            op_save.operation = 'SAVE_POSE_ASSET'
            op_use = asset.operator('b4ml.body', text='Apply Pose')
            op_use.operation = 'APPLY_POSE_ASSET'

            # Rotation limits (foldout via show_body_limits).
            show_limits = getattr(b4ml, 'show_body_limits', False)
            more.prop(b4ml, 'show_body_limits',
                      icon='TRIA_DOWN' if show_limits else 'TRIA_RIGHT')
            if show_limits:
                more.label(text='Rotation limits')
                preset_row = more.row(align=True)
                preset_row.prop(b4ml, 'body_limit_preset', text='')
                preset_row.operator(
                    'b4ml.body', text='Apply to Mapped Controls',
                ).operation = 'APPLY_LIMIT_PRESET'
                more.prop_search(b4ml, 'body_limit_control',
                                 b4ml, 'body_limits', text='Control')
                limit_item = getattr(b4ml, 'body_limits', {}).get(
                    getattr(b4ml, 'body_limit_control', ''), None
                )
                if limit_item is not None:
                    lb = more.box()
                    lb.prop(limit_item, 'enabled', text='Limit This Control')
                    lb.label(text='Source: ' + getattr(limit_item, 'preset_provenance', ''))
                    if getattr(limit_item, 'enabled', False):
                        if getattr(limit_item, 'joint_available', False):
                            lb.prop(limit_item, 'space')
                        else:
                            lb.label(text='Control space only')
                        lb.prop(limit_item, 'swing')
                        lb.prop(limit_item, 'twist_min')
                        lb.prop(limit_item, 'twist_max')
                        lb.prop(limit_item, 'use_bend_plane')
                        if getattr(limit_item, 'use_bend_plane', False):
                            lb.prop(limit_item, 'bend_axis')
                            lb.operator(
                                'b4ml.body',
                                text='Use Current Bend as Forward',
                            ).operation = 'CALIBRATE_BEND'
                            lb.prop(limit_item, 'bend_min')
                            lb.prop(limit_item, 'bend_max')
                            lb.prop(limit_item, 'bend_sideways')
                more.label(text=f'{sum(getattr(i, "enabled", False) for i in getattr(b4ml, "body_limits", []))} controls limited')

            # Balance assist.
            more.prop(b4ml, 'body_balance')
            if getattr(b4ml, 'body_balance', False):
                for field in (
                    'body_balance_strength',
                    'body_balance_inset',
                    'body_balance_free_pelvis',
                    'body_balance_dynamic',
                ):
                    more.prop(b4ml, field)
                if getattr(b4ml, 'body_balance_dynamic', False):
                    more.prop(b4ml, 'body_balance_velocity')
                more.label(text='Procedural balance — authored mass + support.')

            # Solver influence.
            more.prop(b4ml, 'body_strength')
            more.prop(b4ml, 'body_influence')


CLASSES: tuple[type, ...] = (B4ML_PT_pose,)
