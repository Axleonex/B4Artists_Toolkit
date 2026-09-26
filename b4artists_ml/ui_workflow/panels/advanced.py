"""B4ML Advanced panel and subpanels — ui_workflow/panels/advanced.py

Plan §3 "Advanced"; Contract states — all stages.
Ports existing box blocks from B4ML_PT_main.draw (ui.py:2021-2828) verbatim
per packet: .enabled assignments removed (operator poll gates); four primary
polish actions wrapped in header.action_row with the polish.* key.

Verified source lines (ui.py):
  _draw_wrapped               L413-421
  _draw_rig_diagnostics       L424-468 (row.alert kept; no .enabled)
  _draw_rig_mapping_editor    L479-503 (col.enabled L487,L492; clear_all.enabled
                               L498 dropped)
  _draw_contact_interval_controls L205-214 (trim.enabled L212 dropped)
  _contact_review_counts      L150-156 (delegated to _ui)
  Body helpers                L975-1023 (all .enabled params removed)
  _quadruped_target_ui_label  L1034-1035
  Center of Mass              L2051-2081 (col.enabled L2054 dropped;
                               'World COM (internal units):' → 'World COM:'
                               — forbidden term 'internal units' fixed)
  Airborne                    L2083-2137 (col.enabled L2088 dropped)
  Contacts                    L2139-2219 (.enabled L2143,2147,2151,2189,2191,
                               2199,2201,2205 dropped; L2214 → action_row)
  Cleanup                     L2221-2254 (.enabled L2225,2228,2230 dropped;
                               L2231 → action_row polish.cleanup)
  Secondary Motion            L2255-2413 (.enabled L2260,2264,2274,2282 dropped;
                               L2392 → action_row polish.secondary)
  Quadruped                   L2415-2623 (.enabled L2457,2458,2487,2488,2497-2502,
                               2509-2511 dropped; col.enabled L2524; overlay_options
                               L2536; phase_row L2605 dropped; L2590 → action_row)
  Assisted Pose               L2625-2757 (.enabled L2633,2642,2646,2648,2652,
                               2702,2717 dropped)
  Saved Results               L2042-2046
"""
from __future__ import annotations

import importlib.util
import json
import math
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
# Sibling imports
# ---------------------------------------------------------------------------
try:
    from .. import copy as copy_
    from . import header
except ImportError:
    _panels_dir = os.path.dirname(os.path.abspath(__file__))
    _uw_dir = os.path.dirname(_panels_dir)

    def _load_mod(qualified: str, path: str) -> object:
        if qualified in sys.modules:
            return sys.modules[qualified]
        spec = importlib.util.spec_from_file_location(qualified, path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules[qualified] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    copy_ = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.copy', os.path.join(_uw_dir, 'copy.py'))
    header = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.panels.header', os.path.join(_panels_dir, 'header.py'))

_Panel = bpy.types.Panel if bpy is not None else object

_HUMANOID_CONTACT_LIMBS = frozenset(('leg-L', 'leg-R', 'arm-L', 'arm-R'))
_QUADRUPED_POLE_UI_LABELS: dict[str, str] = {
    'Fore Pole L': 'Fore L Pole', 'Fore Pole R': 'Fore R Pole',
    'Hind Pole L': 'Hind L Pole', 'Hind Pole R': 'Hind R Pole',
}


# ---------------------------------------------------------------------------
# Lazy module accessor
# ---------------------------------------------------------------------------
def _lazy(name: str) -> object:
    try:
        import importlib as _il
        return _il.import_module(name)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Inlined helpers — no .enabled assignments (ui.py:413-503, L975-1023)
# ---------------------------------------------------------------------------

def _draw_wrapped(layout, text: str, icon: str = 'NONE', width: int = 30) -> None:
    """Word-wrap *text* into layout labels (ui.py:413-421)."""
    words = str(text).split(); lines: list[str] = []; line: list[str] = []
    for word in words:
        if line and len(' '.join(line + [word])) > width:
            lines.append(' '.join(line)); line = [word]
        else:
            line.append(word)
    if line:
        lines.append(' '.join(line))
    for index, value in enumerate(lines):
        layout.label(text=value, icon=icon if index == 0 else 'BLANK1')


def _json_object(value: str) -> dict:
    """Deserialise a JSON string to a dict; return {} on failure."""
    try:
        record = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return record if isinstance(record, dict) else {}


def _draw_rig_diagnostics(layout, state, report) -> None:
    """Rig diagnostics collapsible box (ui.py:424-468; no .enabled)."""
    box = layout.box()
    box.prop(state, 'show_rig_diagnostics',
             icon='TRIA_DOWN' if getattr(state, 'show_rig_diagnostics', False) else 'TRIA_RIGHT',
             emboss=False)
    if not getattr(state, 'show_rig_diagnostics', False):
        return
    if report is None:
        box.label(text='Click Inspect / Refresh above.', icon='INFO'); return
    box.label(text='Snapshot; refresh after rig edits', icon='INFO')
    box.label(text=report['profile'], icon='ARMATURE_DATA')
    box.label(text=f"{report['family']} / {report['mapping_schema']}")
    box.label(text=(f"Semantic roles: {report['mapped_required_role_count']}/"
                    f"{report['required_role_count']}"))
    box.label(text=f"Mapped controls: {report['mapped_control_count']}")
    box.label(text=f"Directly writable: {report['writable_control_count']}")
    if report['correction_state'] == 'active':
        box.label(text=f"Manual corrections: {len(report['manual_corrections'])}", icon='CHECKMARK')
    elif report['correction_state'] == 'invalid':
        _draw_wrapped(box, report['correction_error'], icon='ERROR')
    excluded = [(k, v) for k, v in report['excluded_bone_counts'].items() if v]
    if excluded:
        box.label(text='Excluded from B4ML controls:')
        for k, v in excluded:
            box.label(text=f'{k.title()}: {v}')
    for wrow in report['workflows']:
        if not wrow['applicable']:
            continue
        row = box.row()
        row.alert = not wrow['ready']
        short_label = {'humanoid_whole_body': 'Whole-Body Pose',
                       'quadruped_whole_body': 'Four-Paw Whole-Body Pose'}.get(
                           wrow['id'], wrow['label'])
        row.label(text=short_label, icon='CHECKMARK' if wrow['ready'] else 'ERROR')
        if not wrow['ready']:
            _draw_wrapped(box, wrow['detail'])
    if report['missing_roles']:
        box.label(text='Missing semantic roles:', icon='ERROR')
        for start in range(0, len(report['missing_roles']), 4):
            box.label(text=', '.join(report['missing_roles'][start:start + 4]))
    if report['blocked_mapped_controls']:
        box.label(text='Blocked mapped controls:', icon='ERROR')
        box.label(text=', '.join(report['blocked_mapped_controls'][:4]))
    if report['unsafe_mapped_controls']:
        box.label(text='Structural bones mapped as controls:', icon='ERROR')
        box.label(text=', '.join(report['unsafe_mapped_controls'][:4]))
    for warning in report['warnings']:
        _draw_wrapped(box, warning, icon='INFO')
    box.prop(state, 'show_rig_role_mappings',
             icon='TRIA_DOWN' if getattr(state, 'show_rig_role_mappings', False) else 'TRIA_RIGHT',
             emboss=False)
    if getattr(state, 'show_rig_role_mappings', False):
        for mapping in report['mapped_roles']:
            box.label(text=mapping['role'] + ' -> ' + mapping['bone'])


def _draw_rig_mapping_editor(layout, obj, state, profile, correction_rows,
                              correction_error) -> None:
    """Mapping correction editor (ui.py:479-503; .enabled removed)."""
    box = layout.box()
    box.prop(state, 'show_mapping_corrections',
             icon='TRIA_DOWN' if getattr(state, 'show_mapping_corrections', False) else 'TRIA_RIGHT',
             emboss=False)
    if not getattr(state, 'show_mapping_corrections', False) and not correction_error:
        return
    if correction_error:
        _draw_wrapped(box, correction_error, icon='ERROR')
        box.operator('b4ml.mapping_correction',
                     text='Clear Invalid Corrections', icon='X').operation = 'CLEAR_ALL'
        return
    if getattr(profile, 'family', '') != 'humanoid':
        box.label(text='Available on recognized humanoid adapters.', icon='INFO')
        return
    col = box.column()
    col.prop(state, 'mapping_role', text='Role')
    col.prop_search(state, 'mapping_bone', obj.data, 'bones', text='Bone')
    row = col.row(align=True)
    row.operator('b4ml.mapping_correction', text='Apply Role').operation = 'APPLY'
    row.operator('b4ml.mapping_correction', text='Clear Role').operation = 'CLEAR_ROLE'
    col.operator('b4ml.mapping_correction',
                 text='Clear All Corrections', icon='X').operation = 'CLEAR_ALL'
    if correction_rows:
        box.label(text='Active corrections:')
        for role, bone in correction_rows:
            box.label(text=role + ' -> ' + bone)
    else:
        box.label(text='No manual corrections.', icon='INFO')


def _draw_contact_interval_controls(layout, state) -> None:
    """Contact interval jump/trim controls (ui.py:205-214; trim.enabled dropped)."""
    jump = layout.row(align=True)
    jump.operator('b4ml.contact', text='Blend In').operation = 'GO_BLEND_IN'
    jump.operator('b4ml.contact', text='Hold Start').operation = 'GO_START'
    jump = layout.row(align=True)
    jump.operator('b4ml.contact', text='Hold End').operation = 'GO_END'
    jump.operator('b4ml.contact', text='Blend Out').operation = 'GO_BLEND_OUT'
    trim = layout.row(align=True)
    trim.operator('b4ml.contact', text='Set Start').operation = 'SET_START'
    trim.operator('b4ml.contact', text='Set End').operation = 'SET_END'


def _contact_review_counts(obj) -> dict:
    """Delegate to ui._contact_review_counts; fallback to zeros."""
    try:
        from b4artists_ml import ui as _ui
        return _ui._contact_review_counts(obj)
    except Exception:
        return {'PROPOSED': 0, 'ACCEPTED': 0, 'REJECTED': 0}


# Body pose helpers — .enabled parameter removed; operator poll handles gating.
def _draw_body_target_reset(row, name: str) -> None:
    """ui.py:975-979; cell.enabled dropped."""
    op = row.row(align=True).operator('b4ml.body', text='Reset')
    op.operation = 'RESET_TARGET'; op.target_name = name


def _draw_body_pole_align(row, name: str) -> None:
    """ui.py:982-986; cell.enabled dropped."""
    op = row.row(align=True).operator('b4ml.body', text='Align Bend')
    op.operation = 'ALIGN_POLE'; op.target_name = name


def _draw_body_pole_flip(row, name: str) -> None:
    """ui.py:989-993; cell.enabled dropped."""
    op = row.row(align=True).operator('b4ml.body', text='Flip Side')
    op.operation = 'FLIP_POLE'; op.target_name = name


def _draw_body_pole_distance(row, item) -> None:
    """ui.py:996-1001; cell.enabled dropped."""
    cell = row.row(align=True)
    cell.prop(item, 'pole_distance', text='')
    op = cell.operator('b4ml.body', text='Set Distance')
    op.operation = 'SET_POLE_DISTANCE'; op.target_name = item.name


def _draw_body_pole_status(layout, obj, name: str) -> None:
    """ui.py:1003-1011; no .enabled."""
    try:
        from b4artists_ml import body_preview as _bp
        status = _bp.pole_bend_status(obj, name)
        layout.label(text='Current: ' + status['relation'] + ' (' +
                     format(math.degrees(status['error_radians']), '.1f') + ' deg)')
    except Exception:
        pass


def _draw_body_mirror(row, direction: str, text: str) -> None:
    """ui.py:1013-1016; no .enabled."""
    op = row.operator('b4ml.body', text=text)
    op.operation = 'MIRROR_TARGETS'; op.mirror_direction = direction


def _draw_quadruped_mirror(row, direction: str, text: str) -> None:
    """ui.py:1019-1023; no .enabled."""
    op = row.operator('b4ml.quadruped_pose', text=text)
    op.operation = 'MIRROR_TARGETS'; op.mirror_direction = direction


def _quadruped_target_ui_label(name: str) -> str:
    """ui.py:1034-1035."""
    return _QUADRUPED_POLE_UI_LABELS.get(name, name)


# ---------------------------------------------------------------------------
# Shared subpanel attrs
# ---------------------------------------------------------------------------
_SP_ATTRS: dict = {
    'bl_space_type': 'VIEW_3D',
    'bl_region_type': 'UI',
    'bl_category': 'B4Artists ML',
    'bl_parent_id': 'B4ML_PT_advanced',
    'bl_options': {'DEFAULT_CLOSED'},
}

# Subpanels whose primary Solve action has been promoted to the Polish stage
# (packets polish-2, register-1, dedup-1).  Each class is kept with advanced
# options only; the primary action_row and prerequisite label were removed.
PROMOTED_TO_POLISH = ('contacts', 'airborne', 'cleanup', 'secondary')


# ---------------------------------------------------------------------------
# Parent panel
# ---------------------------------------------------------------------------

class B4ML_PT_advanced(_Panel):
    """Advanced tools panel — parent for all advanced subpanels.

    Plan §3 "Advanced"; Contract — all stages.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Advanced'
    bl_order = 9
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text='Diagnostics, solvers, and contacts.', icon='TOOL_SETTINGS')


# ---------------------------------------------------------------------------
# Subpanel: Rig Mapping
# ---------------------------------------------------------------------------

class B4ML_PT_adv_rig_mapping(_Panel):
    """Rig diagnostics and manual mapping corrections.

    Plan §3 "Advanced ▸ Rig Mapping"; Contract state MAPPED+.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Rig Mapping'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text=copy_.PREREQ['rig_mapping'])
        state = rig.b4ml
        try:
            from b4artists_ml import rig_mapping as _rm
            from b4artists_ml import rig_diagnostics as _rd
            profile, correction_rows, correction_error = _rm.status(rig)
        except Exception:
            layout.label(text='Rig mapping module unavailable.', icon='ERROR')
            return
        layout.label(text=rig.name, icon='ARMATURE_DATA')
        layout.operator('b4ml.action',
                        text='Inspect / Refresh Rig Mapping').operation = 'INSPECT'
        try:
            report = _rd.decode(getattr(state, 'rig_diagnostics_report', ''))
        except Exception:
            report = None
        _draw_rig_diagnostics(layout, state, report)
        _draw_rig_mapping_editor(layout, rig, state, profile,
                                 correction_rows, correction_error)


# ---------------------------------------------------------------------------
# Subpanel: Assisted Pose
# ---------------------------------------------------------------------------

class B4ML_PT_adv_assisted_pose(_Panel):
    """Humanoid whole-body pose and geometric IK-to-FK solver.

    Plan §3 "Advanced ▸ Assisted Pose"; Contract states MAPPED+.
    Ports B4ML_PT_main.draw L2625-2757.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Assisted Pose'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text=copy_.PREREQ['assisted_pose'])
        state = rig.b4ml

        try:
            from b4artists_ml import rig_mapping as _rm
            profile, _, _ = _rm.status(rig)
            humanoid = profile.family == 'humanoid'
        except Exception:
            humanoid = False

        # ── Humanoid Whole-Body Pose (b4ml.body) ─────────────────────────────
        # ui.py:2625-2719
        box = layout.box()
        box.label(text='Humanoid Whole-Body Pose')
        box.label(text='Experimental learned model')
        if getattr(state, 'body_payload', None):
            box.label(text='Move targets in Object Mode.')
            box.label(text='Use Live Solve or Solve Whole Body.')
            box.label(text='Enable Rotation to use axes.')
            box.label(text='Static balance is optional.')
            col = box.column()
            try:
                body_record = _json_object(getattr(state, 'body_payload', ''))
                controls_version = body_record.get('controls_version')
                extra = isinstance(controls_version, int) and controls_version >= 1
                chest_orientation = isinstance(controls_version, int) and controls_version >= 4
                neck_orientation = isinstance(controls_version, int) and controls_version >= 5
            except Exception:
                extra = False; chest_orientation = False; neck_orientation = False
            col.prop(state, 'show_body_targets',
                     icon='TRIA_DOWN' if getattr(state, 'show_body_targets', False) else 'TRIA_RIGHT')
            if getattr(state, 'show_body_targets', False):
                mirror = col.row(align=True)
                _draw_body_mirror(mirror, 'LEFT_TO_RIGHT', 'Mirror L to R')
                _draw_body_mirror(mirror, 'RIGHT_TO_LEFT', 'Mirror R to L')
                col.label(text='Semantic Pose Asset')
                asset = col.row(align=True)
                save_op = asset.operator('b4ml.body', text='Save Solved Pose')
                save_op.operation = 'SAVE_POSE_ASSET'
                apply_row = asset.row(align=True)
                use_op = apply_row.operator('b4ml.body', text='Apply Pose')
                use_op.operation = 'APPLY_POSE_ASSET'
                for item in getattr(state, 'body_targets', []):
                    row = col.row(align=True)
                    position = row.row()
                    balance = getattr(state, 'body_balance', False)
                    balance_strength = getattr(state, 'body_balance_strength', 0)
                    free_pelvis = getattr(state, 'body_balance_free_pelvis', False)
                    if item.name == 'Pelvis' and balance and balance_strength > 0 and free_pelvis:
                        position.label(text='Pelvis position: free')
                    else:
                        position.prop(item, 'enabled', text=item.name)
                    try:
                        from b4artists_ml import body_preview as _bp
                        supports_orient = (extra
                                           and _bp.target_supports_orientation(item.name)
                                           and (item.name != 'Chest' or chest_orientation)
                                           and (item.name != 'Neck' or neck_orientation))
                    except Exception:
                        supports_orient = False
                    if supports_orient:
                        row.prop(item, 'use_orientation', text='Rot')
                    elif item.name in {'Chest', 'Neck'}:
                        row.label(text='Restart for rotation')
                    _draw_body_target_reset(row, item.name)
                    try:
                        from b4artists_ml import body_preview as _bp2
                        supports_pole = extra and item.pole and _bp2.target_supports_pole(item.name)
                    except Exception:
                        supports_pole = False
                    if supports_pole:
                        pole_row = col.row(align=True)
                        pole_row.prop(item, 'use_pole',
                                      text='Elbow Direction' if item.name.startswith('Hand')
                                      else 'Knee Direction')
                        pole_actions = col.row(align=True)
                        _draw_body_pole_align(pole_actions, item.name)
                        _draw_body_pole_flip(pole_actions, item.name)
                        pole_distance = col.row(align=True)
                        _draw_body_pole_distance(pole_distance, item)
                        _draw_body_pole_status(col, rig, item.name)
            if not extra:
                box.label(text='Restart for rotation/poles.')
            col.prop(state, 'show_body_limits',
                     icon='TRIA_DOWN' if getattr(state, 'show_body_limits', False) else 'TRIA_RIGHT')
            if getattr(state, 'show_body_limits', False):
                col.label(text='Rotation limits')
                col.label(text='Opt-in animation estimates; tune per character.')
                preset_row = col.row(align=True)
                preset_row.prop(state, 'body_limit_preset', text='')
                preset_row.operator('b4ml.body',
                                    text='Apply to Mapped Controls').operation = 'APPLY_LIMIT_PRESET'
                col.prop_search(state, 'body_limit_control', state, 'body_limits', text='Control')
                item = getattr(state, 'body_limits', {}).get(
                    getattr(state, 'body_limit_control', ''))
                if item is not None:
                    limits_box = col.box()
                    limits_box.prop(item, 'enabled', text='Limit This Control')
                    limits_box.label(text='Source: ' + item.preset_provenance)
                    if item.enabled:
                        if item.joint_available:
                            limits_box.prop(item, 'space')
                        else:
                            limits_box.label(text='Control space only')
                        limits_box.prop(item, 'swing')
                        limits_box.prop(item, 'twist_min')
                        limits_box.prop(item, 'twist_max')
                        limits_box.prop(item, 'use_bend_plane')
                        if item.use_bend_plane:
                            limits_box.prop(item, 'bend_axis')
                            limits_box.operator(
                                'b4ml.body',
                                text='Use Current Bend as Forward').operation = 'CALIBRATE_BEND'
                            limits_box.prop(item, 'bend_min')
                            limits_box.prop(item, 'bend_max')
                            limits_box.prop(item, 'bend_sideways')
                col.label(text=f'{sum(i.enabled for i in getattr(state, "body_limits", []))} controls limited')
            col.prop(state, 'body_balance')
            if getattr(state, 'body_balance', False):
                for field in ('body_balance_strength', 'body_balance_inset',
                              'body_balance_free_pelvis', 'body_balance_dynamic'):
                    col.prop(state, field)
                if getattr(state, 'body_balance_dynamic', False):
                    col.prop(state, 'body_balance_velocity')
                    col.label(text='Procedural capture point; no force solve.')
                col.label(text='Authored mass + support')
                col.label(text='Support limbs stay pinned.')
            col.prop(state, 'body_strength')
            col.prop(state, 'body_influence')
            manual = col.row()
            manual.operator('b4ml.body_solve', text='Solve Whole Body')
            live = box.row()
            live.operator('b4ml.body_live',
                          text='Stop Live Solve' if getattr(state, 'body_live', False)
                          else 'Start Live Solve',
                          icon='PAUSE' if getattr(state, 'body_live', False) else 'PLAY')
            if getattr(state, 'body_balance', False):
                try:
                    metrics = _json_object(
                        getattr(state, 'body_payload', '')).get('metrics', {}).get('balance')
                    if metrics:
                        col.label(text='Last dynamic balance solve:'
                                  if metrics.get('dynamic')
                                  else 'Last static balance solve:')
                        col.label(text='COM error: ' + format(metrics['com_error'], '.3g'))
                        col.label(text='Margin: ' + format(metrics['after_margin'], '.5f'))
                except Exception:
                    pass
            col.operator('b4ml.body',
                         text='Keep as Pose Anchor', icon='CHECKMARK').operation = 'KEEP'
            col.operator('b4ml.body',
                         text='Cancel Preview', icon='X').operation = 'CANCEL'
            if getattr(state, 'body_running', False):
                box.label(text=getattr(state, 'body_progress', '') + ' (Esc to cancel)')
        else:
            row = box.row()
            row.operator('b4ml.body', text='Start Whole-Body Pose').operation = 'BEGIN'
            if not humanoid:
                box.label(text='Humanoid solver unavailable for this rig schema.')

        # ── Humanoid Assisted Pose — Geometric Solver (b4ml.pose) ────────────
        # ui.py:2720-2757
        box2 = layout.box()
        box2.label(text='Humanoid Assisted Pose — Geometric Solver')
        if getattr(state, 'posing_payload', None):
            box2.label(text='Move the sphere targets in Object Mode.')
            box2.label(text='IK input is matched to an editable FK pose.')
            for item in getattr(state, 'pose_targets', []):
                row = box2.row(align=True)
                row.prop(item, 'enabled', text=item.name)
                if item.pole:
                    row.prop(item, 'learn_bend', text='Learn Bend')
            if getattr(state, 'pose_metrics', None):
                try:
                    metrics = json.loads(state.pose_metrics)
                except (ValueError, TypeError):
                    metrics = {}
                for limb in metrics.get('limbs', []):
                    reason = limb.get('bend_source', 'authored pole')
                    if reason not in ('learned', 'authored pole'):
                        box2.label(text=f"{limb['limb']}: {reason}", icon='INFO')
            box2.prop(state, 'pose_offset')
            box2.prop(state, 'pose_strength')
            box2.prop(state, 'max_bend')
            if any(item.learn_bend for item in getattr(state, 'pose_targets', [])):
                box2.prop(state, 'learned_bend_strength')
            box2.operator('b4ml.pose', text='Solve Pose').operation = 'SOLVE'
            row = box2.row(align=True)
            row.operator('b4ml.pose', text='Keep as Pose Anchor',
                         icon='CHECKMARK').operation = 'KEEP'
            row.operator('b4ml.pose', text='Cancel', icon='X').operation = 'CANCEL'
        else:
            row = box2.row()
            row.operator('b4ml.pose', text='Start Assisted Pose').operation = 'BEGIN'


# ---------------------------------------------------------------------------
# Subpanel: Quadruped
# ---------------------------------------------------------------------------

class B4ML_PT_adv_quadruped(_Panel):
    """Quadruped whole-body pose and paw contacts.

    Plan §3 "Advanced ▸ Quadruped"; Contract states MAPPED+.
    Ports B4ML_PT_main.draw L2415-2623.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Quadruped'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text=copy_.PREREQ['quadruped'])
        state = rig.b4ml

        try:
            from b4artists_ml import rig_mapping as _rm
            profile, _, _ = _rm.status(rig)
            if profile.family != 'quadruped':
                layout.label(text='Quadruped rigs only.', icon='INFO')
                return
        except Exception:
            layout.label(text='Rig mapping unavailable.', icon='ERROR')
            return

        try:
            from b4artists_ml import quadruped_pose as _qp
            _qp_available = True
        except Exception:
            _qp_available = False

        # ui.py:2415-2514
        box = layout.box()
        box.label(text='Quadruped Whole-Body Pose')
        box.label(text='Generated Rigify cat, horse, or wolf')
        if getattr(state, 'quadruped_payload', None):
            quadruped_record = _json_object(getattr(state, 'quadruped_payload', ''))
            schema = quadruped_record.get('schema')
            supports_spine_follow = schema in {3, 4}
            supports_poles = schema == 4
            if _qp_available and getattr(state, 'quadruped_targets', {}).get('Head'):
                box.label(text=('Move body, paws, and poles; rotate Head.'
                                if supports_poles
                                else 'Move body/paws; rotate the location-locked Head.'))
            else:
                box.label(text='Move body/paws; recover this legacy preview.')
            for item in getattr(state, 'quadruped_targets', []):
                pole_targets = _qp.POLE_TARGETS if _qp_available else set()
                container = box.box() if item.name in pole_targets else box
                row = container.row(align=True)
                row.label(text=_quadruped_target_ui_label(item.name),
                          icon='EMPTY_ARROWS' if item.name in {'Body', 'Head'} else 'EMPTY_DATA')
                if item.name in pole_targets:
                    reset = row.operator('b4ml.quadruped_pose', text='Reset')
                    reset.operation = 'RESET_TARGET'; reset.target_name = item.name
                    pole_actions = container.row(align=True)
                    align = pole_actions.operator('b4ml.quadruped_pose', text='Align Bend')
                    align.operation = 'ALIGN_POLE'; align.target_name = item.name
                    flip = pole_actions.operator('b4ml.quadruped_pose', text='Flip Side')
                    flip.operation = 'FLIP_POLE'; flip.target_name = item.name
                    pole_distance = container.row(align=True)
                    pole_distance.prop(item, 'pole_distance', text='')
                    distance = pole_distance.operator('b4ml.quadruped_pose', text='Set Distance')
                    distance.operation = 'SET_POLE_DISTANCE'; distance.target_name = item.name
                else:
                    row.prop(item, 'use_orientation', text='Rotation')
                    reset = row.operator('b4ml.quadruped_pose', text='Reset')
                    reset.operation = 'RESET_TARGET'; reset.target_name = item.name
            if supports_spine_follow:
                box.prop(state, 'quadruped_spine_follow')
                box.row().prop(state, 'quadruped_neck_share')
            else:
                box.label(text='Legacy direct recovery; Spine Follow is unavailable.')
            mirror = box.row(align=True)
            _draw_quadruped_mirror(mirror, 'LEFT_TO_RIGHT', 'Mirror L to R')
            _draw_quadruped_mirror(mirror, 'RIGHT_TO_LEFT', 'Mirror R to L')
            box.operator('b4ml.quadruped_pose',
                         text='Solve Quadruped Pose').operation = 'SOLVE'
            assets = box.row(align=True)
            assets.operator('b4ml.quadruped_pose',
                            text='Save Solved Pose').operation = 'SAVE_POSE_ASSET'
            assets.operator('b4ml.quadruped_pose',
                            text='Apply Pose').operation = 'APPLY_POSE_ASSET'
            try:
                metrics = quadruped_record.get('metrics')
                if metrics:
                    box.label(text='Max paw error: ' + format(metrics['max_paw_error'], '.3g'))
                    if 'max_pole_error' in metrics:
                        box.label(text='Max pole error: ' + format(metrics['max_pole_error'], '.3g'))
                    if metrics.get('orientation_errors'):
                        box.label(text='Max rotation error: ' +
                                  format(math.degrees(metrics['max_orientation_error']), '.3g') +
                                  ' deg')
                    distribution = metrics.get('spine_distribution')
                    if distribution and distribution.get('active'):
                        box.label(text='Spine follow: ' +
                                  format(distribution['follow'] * 100, '.0f') +
                                  '%; Neck share ' +
                                  format(distribution['neck_share'] * 100, '.0f') + '%')
            except (ValueError, KeyError, TypeError, AttributeError):
                pass
            row = box.row(align=True)
            row.operator('b4ml.quadruped_pose',
                         text='Keep as Pose Anchor', icon='CHECKMARK').operation = 'KEEP'
            row.operator('b4ml.quadruped_pose',
                         text='Cancel', icon='X').operation = 'CANCEL'
        else:
            box.prop(state, 'quadruped_spine_follow')
            box.row().prop(state, 'quadruped_neck_share')
            box.prop(state, 'quadruped_use_poles')
            if getattr(state, 'quadruped_use_poles', False):
                try:
                    if _qp_available:
                        pole_modes = _qp.pole_mode_values(rig)
                        if not all(abs(v - 1.0) <= 1e-7 for v in pole_modes.values()):
                            box.label(text='Pole Vectors need pose-preserving matching.',
                                      icon='INFO')
                            box.row().operator('b4ml.quadruped_pose',
                                               text='Match + Enable All Poles',
                                               icon='FORCE_MAGNETIC').operation = 'MATCH_POLES'
                except (ValueError, KeyError, TypeError) as exc:
                    box.label(text=str(exc), icon='ERROR')
            row = box.row()
            row.operator('b4ml.quadruped_pose',
                         text='Start Quadruped Pose').operation = 'BEGIN'
            if not (getattr(profile, 'name', '').startswith('Rigify Generated Quadruped')):
                box.label(text='Generate this Rigify metarig to use paw and pole posing.')
        box.label(text='Position, rotation and procedural spine follow; no learned gait model.')

        # ── Quadruped Paw Contacts (ui.py:2516-2623) ─────────────────────────
        contacts_col = layout.column()
        contacts_col.prop(
            state, 'show_quadruped_contacts',
            icon='TRIA_DOWN' if getattr(state, 'show_quadruped_contacts', False) else 'TRIA_RIGHT',
            emboss=False)
        if getattr(state, 'show_quadruped_contacts', False):
            contacts_col.label(text='Review suggestions or capture paw holds.')
            contacts_col.label(text='Priority poses stay unchanged.')
            col = contacts_col.column()
            col.prop(state, 'contact_surface')
            if state.contact_surface is None:
                col.prop(state, 'support_plane_point')
                col.prop(state, 'support_plane_normal')
            for field in ('contact_suggest_distance', 'contact_suggest_speed',
                          'contact_suggest_min_frames', 'contact_suggest_gap_frames'):
                col.prop(state, field)
            col.label(text='Thresholds use body-to-paw distance.')
            col.operator('b4ml.contact_suggest', text='Suggest Paw Contacts', icon='VIEWZOOM')
            col.prop(state, 'show_contact_overlay')
            col.row().prop(state, 'show_all_contact_overlays')
            review_counts = _contact_review_counts(rig)
            col.label(text=(f'{review_counts["PROPOSED"]} proposed | '
                            f'{review_counts["ACCEPTED"]} accepted | '
                            f'{review_counts["REJECTED"]} rejected'))
            if review_counts['PROPOSED']:
                navigate = col.row(align=True)
                navigate.operator('b4ml.contact', text='Previous Proposed',
                                  icon='TRIA_LEFT').operation = 'PREVIOUS_PROPOSED'
                navigate.operator('b4ml.contact', text='Next Proposed',
                                  icon='TRIA_RIGHT').operation = 'NEXT_PROPOSED'
                bulk = col.row(align=True)
                bulk.operator('b4ml.contact', text='Accept All Proposed',
                              icon='CHECKMARK').operation = 'ACCEPT_ALL'
                bulk.operator('b4ml.contact', text='Reject All Proposed',
                              icon='X').operation = 'REJECT_ALL'
            col.prop(state, 'quadruped_contact_limb')
            col.prop(state, 'show_contact_details')
            if getattr(state, 'show_contact_details', False):
                col.prop(state, 'contact_offset', text='Offset from Paw Tip')
            col.operator('b4ml.contact',
                         text='Capture Paw Contact Here').operation = 'CAPTURE'
            try:
                from b4artists_ml import quadruped_contacts as _qc
                quad_contacts = [item for item in getattr(state, 'contacts', [])
                                 if item.limb in _qc.LIMBS]
            except Exception:
                quad_contacts = []
            if quad_contacts:
                col.prop(state, 'contact_index')
                if 0 <= getattr(state, 'contact_index', -1) < len(
                        getattr(state, 'contacts', [])):
                    item = state.contacts[state.contact_index]
                    try:
                        from b4artists_ml import quadruped_contacts as _qc2
                        in_quad = item.limb in _qc2.LIMBS
                    except Exception:
                        in_quad = True
                    if in_quad:
                        col.label(text=item.name)
                        col.prop(item, 'enabled')
                        col.label(text='Review: ' + item.review_state.title())
                        if item.reason:
                            col.label(text=item.reason)
                        if item.review_state == 'PROPOSED':
                            col.label(text='Score: ' + format(item.confidence, '.2f'))
                            col.label(text=item.provenance)
                            review = col.row(align=True)
                            review.operator('b4ml.contact',
                                            text='Accept').operation = 'ACCEPT'
                            review.operator('b4ml.contact',
                                            text='Reject').operation = 'REJECT'
                        for field in ('start', 'end'):
                            col.prop(item, field)
                        col.prop(item, 'asymmetric_blend')
                        for field in (('blend_in', 'blend_out')
                                      if item.asymmetric_blend else ('blend',)):
                            col.prop(item, field)
                        for field in ('strength', 'lock_rotation'):
                            col.prop(item, field)
                        try:
                            from b4artists_ml import contact_visualization as _cv
                            from b4artists_ml import posing as _posing
                            timing = _cv.timing(item, _posing._frame(context.scene))
                            col.label(text=f"Now: {timing['phase']} | "
                                      f"{timing['influence'] * 100:.0f}% influence")
                        except ValueError:
                            col.label(text='Now: invalid contact timing', icon='ERROR')
                        except Exception:
                            pass
                        _draw_contact_interval_controls(col, state)
                        if getattr(state, 'show_contact_details', False):
                            for field in ('point', 'offset'):
                                col.prop(item, field)
                        col.operator('b4ml.contact',
                                     text='Remove Paw Contact').operation = 'REMOVE'
            header.action_row(contacts_col, st, 'polish.contacts', 'b4ml.contact_solve',
                              text='Preview Four-Paw Correction')
            if (getattr(state, 'contact_input', None)
                    and getattr(state, 'contact_output', None) == getattr(
                        state, 'candidate_action', None)):
                col.operator('b4ml.contact',
                             text='Restore Before Paw Contacts').operation = 'RESET'
            if getattr(state, 'contact_running', False):
                contacts_col.label(text=getattr(state, 'contact_progress', '') +
                                   ' (Esc to cancel)')
            if getattr(state, 'contact_suggest_running', False):
                contacts_col.label(text=getattr(state, 'contact_suggest_progress', '') +
                                   ' (Esc to cancel)')
            try:
                metrics = json.loads(getattr(state, 'contact_metrics', '{}'))
                if metrics.get('paw_drift') is not None or True:
                    drift_after = metrics.get('contact_drift_after')
                    drift_before = metrics.get('contact_drift_before')
                    if drift_before is not None and drift_after is not None:
                        contacts_col.label(text='Paw drift: ' +
                                           format(drift_before, '.3g') + ' -> ' +
                                           format(drift_after, '.3g'))
            except (ValueError, KeyError, TypeError):
                pass
            phase_row = col.row()
            phase_row.operator('b4ml.quadruped_gait',
                               text='Analyze Gait Phases', icon='TIME').operation = 'ANALYZE'
            if getattr(state, 'quadruped_gait_report', None):
                try:
                    from b4artists_ml import quadruped_gait as _qg
                    gait = _qg.display_report(rig)
                    index = min(max(int(getattr(state, 'quadruped_gait_index', 0)), 0),
                                len(gait['phases']) - 1)
                    phase = gait['phases'][index]
                    contacts_col.label(
                        text=f"Phase {index + 1}/{len(gait['phases'])}: {phase['label']}")
                    contacts_col.label(
                        text=f"Frames {phase['start']:g} to {phase['end']:g}")
                    paws = ', '.join(v.replace('-', ' ') for v in phase['support_limbs'])
                    contacts_col.label(text='Support: ' + (paws if paws else 'none'))
                    contacts_col.label(text='Navigation revalidates the preview action.')
                    navigate = col.row(align=True)
                    navigate.operator('b4ml.quadruped_gait', text='Previous Phase',
                                      icon='TRIA_LEFT').operation = 'PREVIOUS'
                    navigate.operator('b4ml.quadruped_gait', text='Next Phase',
                                      icon='TRIA_RIGHT').operation = 'NEXT'
                    col.operator('b4ml.quadruped_gait', text='Clear Phase Report',
                                 icon='X').operation = 'CLEAR'
                except ValueError as exc:
                    _draw_wrapped(contacts_col, str(exc), icon='ERROR')
                    col.operator('b4ml.quadruped_gait', text='Clear Stale Report',
                                 icon='X').operation = 'CLEAR'
                except Exception:
                    pass
            contacts_col.label(
                text='Procedural contact-phase review; animation stays unchanged.')


# ---------------------------------------------------------------------------
# Subpanel: Center of Mass
# ---------------------------------------------------------------------------

class B4ML_PT_adv_center_of_mass(_Panel):
    """Artist-authored mass estimate and static support analysis.

    Plan §3 "Advanced ▸ Center of Mass"; Contract states MAPPED+.
    Ports B4ML_PT_main.draw L2051-2081 (show_support block).
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Center of Mass'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text=copy_.PREREQ['center_of_mass'])
        state = rig.b4ml
        col = layout.column()
        col.label(text='Artist-authored mass estimate')
        if not getattr(state, 'mass_segments', []):
            col.operator('b4ml.support', text='Initialize Mass Model').operation = 'INITIALIZE'
        else:
            col.prop(state, 'show_mass_settings',
                     icon='TRIA_DOWN' if getattr(state, 'show_mass_settings', False) else 'TRIA_RIGHT',
                     emboss=False)
            if getattr(state, 'show_mass_settings', False):
                col.prop(state, 'mass_index')
                mass_segments = getattr(state, 'mass_segments', [])
                mass_index = getattr(state, 'mass_index', 0)
                if mass_index < len(mass_segments):
                    segment = mass_segments[mass_index]
                    col.label(text=segment.name)
                    col.prop(segment, 'weight')
                    col.prop(segment, 'fraction')
                    col.prop(segment, 'inertia_radius')
            col.prop(state, 'show_support_settings',
                     icon='TRIA_DOWN' if getattr(state, 'show_support_settings', False) else 'TRIA_RIGHT',
                     emboss=False)
            if getattr(state, 'show_support_settings', False):
                for field in ('support_plane_point', 'support_plane_normal',
                              'support_tolerance', 'support_rotation_tolerance'):
                    col.prop(state, field)
            col.label(text='Patches: Animation Contacts')
            col.operator('b4ml.support', text='Analyze Current Pose').operation = 'ANALYZE'
        if getattr(state, 'support_report', None):
            try:
                report = json.loads(state.support_report)
                layout.label(text='Snapshot at frame ' + format(report['frame'], '.3f'))
                layout.label(text=report['status'].replace('_', ' ').title())
                layout.label(text='World COM:')  # original: 'World COM (internal units):' — 'internal units' is a forbidden term
                for axis, value in zip('XYZ', report['com']):
                    layout.label(text=axis + ': ' + format(value, '.5f'))
                if report['margin'] is not None:
                    layout.label(text='Margin: ' + format(report['margin'], '.5f'))
                layout.label(text='Contacts: ' + str(len(report['contacts'])) +
                             ' in / ' + str(len(report['excluded_contacts'])) + ' excluded')
                for item in report['excluded_contacts']:
                    layout.label(text=item['limb'] + ': ' + item['reason'])
            except (ValueError, KeyError, TypeError):
                layout.label(text='Reanalyze to replace an unreadable snapshot.')
        layout.label(text='Reanalyze after edits.')
        layout.label(text='Static support estimate')


# ---------------------------------------------------------------------------
# Subpanel: Contacts
# ---------------------------------------------------------------------------

class B4ML_PT_adv_contacts(_Panel):
    """Humanoid geometric contact correction.

    Plan §3 "Advanced ▸ Contacts"; Contract states PREVIEW_ACTIVE, KEPT.
    Ports B4ML_PT_main.draw L2139-2219 (show_contacts block).
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Contacts'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text='Primary action: Polish stage', icon='INFO')
        state = rig.b4ml
        layout.label(text='Humanoid geometric contact correction')
        layout.label(text='Priority poses stay unchanged.')
        col = layout.column()
        col.label(text='Provisional foot-contact scan')
        col.prop(state, 'contact_surface')
        for field in ('contact_suggest_distance', 'contact_suggest_speed',
                      'contact_suggest_min_frames', 'contact_suggest_gap_frames'):
            col.prop(state, field)
        scan = col.row()
        scan.operator('b4ml.contact_suggest', text='Suggest Foot Contacts', icon='VIEWZOOM')
        if state.contact_surface is None:
            col.label(text='Uses the authored support plane.')
        col.label(text='Suggestions never change animation.')
        col.prop(state, 'show_contact_overlay')
        col.row().prop(state, 'show_all_contact_overlays')
        review_counts = _contact_review_counts(rig)
        col.label(text=(f'{review_counts["PROPOSED"]} proposed | '
                        f'{review_counts["ACCEPTED"]} accepted | '
                        f'{review_counts["REJECTED"]} rejected'))
        if review_counts['PROPOSED']:
            navigate = col.row(align=True)
            navigate.operator('b4ml.contact', text='Previous Proposed',
                              icon='TRIA_LEFT').operation = 'PREVIOUS_PROPOSED'
            navigate.operator('b4ml.contact', text='Next Proposed',
                              icon='TRIA_RIGHT').operation = 'NEXT_PROPOSED'
            bulk = col.row(align=True)
            bulk.operator('b4ml.contact', text='Accept All Proposed',
                          icon='CHECKMARK').operation = 'ACCEPT_ALL'
            bulk.operator('b4ml.contact', text='Reject All Proposed',
                          icon='X').operation = 'REJECT_ALL'
        col.prop(state, 'contact_limb')
        col.prop(state, 'show_contact_details')
        if getattr(state, 'show_contact_details', False):
            col.prop(state, 'contact_offset')
        col.operator('b4ml.contact', text='Capture Contact Here').operation = 'CAPTURE'
        if getattr(state, 'contacts', []):
            col.prop(state, 'contact_index')
            contacts = getattr(state, 'contacts', [])
            contact_index = getattr(state, 'contact_index', -1)
            if 0 <= contact_index < len(contacts):
                item = contacts[contact_index]
                col.label(text=item.name)
                col.prop(item, 'enabled')
                col.label(text='Review: ' + item.review_state.title())
                if item.reason:
                    col.label(text=item.reason)
                if item.review_state == 'PROPOSED':
                    col.prop(item, 'confidence', slider=True)
                    col.label(text=item.provenance)
                    review = col.row(align=True)
                    review.operator('b4ml.contact', text='Accept').operation = 'ACCEPT'
                    review.operator('b4ml.contact', text='Reject').operation = 'REJECT'
                elif item.review_state == 'REJECTED':
                    col.label(text='Excluded from correction')
                for field in ('start', 'end'):
                    col.prop(item, field)
                col.prop(item, 'asymmetric_blend')
                for field in (('blend_in', 'blend_out')
                              if item.asymmetric_blend else ('blend',)):
                    col.prop(item, field)
                for field in ('strength', 'lock_rotation'):
                    col.prop(item, field)
                try:
                    from b4artists_ml import contact_visualization as _cv
                    from b4artists_ml import posing as _posing
                    timing = _cv.timing(item, _posing._frame(context.scene))
                    col.label(text=f"Now: {timing['phase']} | "
                              f"{timing['influence'] * 100:.0f}% influence")
                except ValueError:
                    col.label(text='Now: invalid contact timing', icon='ERROR')
                except Exception:
                    pass
                _draw_contact_interval_controls(col, state)
                if getattr(state, 'show_contact_details', False):
                    for field in ('point', 'offset'):
                        col.prop(item, field)
                if item.limb in _HUMANOID_CONTACT_LIMBS and item.limb.startswith('arm-'):
                    col.label(text='Hand-to-Prop Hold')
                    col.prop(item, 'prop_object')
                    prop_row = col.row(align=True)
                    prop_row.row().operator('b4ml.contact', text='Bind to Prop',
                                           icon='CONSTRAINT').operation = 'BIND_PROP'
                    prop_row.row().operator('b4ml.contact', text='Clear',
                                           icon='X').operation = 'CLEAR_PROP'
                    if item.prop_bound and item.prop_target:
                        col.label(text='Following ' + item.prop_target.name)
                elif item.limb in _HUMANOID_CONTACT_LIMBS and item.limb.startswith('leg-'):
                    col.label(text='Foot-to-Moving-Platform')
                    col.prop(item, 'prop_object', text='Surface')
                    surface_row = col.row(align=True)
                    surface_row.row().operator('b4ml.contact', text='Bind to Platform',
                                              icon='CONSTRAINT').operation = 'BIND_SURFACE'
                    surface_row.row().operator('b4ml.contact', text='Clear',
                                              icon='X').operation = 'CLEAR_SURFACE'
                    if item.prop_bound and item.prop_target:
                        col.label(text='Following ' + item.prop_target.name)
                support_controls = col.column()
                support_controls.prop(item, 'use_support')
                if item.use_support:
                    for field in ('support_width', 'support_length', 'support_heading'):
                        support_controls.prop(item, field)
                if getattr(state, 'show_contact_details', False):
                    for field in ('point', 'offset'):
                        col.prop(item, field)
                    if item.prop_bound:
                        col.prop(item, 'prop_point')
                        col.prop(item, 'prop_rotation')
                col.operator('b4ml.contact', text='Remove Contact').operation = 'REMOVE'
        if (getattr(state, 'contact_input', None)
                and getattr(state, 'contact_output', None) == getattr(
                    state, 'candidate_action', None)):
            col.operator('b4ml.contact',
                         text='Restore Before Contacts').operation = 'RESET'
        if getattr(state, 'contact_running', False):
            layout.label(text=getattr(state, 'contact_progress', ''))
        if getattr(state, 'contact_suggest_running', False):
            layout.label(text=getattr(state, 'contact_suggest_progress', '') +
                         ' (Esc to cancel)')
        layout.label(text='No self-collision solve yet.')


# ---------------------------------------------------------------------------
# Subpanel: Airborne
# ---------------------------------------------------------------------------

class B4ML_PT_adv_airborne(_Panel):
    """COM gravity arc for airborne intervals.

    Plan §3 "Advanced ▸ Airborne"; Contract states PREVIEW_ACTIVE, KEPT.
    Ports B4ML_PT_main.draw L2083-2137 (show_flights block).
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Airborne'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text='Primary action: Polish stage', icon='INFO')
        state = rig.b4ml

        try:
            from b4artists_ml import rig_mapping as _rm
            profile, _, _ = _rm.status(rig)
            humanoid = profile.family == 'humanoid'
        except Exception:
            humanoid = False

        layout.label(text='Gravity arc for COM')
        layout.label(text='Use priority pose frames')
        col = layout.column()
        if not getattr(state, 'mass_segments', []):
            col.operator('b4ml.support', text='Initialize Mass Model').operation = 'INITIALIZE'
        col.operator('b4ml.flight', text='Add Airborne Interval').operation = 'ADD'
        flights = getattr(state, 'flights', [])
        if flights:
            col.prop(state, 'flight_index')
            flight_index = getattr(state, 'flight_index', 0)
            if 0 <= flight_index < len(flights):
                item = flights[flight_index]
                col.prop(item, 'enabled')
                col.prop(item, 'start', text='Takeoff')
                col.prop(item, 'end', text='Landing')
                col.prop(item, 'strength')
                if getattr(state, 'flight_backend', '') == 'NATIVE':
                    col.label(text='Transition frames')
                    col.prop(item, 'takeoff_blend', text='Before takeoff')
                    col.prop(item, 'landing_blend', text='After landing')
                    col.prop(item, 'match_acceleration')
                    col.label(text='Airborne rotation')
                    col.prop(item, 'angular_momentum_strength')
                    col.label(text='Landing support')
                    col.prop(item, 'contact_impulse_strength')
                    col.label(text='Static planar collision')
                    col.prop(item, 'collision_strength')
                    if item.collision_strength:
                        col.prop(item, 'collision_clearance')
                col.operator('b4ml.flight', text='Remove Interval').operation = 'REMOVE'
            col.prop(state, 'flight_backend')
        candidate = getattr(state, 'candidate_action', None)
        if (getattr(state, 'flight_input', None)
                and getattr(state, 'flight_output', None) == candidate):
            col.operator('b4ml.flight', text='Restore Before Flight').operation = 'RESET'
        if getattr(state, 'flight_running', False):
            layout.label(text=getattr(state, 'flight_progress', ''))
        if getattr(state, 'flight_metrics', None):
            try:
                report = json.loads(state.flight_metrics)
                layout.label(text='COM error (body units)')
                layout.label(text=format(report['max_after'], '.3g'))
                jumps = [r[key]['corrected']['jump']
                         for r in report['intervals']
                         for key in ('takeoff_velocity', 'landing_velocity')
                         if key in r]
                jumps.extend(r['after_jump'] for r in report.get('transitions', []))
                if jumps:
                    layout.label(text='Boundary speed jump')
                    layout.label(text=format(max(jumps), '.3g') + ' units/s (estimate)')
                acceleration = [r['after_acceleration_jump']
                                for r in report.get('transitions', [])
                                if r.get('match_acceleration')]
                if acceleration:
                    layout.label(text='Boundary acceleration jump')
                    layout.label(text=format(max(acceleration), '.3g') + ' units/s^2 (estimate)')
                angular = [r for r in report.get('intervals', [])
                           if r.get('angular_momentum')]
                if angular:
                    layout.label(text='Angular variation reduction')
                    layout.label(text=format(
                        max(r['angular_momentum']['improvement'] for r in angular) * 100,
                        '.1f') + '% (rigid-segment estimate)')
                collision = [r['collision_response']
                             for r in report.get('intervals', [])
                             if r.get('collision_response')]
                if collision:
                    layout.label(text='Planar penetration')
                    layout.label(text=format(
                        max(r['max_penetration_after'] for r in collision), '.3g') +
                        ' world units')
            except (ValueError, KeyError, TypeError):
                pass


# ---------------------------------------------------------------------------
# Subpanel: Cleanup
# ---------------------------------------------------------------------------

class B4ML_PT_adv_cleanup(_Panel):
    """Deterministic copied-curve cleanup.

    Plan §3 "Advanced ▸ Cleanup"; Contract states PREVIEW_ACTIVE, KEPT.
    Ports B4ML_PT_main.draw L2221-2254 (show_cleanup block).
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Cleanup'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text='Primary action: Polish stage', icon='INFO')
        state = rig.b4ml
        layout.label(text='Deterministic copied-curve cleanup')
        layout.label(text='Priority poses and accepted contacts stay exact.')
        col = layout.column()
        col.prop(state, 'cleanup_scope')
        col.prop(state, 'cleanup_smooth')
        smooth = col.column()
        smooth.prop(state, 'cleanup_strength')
        col.prop(state, 'cleanup_reduce')
        reduce = col.column()
        reduce.prop(state, 'cleanup_tolerance')
        if (getattr(state, 'cleanup_input', None)
                and getattr(state, 'cleanup_output', None) == getattr(
                    state, 'candidate_action', None)):
            col.operator('b4ml.cleanup', text='Restore Input').operation = 'RESET'
        if getattr(state, 'cleanup_running', False):
            layout.label(text=getattr(state, 'cleanup_progress', '') + ' (Esc to cancel)')
        if getattr(state, 'cleanup_metrics', None):
            try:
                report = json.loads(state.cleanup_metrics)
                layout.label(text=(str(report['keys_before']) + ' to ' +
                                   str(report['keys_after']) + ' keys; ' +
                                   str(report['keys_removed']) + ' removed'))
                layout.label(text=(str(report['curves_smoothed']) +
                                   ' curves smoothed; ' +
                                   str(len(report['cleaned_controls'])) + ' controls'))
                if report['protected_contact_controls']:
                    layout.label(text=(str(len(report['protected_contact_controls'])) +
                                       ' contact controls protected'))
                if report.get('accepted_contacts'):
                    layout.label(text=(str(report['accepted_contacts']) +
                                       ' accepted contacts; ' +
                                       str(report['contact_samples']) + ' validation samples'))
                    layout.label(text=('Max contact drift: ' +
                                       format(report['max_contact_position_drift'], '.3g') +
                                       '; rotation ' +
                                       format(math.degrees(
                                           report['max_contact_rotation_drift_radians']), '.3g') +
                                       ' deg'))
                if report.get('reduction'):
                    layout.label(text='Max key error: ' +
                                 format(report['max_reduction_error'], '.3g'))
                layout.label(text=('Derivative jump: ' +
                                   format(report['max_scalar_derivative_jump_before'], '.3g') +
                                   ' to ' +
                                   format(report['max_scalar_derivative_jump_after'], '.3g')))
                if report['skipped_constrained_curves'] or report['skipped_unsupported_curves']:
                    layout.label(
                        text=(str(report['skipped_constrained_curves'] +
                                  report['skipped_unsupported_curves']) +
                              ' curves safely skipped'))
            except (ValueError, KeyError, TypeError):
                pass
        layout.label(text=copy_.PREREQ['cleanup'][1])


# ---------------------------------------------------------------------------
# Subpanel: Secondary Motion
# ---------------------------------------------------------------------------

class B4ML_PT_adv_secondary(_Panel):
    """Deterministic control physics — secondary motion.

    Plan §3 "Advanced ▸ Secondary Motion"; Contract states PREVIEW_ACTIVE, KEPT.
    Ports B4ML_PT_main.draw L2255-2413 (show_secondary block).
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Secondary Motion'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text='Primary action: Polish stage', icon='INFO')
        state = rig.b4ml
        layout.label(text='Deterministic control physics')
        layout.label(text='Select pose controls.')
        col = layout.column()
        col.prop(state, 'secondary_space', text='Space')
        row = col.row(align=True)
        row.prop(state, 'secondary_rotation')
        row.prop(state, 'secondary_location')
        col.prop(state, 'secondary_chain')
        chain = col.column()
        if getattr(state, 'secondary_chain', False) and getattr(state, 'secondary_space', '') == 'WORLD' and getattr(state, 'secondary_location', False):
            chain.label(text='World chain: assign a load to every control; no wind/impulse.',
                        icon='INFO')
        chain.prop(state, 'secondary_chain_direction', text='Grow From Active')
        chain.prop(state, 'secondary_chain_length', text='Maximum Controls')
        selector = chain.operator('b4ml.secondary_select_chain',
                                  text='Select Direct Chain', icon='BONE_DATA')
        selector.direction = getattr(state, 'secondary_chain_direction', 'CHILDREN')
        selector.max_controls = getattr(state, 'secondary_chain_length', 4)
        if getattr(state, 'secondary_selection_swap', None):
            chain.operator('b4ml.secondary_selection_swap',
                           text='Swap Previous Selection', icon='FILE_REFRESH')
        chain.prop(state, 'secondary_chain_propagation', text='Propagation')
        for field in ('secondary_frequency', 'secondary_damping', 'secondary_air_friction',
                      'secondary_strength', 'secondary_blend_frames'):
            col.prop(state, field)
        world = col.column()
        world.prop(state, 'secondary_gravity')
        world.prop(state, 'secondary_external_acceleration')
        world.prop(state, 'secondary_self_collision', text='Self-Collision')
        if getattr(state, 'secondary_self_collision', False):
            world.prop(state, 'secondary_self_collision_radius', text='Self Radius')
            world.label(text='Selected controls only; World space and Location required.')
        world.prop(state, 'secondary_wind_velocity')
        world.prop(state, 'secondary_impulse_velocity')
        impulse_frame = world.column()
        impulse_frame.prop(state, 'secondary_impulse_frame')
        world.prop(state, 'secondary_load_force')
        world.prop(state, 'secondary_load_mass')
        world.prop(state, 'secondary_load_offset')
        world.prop(state, 'secondary_load_inertia')
        try:
            from b4artists_ml import secondary_motion as _sm
            load_count = _sm.control_load_count(rig)
        except Exception:
            load_count = 0
        recall = world.operator('b4ml.secondary_control_load',
                                text='Load From Active', icon='IMPORT')
        recall.operation = 'LOAD_ACTIVE'
        assign = world.operator('b4ml.secondary_control_load',
                                text='Assign Load', icon='ADD')
        assign.operation = 'ASSIGN'
        clear = world.operator('b4ml.secondary_control_load',
                               text='Clear Load', icon='X')
        clear.operation = 'CLEAR'
        world.label(text=('Invalid stored control loads' if load_count is None else
                          str(load_count) + ' assigned control load' +
                          ('s' if load_count != 1 else '')))
        if load_count is None:
            reset = world.operator('b4ml.secondary_control_load',
                                   text='Clear Invalid Assignments', icon='TRASH')
            reset.operation = 'CLEAR_ALL'
        world.prop(state, 'secondary_collision')
        if getattr(state, 'secondary_collision', False):
            world.prop(state, 'secondary_collision_shape', text='Shape')
            shape = getattr(state, 'secondary_collision_shape', 'PLANE')
            if shape in {'SPHERE', 'COMPOUND'}:
                if shape == 'COMPOUND':
                    world.prop(state, 'contact_surface', text='Support Surface')
                    world.label(
                        text='Static support surface is resolved before the static sphere set.')
                    world.prop(state, 'secondary_collision_compound_capsule',
                               text='Also Include Capsule')
                    world.prop(state, 'secondary_collision_compound_mesh',
                               text='Also Include Static Closed Mesh')
                world.prop(state, 'secondary_sphere_collider',
                           text='Sphere Center / Bounds Source')
                world.prop(state, 'secondary_sphere_radius', text='New Radius')
                fit = world.operator('b4ml.secondary_sphere',
                                     text='Fit New Radius from Bounds', icon='FULLSCREEN_ENTER')
                fit.operation = 'FIT'; fit.index = -1
                proxy = world.operator('b4ml.secondary_sphere',
                                       text='Create Bounds Proxy', icon='OUTLINER_OB_EMPTY')
                proxy.operation = 'PROXY'
                world.prop(state, 'secondary_sphere_moving', text='Follow Center Animation')
                world.prop(state, 'secondary_sphere_scaling', text='Follow Radius Scale')
                if shape == 'SPHERE':
                    world.prop(state, 'secondary_collision_continuous',
                               text='Continuous-Time Sweep')
                    world.label(text=(
                        'One sphere uses a bounded analytic relative-motion sweep.'
                        if getattr(state, 'secondary_collision_continuous', False)
                        else 'Sphere sets use bounded projection at solver samples.'))
                else:
                    world.label(text=(
                        'Compound mode permits one moving sphere plus the support surface, '
                        'optionally after static spheres, two moving spheres plus the support '
                        'surface, or one moving capsule after static spheres; other '
                        'moving-collider mixtures remain rejected.'))
                add = world.operator('b4ml.secondary_sphere',
                                     text='Add Sphere to Set', icon='ADD')
                add.operation = 'ADD'
                secondary_spheres = getattr(state, 'secondary_spheres', [])
                if secondary_spheres:
                    moving_count = sum(bool(item.moving) for item in secondary_spheres)
                    world.label(text=(str(len(secondary_spheres)) + ' active sphere' +
                                      ('s' if len(secondary_spheres) != 1 else '')))
                    if moving_count:
                        world.label(text=str(moving_count) +
                                    ' following direct location animation')
                    for index, item in enumerate(secondary_spheres):
                        sphere = world.box()
                        sphere.prop(item, 'collider', text=str(index + 1) + ' Center')
                        sphere.prop(item, 'radius', text='Radius')
                        fit2 = sphere.operator('b4ml.secondary_sphere',
                                               text='Fit Radius from Bounds',
                                               icon='FULLSCREEN_ENTER')
                        fit2.operation = 'FIT'; fit2.index = index
                        sphere.prop(item, 'moving', text='Follow Animation')
                        sphere.prop(item, 'scaling', text='Follow Radius Scale')
                        remove = sphere.operator('b4ml.secondary_sphere',
                                                 text='Remove', icon='X')
                        remove.operation = 'REMOVE'; remove.index = index
                    clr = world.operator('b4ml.secondary_sphere',
                                         text='Clear Sphere Set', icon='TRASH')
                    clr.operation = 'CLEAR'
                else:
                    world.label(text='No set: uses New Sphere directly.')
                if (shape == 'COMPOUND'
                        and getattr(state, 'secondary_collision_compound_capsule', False)):
                    world.prop(state, 'secondary_capsule_start',
                               text='Capsule Start Endpoint')
                    world.prop(state, 'secondary_capsule_end',
                               text='Capsule End Endpoint')
                    world.prop(state, 'secondary_capsule_radius', text='Capsule Radius')
                    world.prop(state, 'secondary_capsule_moving',
                               text='Follow Endpoint Animation')
                    world.prop(state, 'secondary_capsule_scaling',
                               text='Follow Radius Scale')
                    world.prop(state, 'secondary_collision_continuous',
                               text='Continuous-Time Sweep')
                    world.label(text=(
                        'One moving capsule plus the support and static sphere set uses '
                        'bounded relative-motion response; mixed moving colliders and '
                        'compound meshes are rejected.'
                        if getattr(state, 'secondary_capsule_moving', False)
                        else 'Static capsule only; enable endpoint animation for the '
                             'bounded moving-capsule compound slice.'))
                if (shape == 'COMPOUND'
                        and getattr(state, 'secondary_collision_compound_mesh', False)):
                    world.prop(state, 'secondary_collision_mesh', text='Closed Mesh')
                    if not getattr(state, 'secondary_collision_compound_capsule', False):
                        world.prop(state, 'secondary_collision_continuous',
                                   text='Continuous-Time Sweep (disable for compound mesh)')
                    world.label(
                        text='Static closed mesh only; deformation, object motion, '
                             'volume mode, and continuous sweep are rejected in this compound.')
            elif shape == 'CAPSULE':
                world.prop(state, 'secondary_capsule_start', text='Start Endpoint')
                world.prop(state, 'secondary_capsule_end', text='End Endpoint')
                world.prop(state, 'secondary_capsule_radius', text='Radius')
                world.prop(state, 'secondary_capsule_moving', text='Follow Endpoint Animation')
                world.prop(state, 'secondary_capsule_scaling', text='Follow Radius Scale')
                world.prop(state, 'secondary_collision_continuous', text='Continuous-Time Sweep')
                cap_moving = getattr(state, 'secondary_capsule_moving', False)
                cap_cont = getattr(state, 'secondary_collision_continuous', False)
                world.label(text=(
                    'Direct endpoint Actions with bounded interpolated sweep.'
                    if cap_moving and cap_cont else
                    'Direct endpoint Actions sampled at solver frames.'
                    if cap_moving else
                    'Static, unparented endpoints; sweep is a bounded static capsule crossing check.'
                    if cap_cont else
                    'Static, unparented endpoints only.'))
            elif shape in {'MESH', 'VOLUME'}:
                world.prop(state, 'secondary_collision_mesh', text='Triangle Mesh')
                world.prop(state, 'secondary_collision_mesh_deforming',
                           text='Follow Shape-Key Deformation')
                world.prop(state, 'secondary_collision_mesh_moving', text='Follow Object Motion')
                mesh_deforming = getattr(state, 'secondary_collision_mesh_deforming', False)
                if shape == 'VOLUME':
                    world.prop(state, 'secondary_collision_volume_radius',
                               text='Control Volume Radius')
                    world.label(text=(
                        'Closed mesh; finite spherical control volume; '
                        'direct shape-key Action sampled per frame.'
                        if mesh_deforming else
                        'Closed mesh; finite spherical control volume; static evaluated triangles.'))
                else:
                    world.label(text=(
                        'Unparented mesh; direct shape-key Action sampled per frame.'
                        if mesh_deforming else
                        'Static, unparented mesh without modifiers or animation.'))
                world.prop(state, 'secondary_collision_continuous', text='Continuous-Time Sweep')
                if getattr(state, 'secondary_collision_continuous', False):
                    world.label(text=(
                        'Closed shape-key mesh uses bounded interpolated sweep samples.'
                        if mesh_deforming else
                        'Catches segment crossings between solver samples.'))
            else:
                world.prop(state, 'contact_surface', text='Planar Surface')
                if state.contact_surface is None:
                    world.label(text='Uses the authored support plane.')
            world.prop(state, 'secondary_collision_clearance', text='Clearance')
            world.prop(state, 'secondary_restitution', text='Bounce')
            world.prop(state, 'secondary_surface_friction', text='Friction')
        if (getattr(state, 'secondary_input', None)
                and getattr(state, 'secondary_output', None) == getattr(
                    state, 'candidate_action', None)):
            col.operator('b4ml.secondary', text='Restore Input').operation = 'RESET'
        if getattr(state, 'secondary_running', False):
            layout.label(text=getattr(state, 'secondary_progress', '') + ' (Esc to cancel)')
        if getattr(state, 'secondary_metrics', None):
            try:
                report = json.loads(state.secondary_metrics)
                count = len(report['controls'])
                layout.label(text=(str(count) + ' control' +
                                   ('s' if count != 1 else '') + '; ' +
                                   report.get('space', 'LOCAL').title()))
                if report.get('chain'):
                    layout.label(text=str(report.get('chain_links', 0)) + ' coupled chain links')
                layout.label(text=(str(report['samples']) + ' samples; ' +
                                   str(report['curves']) + ' editable curves'))
                if report['rotation']:
                    layout.label(text='Max rotation: ' +
                                 format(math.degrees(report['max_rotation_correction_radians']),
                                        '.2f') + ' degrees')
                if report['location']:
                    layout.label(text='Max location: ' +
                                 format(report['max_location_correction'], '.4g'))
                if report.get('torque_controls'):
                    layout.label(text=(str(report['torque_controls']) + ' torque control' +
                                       ('s' if report['torque_controls'] != 1 else '') +
                                       '; max ' +
                                       format(report.get('max_control_torque', 0.), '.4g')))
                if report.get('collision'):
                    cc = report.get('collision_sphere_count', 0)
                    cl = ('support + ' + str(max(0, cc - 1)) + ' sphere colliders'
                          if report.get('collision_compound') else
                          str(cc) + ' sphere colliders' if cc > 1 else
                          report.get('collision_shape', 'PLANE').title() + ' collider')
                    layout.label(text=(cl + '; ' +
                                       str(report.get('collision_samples', 0)) + ' contacts'))
                    layout.label(text='Final penetration ' +
                                 format(report.get('max_penetration_after', 0.), '.3g'))
            except (ValueError, KeyError, TypeError):
                pass
        layout.label(text='Priority poses remain exact; no learned model used.')


# ---------------------------------------------------------------------------
# Subpanel: Saved Results
# ---------------------------------------------------------------------------

class B4ML_PT_adv_saved_results(_Panel):
    """Previously kept motion results.

    Plan §3 "Advanced ▸ Saved Results"; Contract state KEPT+.
    Ports B4ML_PT_main.draw L2042-2046.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Saved Results'
    bl_parent_id = 'B4ML_PT_advanced'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return
        layout.label(text=copy_.PREREQ['saved_results'])
        try:
            from b4artists_ml import workflow as _wf
            alternatives = _wf.motion_layer.results(rig)
        except Exception:
            alternatives = []
        if alternatives:
            for result in alternatives:
                layout.operator('b4ml.motion_result',
                                text=result.name).result_name = result.name
        else:
            layout.label(text='No saved results yet.', icon='INFO')


# ---------------------------------------------------------------------------
# CLASSES — parent first, then subpanels in packet order
# ---------------------------------------------------------------------------

CLASSES = (
    B4ML_PT_advanced,
    B4ML_PT_adv_rig_mapping,
    B4ML_PT_adv_assisted_pose,
    B4ML_PT_adv_quadruped,
    B4ML_PT_adv_center_of_mass,
    B4ML_PT_adv_contacts,
    B4ML_PT_adv_airborne,
    B4ML_PT_adv_cleanup,
    B4ML_PT_adv_secondary,
    B4ML_PT_adv_saved_results,
)
