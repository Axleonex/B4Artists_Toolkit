"""Viewport overlay for B4Artists ML posing sessions.

plan §4 items 1–4; contract §DESIGN PLAN palette + TYPE, §STATE MAP POSING states,
§BEHAVIORAL SUCCESS 3 and 4; spike items 6 and 7.

Verified source facts:
  body_preview.py:17-21  TARGETS_V1/V2/V3, TARGETS, POLE_JOINTS — label↔index mapping
  body_preview.py:143-144  posing._helper: Blender object name is 'B4ML Body <label>'
  body_preview.py:204-206  body_targets[i].name = label; .target = empty; .enabled = Pin
  body_preview.py:222      pole object name is 'B4ML Body <label> pole'
  body_solver.py:339,346   Session.points() → local joint array; .world_points(local) → world
  contact_visualization.py:22-27  _COLORS: 'ACCEPTED'/'PROPOSED'/'REJECTED' (3-tuple RGB)
  posing.py:143-144  _helper: object named 'B4ML ' + label; body label = 'Body <name>'
  ui.py:47  B4ML_PG_target.enabled: BoolProperty(name="Pin", default=True)
  ui_workflow/copy.py:129-140  HUD dict keys: mode_hint, mode_alert, legend_*
  ui_workflow/copy.py:87-98  BADGES dict, state-name keys
  ui_workflow/stage.py:74-85  Snapshot.posing / .candidate / .kept fields
  ui_workflow/stage.py:87-97  StageState.current / .state_name
"""
from __future__ import annotations

import math

try:
    import bpy
    _OperatorBase = bpy.types.Operator
except ImportError:
    bpy = None  # type: ignore[assignment]
    class _OperatorBase:  # type: ignore[no-redef]
        """Stub so the operator class definition does not fail in bpy-free environments."""

try:
    import gpu
    from gpu_extras.batch import batch_for_shader
except ImportError:
    gpu = None  # type: ignore[assignment]
    batch_for_shader = None  # type: ignore[assignment]

try:
    import blf
except ImportError:
    blf = None  # type: ignore[assignment]

from .copy import HUD, BADGES
from . import stage as _st_module

# ---------------------------------------------------------------------------
# Palette — contract §DESIGN PLAN palette + TYPE
# ---------------------------------------------------------------------------

ROLE_COLORS: dict[str, tuple[float, float, float]] = {
    'pelvis': (0.788, 0.494, 0.000),   # #C97E00
    'torso':  (0.157, 0.565, 0.369),   # #28905E
    'head':   (0.608, 0.490, 0.000),   # #9B7D00
    'hand-L': (0.906, 0.298, 0.235),   # #E74C3C
    'hand-R': (0.204, 0.596, 0.859),   # #3498DB
    'pole':   (0.608, 0.349, 0.714),   # #9B59B6
    'foot-L': (0.753, 0.224, 0.169),   # #C0392B
    'foot-R': (0.180, 0.525, 0.757),   # #2E86C1
}

# HUD legend labels (copy.py:129-140)
ROLE_LABELS: dict[str, str] = {
    'pelvis': HUD['legend_pelvis'],
    'torso':  HUD['legend_torso'],
    'head':   HUD['legend_head'],
    'hand-L': HUD['legend_hand_l'],
    'hand-R': HUD['legend_hand_r'],
    'foot-L': HUD['legend_foot_l'],
    'foot-R': HUD['legend_foot_r'],
    'pole':   HUD['legend_pole'],
}

# body_preview.TARGETS_V3 label → role  (body_preview.py:17-21)
_LABEL_TO_ROLE: dict[str, str] = {
    'Pelvis':  'pelvis',
    'Spine':   'torso',
    'Chest':   'torso',
    'Neck':    'head',
    'Head':    'head',
    'Hand L':  'hand-L',
    'Hand R':  'hand-R',
    'Foot L':  'foot-L',
    'Foot R':  'foot-R',
}

LABEL_SIZE: int = 12   # blf pixel size for target labels
STAGE_SIZE: int = 14   # blf pixel size for HUD first line

_N_CIRCLE: int = 32    # polyline segments per ring

# ---------------------------------------------------------------------------
# Module-level state  (populated by register / cleared by unregister)
# ---------------------------------------------------------------------------

_HANDLERS: list = []   # SpaceView3D draw handler handles
_LAST_SESSION_TOKEN: str = ''
_TIMER_INTERVAL: float = 0.25

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def role_of(name: str) -> str:
    """Map a body_target label to a ROLE_COLORS key.

    Pole targets end with ' pole' (body_preview.py:222: 'Body ' + label + ' pole').
    Main target labels match TARGETS_V3 second elements (body_preview.py:19-20).
    """
    if name.endswith(' pole'):
        return 'pole'
    return _LABEL_TO_ROLE.get(name, 'pelvis')


def _finite_pos(v) -> tuple[float, float, float]:
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise ValueError(f'Non-finite position: ({x}, {y}, {z})')
    return (x, y, z)


def build_payload(context) -> list[dict]:
    """Build one overlay entry per body target for the active posing session.

    Returns [] when no session is active or bpy is unavailable.  Never raises.
    Each entry: {role, label, color (RGB 3-tuple), position (world, finite),
                 pinned (bool), joint (world 3-tuple or None), height (rig bbox h)}.
    """
    if bpy is None:
        return []
    try:
        from b4artists_ml import workflow as _workflow
        from b4artists_ml import body_preview as _bp
        from mathutils import Vector

        obj = _workflow.active_rig(context)
        if obj is None:
            return []
        state = obj.b4ml
        if not state.body_payload:
            return []

        # Rig bounding-box height for ring-size scaling
        # (contact_visualization._marker_size idiom; body_preview.py:203-206)
        bb = obj.bound_box
        mat = obj.matrix_world
        heights = [(mat @ Vector(corner)).z for corner in bb]
        h = (max(heights) - min(heights)) if heights else 1.0
        if not math.isfinite(h) or h <= 0.0:
            h = 1.0

        # Attempt to read current solved joint positions from the live session
        # body_solver.py:339,346: session.world_points(session.points()) → (17,3)
        joint_world: dict[int, tuple[float, float, float]] = {}
        session = _bp._LIVE.get(obj.as_pointer())
        if session is not None:
            try:
                import numpy as _np
                pts = session.world_points(session.points())
                for end_idx, mid_idx in _bp.POLE_JOINTS.items():
                    row = pts[mid_idx]
                    if _np.isfinite(row).all():
                        joint_world[end_idx] = (float(row[0]), float(row[1]), float(row[2]))
            except Exception:
                pass

        # Build index lookup from TARGETS_V3 (body_preview.py:20)
        label_to_idx: dict[str, int] = {lbl: idx for idx, lbl in _bp.TARGETS_V3}

        entries: list[dict] = []
        for item in state.body_targets:
            label: str = item.name
            role = role_of(label)
            color = ROLE_COLORS.get(role, ROLE_COLORS['pelvis'])
            try:
                target = getattr(item, 'target', None)
                if target is None:
                    continue
                pos = _finite_pos(target.location)
            except (ValueError, AttributeError, ReferenceError):
                continue
            pinned = bool(getattr(item, 'enabled', True))
            end_idx = label_to_idx.get(label)
            joint = joint_world.get(end_idx) if end_idx is not None else None
            entries.append({
                'role':     role,
                'label':    ROLE_LABELS.get(role, label),
                'color':    color,
                'position': pos,
                'pinned':   pinned,
                'joint':    joint,
                'height':   h,
            })
        return entries
    except Exception:
        return []


# ---------------------------------------------------------------------------
# POST_VIEW draw — rings and joint lines in world space
# ---------------------------------------------------------------------------

def _draw_3d() -> None:
    if bpy is None or gpu is None or batch_for_shader is None:
        return
    changed_state = False
    try:
        context = bpy.context
        if context is None:
            return
        entries = build_payload(context)
        if not entries:
            return

        from mathutils import Vector

        region = context.region
        rv3d = context.region_data
        if rv3d is None:
            return

        # Screen-facing ring: right/up from inverted view matrix
        view_inv = rv3d.view_matrix.inverted()
        right = Vector(view_inv.col[0][:3])
        up    = Vector(view_inv.col[1][:3])

        shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        changed_state = True
        shader.bind()
        if region is not None:
            shader.uniform_float('viewportSize', (float(region.width), float(region.height)))

        for entry in entries:
            center = Vector(entry['position'])
            radius = max(entry['height'] / 40.0, 0.01)
            r, g, b = entry['color']
            pinned: bool = entry['pinned']

            # Build circle segments as LINES pairs
            # Solid when pinned; dashed (even segments only) when unpinned
            circle_verts: list[tuple[float, float, float]] = []
            for i in range(_N_CIRCLE):
                if not pinned and i % 2 != 0:
                    continue
                a0 = 2.0 * math.pi * i / _N_CIRCLE
                a1 = 2.0 * math.pi * (i + 1) / _N_CIRCLE
                v0 = center + radius * (math.cos(a0) * right + math.sin(a0) * up)
                v1 = center + radius * (math.cos(a1) * right + math.sin(a1) * up)
                circle_verts.append((v0.x, v0.y, v0.z))
                circle_verts.append((v1.x, v1.y, v1.z))

            if circle_verts:
                line_w = 2.0 if pinned else 1.5
                shader.uniform_float('lineWidth', line_w)
                shader.uniform_float('color', (r, g, b, 0.9))
                batch = batch_for_shader(shader, 'LINES', {'pos': circle_verts})
                batch.draw(shader)

            # Thin line: target → solved joint
            joint = entry.get('joint')
            if joint is not None:
                j_verts = [(center.x, center.y, center.z), joint]
                shader.uniform_float('lineWidth', 1.0)
                shader.uniform_float('color', (r, g, b, 0.5))
                jbatch = batch_for_shader(shader, 'LINES', {'pos': j_verts})
                jbatch.draw(shader)

    except Exception:
        pass
    finally:
        if changed_state:
            try:
                gpu.state.blend_set('NONE')
            except Exception:
                pass


# ---------------------------------------------------------------------------
# POST_PIXEL draw — blf labels and HUD block
# ---------------------------------------------------------------------------

def _draw_2d() -> None:
    if bpy is None or blf is None:
        return
    try:
        context = bpy.context
        if context is None:
            return

        from b4artists_ml import workflow as _workflow
        from b4artists_ml import contact_visualization as _cv
        from bpy_extras import view3d_utils
        from mathutils import Vector

        region = context.region
        rv3d   = context.region_data
        prefs  = getattr(context, 'preferences', None)
        sys_p  = getattr(prefs, 'system', None)
        ui_scale = float(getattr(sys_p, 'ui_scale', 1.0))

        font_id = 0

        # ── Per-target labels ─────────────────────────────────────────────
        entries = build_payload(context)
        if entries and region is not None and rv3d is not None:
            lbl_size = max(1, int(LABEL_SIZE * ui_scale))
            blf.size(font_id, lbl_size)
            for entry in entries:
                screen = view3d_utils.location_3d_to_region_2d(
                    region, rv3d, Vector(entry['position']))
                if screen is None:
                    continue
                sx, sy = screen
                r, g, b = entry['color']
                text = entry['label']
                # Shadow
                blf.color(font_id, 0.0, 0.0, 0.0, 0.7)
                blf.position(font_id, sx + 9.0, sy - 1.0, 0.0)
                blf.draw(font_id, text)
                # Coloured label
                blf.color(font_id, r, g, b, 1.0)
                blf.position(font_id, sx + 8.0, sy, 0.0)
                blf.draw(font_id, text)

        # ── HUD block — only while session / preview / kept is active ─────
        obj = _workflow.active_rig(context)
        if obj is None or region is None:
            return

        snap = _st_module.snapshot(context)
        if not (snap.posing or snap.candidate or snap.kept):
            return

        state_s = _st_module.evaluate(snap)
        bad_color  = _cv._COLORS.get('REJECTED', (0.95, 0.18, 0.18))
        good_color = _cv._COLORS.get('ACCEPTED', (0.18, 0.92, 0.45))

        stage_px = max(1, int(STAGE_SIZE * ui_scale))
        lbl_px   = max(1, int(LABEL_SIZE * ui_scale))
        line_h   = int(stage_px * 1.6)
        lbl_h    = int(lbl_px  * 1.5)

        x0 = 10
        y  = region.height - 30

        def _text(txt: str, color: tuple, size: int, x: int, y_pos: int) -> None:
            blf.size(font_id, size)
            blf.color(font_id, 0.0, 0.0, 0.0, 0.7)
            blf.position(font_id, float(x + 1), float(y_pos - 1), 0.0)
            blf.draw(font_id, txt)
            blf.color(font_id, color[0], color[1], color[2], 1.0)
            blf.position(font_id, float(x), float(y_pos), 0.0)
            blf.draw(font_id, txt)

        # Line 1 — stage + state badge
        badge_tmpl = BADGES.get(state_s.state_name, '')
        if '{name}' in badge_tmpl:
            act = (getattr(obj.b4ml, 'candidate_action', None)
                   if snap.candidate else getattr(obj.b4ml, 'kept_action', None))
            act_name = getattr(act, 'name', '') if act is not None else ''
            badge = badge_tmpl.format(name=act_name) if act_name else badge_tmpl.replace('{name}', '').strip()
        else:
            badge = badge_tmpl
        line1 = f'{state_s.current}  {badge}' if badge else state_s.current
        _text(line1, (1.0, 1.0, 1.0), stage_px, x0, y)
        y -= line_h

        # Line 2 — mode hint / alert
        if context.mode != 'OBJECT':
            hint = HUD.get('mode_alert', 'Switch to Object Mode')
            hcol = bad_color
        else:
            hint = HUD.get('mode_hint', 'Move targets in Object Mode')
            hcol = (0.80, 0.80, 0.80)
        _text(hint, hcol, lbl_px, x0, y)
        y -= lbl_h

        # Line 3 — legend: role labels in their palette colours
        blf.size(font_id, lbl_px)
        lx = x0
        for role, lbl_text in ROLE_LABELS.items():
            rc = ROLE_COLORS.get(role, (1.0, 1.0, 1.0))
            blf.color(font_id, 0.0, 0.0, 0.0, 0.7)
            blf.position(font_id, float(lx + 1), float(y - 1), 0.0)
            blf.draw(font_id, lbl_text)
            blf.color(font_id, rc[0], rc[1], rc[2], 1.0)
            blf.position(font_id, float(lx), float(y), 0.0)
            blf.draw(font_id, lbl_text)
            try:
                tw, _ = blf.dimensions(font_id, lbl_text + ' ')
            except Exception:
                tw = lbl_px * (len(lbl_text) + 1)
            lx += int(tw)
        y -= lbl_h

        # Line 4 — original-vs-preview badge when a preview or kept result exists
        if snap.candidate:
            act = getattr(obj.b4ml, 'candidate_action', None)
            aname = getattr(act, 'name', '') if act is not None else ''
            b4 = f'Preview: {aname}' if aname else 'Preview active'
            _text(b4, good_color, lbl_px, x0, y)
            y -= lbl_h
        elif snap.kept:
            act = getattr(obj.b4ml, 'kept_action', None)
            aname = getattr(act, 'name', '') if act is not None else ''
            b4 = f'Kept: {aname}' if aname else 'Kept result'
            _text(b4, good_color, lbl_px, x0, y)
            y -= lbl_h

        # Line 5 — frame-range bar: "frames A–B  (N key poses)"
        anchors = list(getattr(obj.b4ml, 'anchors', []))
        if anchors:
            frames = sorted(
                a.frame for a in anchors
                if hasattr(a, 'frame') and math.isfinite(float(a.frame))
            )
            if len(frames) >= 2:
                fr_text = f'frames {int(frames[0])}\u2013{int(frames[-1])}  ({len(frames)} key poses)'
                _text(fr_text, (0.70, 0.70, 0.70), lbl_px, x0, y)

    except Exception:
        pass


# ---------------------------------------------------------------------------
# Focus
# ---------------------------------------------------------------------------

def focus(context) -> bool:
    """Select all body target empties, make pelvis active, ensure Object Mode, frame selection.

    spike item 6: mode_set + temp_override(view3d.view_selected).
    Returns True on success, False otherwise.  Never raises.
    """
    if bpy is None:
        return False
    try:
        from b4artists_ml import workflow as _workflow

        obj = _workflow.active_rig(context)
        if obj is None:
            return False
        state = obj.b4ml
        if not state.body_payload:
            return False

        view_layer = context.view_layer
        for o in view_layer.objects:
            try:
                o.select_set(False)
            except RuntimeError:
                pass

        pelvis_target = None
        for item in state.body_targets:
            t = getattr(item, 'target', None)
            if t is None:
                continue
            try:
                if t.name in view_layer.objects:
                    t.select_set(True)
                    if item.name == 'Pelvis':
                        pelvis_target = t
            except (ReferenceError, RuntimeError):
                continue

        if pelvis_target is not None:
            view_layer.objects.active = pelvis_target

        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except RuntimeError:
                pass

        # Frame selection in the first VIEW_3D area  (spike item 6)
        screen = getattr(context, 'screen', None)
        if screen is None:
            return True
        area = next((a for a in screen.areas if a.type == 'VIEW_3D'), None)
        if area is None:
            return True
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region is None:
            return True
        with context.temp_override(window=context.window, area=area, region=region):
            try:
                bpy.ops.view3d.view_selected()
            except RuntimeError:
                pass
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Auto-focus timer  (spike item 7)
# ---------------------------------------------------------------------------

def _focus_poll() -> float | None:
    """bpy.app.timers callback: fire focus() once when a new body session starts."""
    global _LAST_SESSION_TOKEN
    if bpy is None:
        return None
    try:
        import json as _json
        context = bpy.context
        if context is None:
            return _TIMER_INTERVAL
        from b4artists_ml import workflow as _workflow
        obj = _workflow.active_rig(context)
        if obj is None:
            if _LAST_SESSION_TOKEN:
                _LAST_SESSION_TOKEN = ''
            return _TIMER_INTERVAL
        payload = obj.b4ml.body_payload
        if not payload:
            if _LAST_SESSION_TOKEN:
                _LAST_SESSION_TOKEN = ''
            return _TIMER_INTERVAL
        try:
            token = _json.loads(payload).get('token', '')
        except (ValueError, KeyError):
            return _TIMER_INTERVAL
        if token and token != _LAST_SESSION_TOKEN:
            _LAST_SESSION_TOKEN = token
            focus(context)
    except Exception:
        pass
    return _TIMER_INTERVAL


# ---------------------------------------------------------------------------
# Task controls — appended to VIEW3D_HT_header
# ---------------------------------------------------------------------------

def _draw_task_controls(self, context) -> None:  # noqa: ANN001
    if bpy is None:
        return
    try:
        from b4artists_ml import workflow as _workflow
        obj = _workflow.active_rig(context)
        if obj is None or not obj.b4ml.body_payload:
            return
        layout = self.layout
        layout.separator()
        layout.operator('b4ml.body_solve',       text='Solve',    icon='PLAY')
        layout.prop(obj.b4ml, 'body_live',        text='Live',     toggle=True)
        layout.operator('b4ml.body',              text='Keep').operation    = 'KEEP'
        layout.operator('b4ml.body',              text='Cancel').operation  = 'CANCEL'
        layout.operator('b4ml.ui_frame_targets',  text='Frame Controls', icon='ZOOM_SELECTED')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class B4ML_OT_ui_frame_targets(_OperatorBase):
    bl_idname  = 'b4ml.ui_frame_targets'
    bl_label   = 'Frame Controls'
    bl_description = 'Frame posing targets in the viewport'
    bl_options = {'REGISTER'}

    def execute(self, context):  # noqa: ANN001
        focus(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register() -> None:
    global _HANDLERS, _LAST_SESSION_TOKEN
    if bpy is None:
        return

    # Operator: registered in all modes including background (tests need it)
    if getattr(bpy.types, 'B4ML_OT_ui_frame_targets', None) is None:
        bpy.utils.register_class(B4ML_OT_ui_frame_targets)

    if bpy.app.background:
        return  # no draw handlers, timer, or header items in background

    # POST_VIEW handler — rings and joint lines
    if not _HANDLERS:
        h3d = bpy.types.SpaceView3D.draw_handler_add(
            _draw_3d, (), 'WINDOW', 'POST_VIEW')
        h2d = bpy.types.SpaceView3D.draw_handler_add(
            _draw_2d, (), 'WINDOW', 'POST_PIXEL')
        _HANDLERS[:] = [h3d, h2d]

    bpy.types.VIEW3D_HT_header.append(_draw_task_controls)

    # Auto-focus timer (spike item 7)
    if not bpy.app.timers.is_registered(_focus_poll):
        bpy.app.timers.register(_focus_poll, first_interval=_TIMER_INTERVAL, persistent=True)

    _LAST_SESSION_TOKEN = ''


def unregister() -> None:
    global _HANDLERS, _LAST_SESSION_TOKEN
    if bpy is None:
        return

    if not bpy.app.background:
        # Stop timer
        try:
            if bpy.app.timers.is_registered(_focus_poll):
                bpy.app.timers.unregister(_focus_poll)
        except Exception:
            pass

        # Remove header draw
        try:
            bpy.types.VIEW3D_HT_header.remove(_draw_task_controls)
        except Exception:
            pass

        # Remove draw handlers
        for handle in _HANDLERS:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
            except (ReferenceError, RuntimeError):
                pass
        _HANDLERS.clear()

    # Unregister operator
    try:
        cls = getattr(bpy.types, 'B4ML_OT_ui_frame_targets', None)
        if cls is not None:
            bpy.utils.unregister_class(cls)
    except RuntimeError:
        pass

    _LAST_SESSION_TOKEN = ''
