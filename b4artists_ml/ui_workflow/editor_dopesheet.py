"""Dope Sheet / Timeline panel, header buttons, and band overlay for B4Artists ML.

Plan §5 items 4-5; contract §STATE MAP ANCHORS_CAPTURED / PREVIEW_ACTIVE.
Spike items 2-4 (all VERIFIED):
  item 2: bl_space_type='DOPESHEET_EDITOR', bl_region_type='UI' panel registers
  item 3: DOPESHEET_HT_header has .append/.remove; TIME_HT_editor_buttons absent
  item 4: SpaceDopeSheetEditor.draw_handler_add(_cb, (), 'WINDOW', 'POST_PIXEL');
          region.view2d.view_to_region(frame, 0, clip=False) → (x_px, y_px)

Verified source facts:
  ui.py:643    'b4ml.retime_anchor' source_frame: FloatProperty(options={'HIDDEN'})
  ui.py:849    'b4ml.action' operation in ('CAPTURE','PREVIEW','KEEP','DISCARD','RESTORE_SOURCE')
  contact_visualization.py:23  _COLORS={'ACCEPTED':(0.18,0.92,0.45),'PROPOSED':(1.0,0.58,0.12)}
  contacts.py:35   rows(obj) → accepted contacts list with .start/.end dict keys
  ui.py:126    B4ML_PG_flight: .enabled, .start, .end (FloatProperty)
  header.py:109  prelude(layout, context, full=False) → (rig, snap, st)
  header.py:197  action_row(layout, st, key, idname, icon, **props) → op
  header.py:218  badge(layout, st, rig)
"""
from __future__ import annotations

try:
    import bpy
    _Panel = bpy.types.Panel
except ImportError:
    bpy = None  # type: ignore[assignment]
    _Panel = object  # type: ignore[assignment]

try:
    import gpu
    from gpu_extras.batch import batch_for_shader as _batch
except ImportError:
    gpu = None  # type: ignore[assignment]
    _batch = None  # type: ignore[assignment]

try:
    from . import copy as copy_
    from .panels import header
except ImportError:
    copy_ = None  # type: ignore[assignment]
    header = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Module-level state for idempotent register/unregister
# ---------------------------------------------------------------------------

_DRAW_HANDLER = None   # handle returned by draw_handler_add
_HEADER_APPENDED = False


# ---------------------------------------------------------------------------
# Poll helper (shared between panel and header draw)
# ---------------------------------------------------------------------------

def _active_rig_for_dopesheet(context):
    """Return (rig, b4ml) if the context rig has anchors, preview, or kept result."""
    if bpy is None:
        return None, None
    try:
        from b4artists_ml import workflow
        rig = workflow.active_rig(context)
        if rig is None:
            return None, None
        b4ml = rig.b4ml
        if (len(b4ml.anchors) > 0
                or bool(b4ml.candidate_action)
                or bool(b4ml.kept_action)):
            return rig, b4ml
    except Exception:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class B4ML_PT_dopesheet(_Panel):
    bl_space_type  = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category    = 'B4ML'
    bl_label       = 'B4Artists ML'
    bl_options     = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig, _ = _active_rig_for_dopesheet(context)
        return rig is not None

    def draw(self, context) -> None:
        if header is None or copy_ is None:
            return
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)
        if rig is None:
            return

        state = rig.b4ml

        # ── Key-pose list ──────────────────────────────────────────────────
        anchors = sorted(state.anchors, key=lambda a: float(a.frame))
        if anchors:
            col = layout.column(align=True)
            for anchor in anchors:
                row = col.row(align=True)
                row.label(text=anchor.name, icon='KEY_HLT')
                row.label(text=str(round(float(anchor.frame))))
                retime = row.operator('b4ml.retime_anchor', text='', icon='TIME')
                retime.source_frame = float(anchor.frame)
            layout.separator(factor=0.5)

        # ── State badge ────────────────────────────────────────────────────
        header.badge(layout, st, rig)

        # ── Contextual actions ─────────────────────────────────────────────
        # Capture Here: ungated — no 'motion.capture' lock key in the stage map.
        op = layout.operator('b4ml.action', text='Capture Here', icon='KEYFRAME')
        op.operation = 'CAPTURE'

        header.action_row(layout, st, 'motion.preview', 'b4ml.action',
                          icon='RENDER_ANIMATION', operation='PREVIEW')
        header.action_row(layout, st, 'review.keep',    'b4ml.action',
                          icon='CHECKMARK',      operation='KEEP')
        header.action_row(layout, st, 'review.discard', 'b4ml.action',
                          icon='X',              operation='DISCARD')
        header.action_row(layout, st, 'review.restore', 'b4ml.action',
                          icon='LOOP_BACK',      operation='RESTORE_SOURCE')

        # ── Show markers hint ──────────────────────────────────────────────
        sd = getattr(context, 'space_data', None)
        if sd is not None and not getattr(sd, 'show_markers', True):
            row = layout.row()
            row.alert = True
            row.prop(sd, 'show_markers')


# ---------------------------------------------------------------------------
# Header append (icon-only strip on DOPESHEET_HT_header)
# ---------------------------------------------------------------------------

def _draw_header(self, context) -> None:
    """Appended to bpy.types.DOPESHEET_HT_header."""
    rig, _ = _active_rig_for_dopesheet(context)
    if rig is None:
        return
    layout = self.layout
    row = layout.row(align=True)
    # Capture, Generate, Keep, Discard as icon-only buttons.
    row.operator('b4ml.action', text='', icon='KEYFRAME').operation = 'CAPTURE'
    row.operator('b4ml.action', text='', icon='RENDER_ANIMATION').operation = 'PREVIEW'
    row.operator('b4ml.action', text='', icon='CHECKMARK').operation = 'KEEP'
    row.operator('b4ml.action', text='', icon='X').operation = 'DISCARD'


# ---------------------------------------------------------------------------
# Band overlay (POST_PIXEL draw handler)
# ---------------------------------------------------------------------------

def _draw_bands() -> None:
    """Draw translucent interval bands on the Dope Sheet WINDOW region."""
    try:
        if bpy is None or gpu is None or _batch is None:
            return
        ctx = bpy.context
        area = getattr(ctx, 'area', None)
        if area is None or area.type != 'DOPESHEET_EDITOR':
            return
        region = getattr(ctx, 'region', None)
        if region is None or region.type != 'WINDOW':
            return
        scene = getattr(ctx, 'scene', None)
        if scene is None:
            return

        # Collect rigs with key poses visible in this scene.
        rigs = [o for o in scene.objects
                if o.type == 'ARMATURE' and len(o.b4ml.anchors) > 0]
        if not rigs:
            return

        v2d = region.view2d
        height = region.height
        if height <= 0:
            return

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        try:
            def _px(frame: float) -> float:
                return float(v2d.view_to_region(frame, 0, clip=False)[0])

            def _rect(x1: float, x2: float, color: tuple) -> None:
                if x2 <= x1 + 0.5:
                    return
                verts = [(x1, 0.0), (x2, 0.0), (x2, float(height)), (x1, float(height))]
                idx = [(0, 1, 2), (0, 2, 3)]
                b = _batch(shader, 'TRIS', {'pos': verts}, indices=idx)
                shader.uniform_float('color', color)
                b.draw(shader)

            for rig in rigs:
                anchors_s = sorted(rig.b4ml.anchors, key=lambda a: float(a.frame))
                if len(anchors_s) < 2:
                    continue

                first_f = float(anchors_s[0].frame)
                last_f  = float(anchors_s[-1].frame)

                # Key-pose span: neutral blue tint (preview range indicator).
                _rect(_px(first_f), _px(last_f), (0.40, 0.55, 0.90, 0.08))

                # Accepted contacts: green (contact_visualization._COLORS['ACCEPTED']).
                try:
                    from b4artists_ml import contacts as _c
                    from b4artists_ml.contact_visualization import _COLORS as _CV
                    _acc = _CV.get('ACCEPTED', (0.18, 0.92, 0.45))
                    for row in _c.rows(rig):
                        _rect(_px(float(row['start'])), _px(float(row['end'])),
                              (*_acc, 0.22))
                except Exception:
                    pass

                # Proposed contacts: orange (_COLORS['PROPOSED']).
                try:
                    from b4artists_ml.contact_visualization import _COLORS as _CV2
                    _prop = _CV2.get('PROPOSED', (1.0, 0.58, 0.12))
                    for item in rig.b4ml.contacts:
                        if item.enabled and item.review_state == 'PROPOSED':
                            _rect(_px(float(item.start)), _px(float(item.end)),
                                  (*_prop, 0.22))
                except Exception:
                    pass

                # Flight intervals: blue tint.
                try:
                    for fl in rig.b4ml.flights:
                        if fl.enabled:
                            _rect(_px(float(fl.start)), _px(float(fl.end)),
                                  (0.20, 0.50, 1.00, 0.18))
                except Exception:
                    pass

                # Priority frames: hatched vertical strips (thin lines every 2 px).
                try:
                    line_verts = []
                    for anchor in anchors_s:
                        ax = _px(float(anchor.frame))
                        for dx in range(-4, 5, 2):
                            lx = ax + dx
                            line_verts.extend([(lx, 0.0), (lx, float(height))])
                    if line_verts:
                        lb = _batch(shader, 'LINES', {'pos': line_verts})
                        shader.uniform_float('color', (0.90, 0.90, 0.50, 0.30))
                        lb.draw(shader)
                except Exception:
                    pass
        finally:
            gpu.state.blend_set('NONE')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Register / unregister (idempotent)
# ---------------------------------------------------------------------------

def register() -> None:
    """Register panel, append header draw, add band overlay (non-background only)."""
    global _DRAW_HANDLER, _HEADER_APPENDED
    if bpy is None:
        return

    # Panel class.
    if not hasattr(bpy.types, 'B4ML_PT_dopesheet'):
        bpy.utils.register_class(B4ML_PT_dopesheet)

    # Header append.
    if not _HEADER_APPENDED and hasattr(bpy.types, 'DOPESHEET_HT_header'):
        bpy.types.DOPESHEET_HT_header.append(_draw_header)
        _HEADER_APPENDED = True

    # Band overlay: skip in --background (no OpenGL context).
    if not bpy.app.background and _DRAW_HANDLER is None:
        try:
            _DRAW_HANDLER = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
                _draw_bands, (), 'WINDOW', 'POST_PIXEL')
        except Exception:
            pass


def unregister() -> None:
    """Remove panel, header draw, and band overlay."""
    global _DRAW_HANDLER, _HEADER_APPENDED

    if bpy is None:
        return

    # Band overlay.
    if _DRAW_HANDLER is not None:
        try:
            bpy.types.SpaceDopeSheetEditor.draw_handler_remove(_DRAW_HANDLER, 'WINDOW')
        except Exception:
            pass
        _DRAW_HANDLER = None

    # Header remove.
    if _HEADER_APPENDED and hasattr(bpy.types, 'DOPESHEET_HT_header'):
        try:
            bpy.types.DOPESHEET_HT_header.remove(_draw_header)
        except Exception:
            pass
        _HEADER_APPENDED = False

    # Panel class.
    if hasattr(bpy.types, 'B4ML_PT_dopesheet'):
        try:
            bpy.utils.unregister_class(B4ML_PT_dopesheet)
        except RuntimeError:
            pass
