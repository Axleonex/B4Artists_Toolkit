"""B4ML Motion panel.

Plan §3 "Motion"; Contract states ANCHORS_CAPTURED, SOLVE_RUNNING.
Lock reason: "Capture a second key pose to generate motion".

Verified facts (ui.py):
  _ANCHOR_PAGE_SIZE = 10 (ui.py:116)
  _anchor_page logic: sort by frame, ceil(len/10), clamp to [1, page_count] (ui.py:119-124)
  first/last anchor frames: min/max over state.anchors (ui.py:2774-2775)
  anchor row: anchor.name, retime_anchor.source_frame, ripple_retime.source_frame,
    pose_spacing_scale.pivot_frame, pose_spacing_equalize.pivot_frame (ui.py:2776-2796)
  transition_timing.frame, transition_timing_transfer operation/frame (ui.py:2789-2796)
  breakdown_pose / inbetween_series: POSES mode only (ui.py:2759-2763)
  interpolation_method, easing, timing_bias, temporal_strength, temporal_smoothing (ui.py:2808-2817)
  b4ml.action operation='PREVIEW' (ui.py:2823)
  b4ml.anchor_page .page prop (ui.py:2768-2773)
  workflow.has_transition_timing_override(anchor.payload) (ui.py:2790)
  No frame-jump pattern in draw() — frame drawn as label (ui.py:2776-2796)
  screen.space_type_set_or_cycle not found in Bforartists 5.1 startup scripts — UNVERIFIED
"""
from __future__ import annotations

import importlib.util
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
        'b4artists_ml.ui_workflow.copy',
        os.path.join(_uw_dir, 'copy.py'),
    )
    header = _load_mod(  # type: ignore[assignment]
        'b4artists_ml.ui_workflow.panels.header',
        os.path.join(_panels_dir, 'header.py'),
    )

_Panel = bpy.types.Panel if bpy is not None else object

_ANCHOR_PAGE_SIZE = 10  # must stay in sync with ui.py:116


def _has_timing_override(anchor) -> bool:
    """Return True if anchor carries a transition timing override; safe fallback."""
    try:
        from b4artists_ml import workflow as _wf
        return bool(_wf.has_transition_timing_override(anchor.payload))
    except Exception:
        return False


class B4ML_PT_motion(_Panel):
    """Motion panel — key-pose list, interpolation method, and preview action.

    Plan §3 "Motion"; Contract states ANCHORS_CAPTURED, SOLVE_RUNNING.
    Lock reason: "Capture a second key pose to generate motion".
    """

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'
    bl_label = 'Motion'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return True  # prelude handles the no-rig case

    def draw(self, context):
        layout = self.layout
        rig, snap, st = header.prelude(layout, context)

        if rig is None:
            return

        state = rig.b4ml

        # ── Key-pose list ─────────────────────────────────────────────────────
        anchors = sorted(getattr(state, 'anchors', []), key=lambda a: a.frame)
        page_count = max(1, math.ceil(len(anchors) / _ANCHOR_PAGE_SIZE))
        anchor_page = min(max(int(getattr(state, 'anchor_page', 1)), 1), page_count)
        start = (anchor_page - 1) * _ANCHOR_PAGE_SIZE
        page_anchors = anchors[start:start + _ANCHOR_PAGE_SIZE]

        first_anchor_frame = min((a.frame for a in anchors), default=None)
        last_anchor_frame = max((a.frame for a in anchors), default=None)

        interp = getattr(state, 'interpolation_method', 'POSES')

        col = layout.column()

        # Breakdown / inbetween series — POSES mode only; operators' poll()
        # guards the >=2-anchor requirement.
        if interp == 'POSES':
            col.operator('b4ml.breakdown_pose', text='Create Breakdown Pose', icon='KEY_HLT')
            col.operator('b4ml.inbetween_series', text='Procedural Inbetween Series',
                         icon='KEYFRAME_HLT')

        # Pagination (only shown when more than one page; operators guard bounds).
        if page_count > 1:
            row = col.row(align=True)
            op = row.operator('b4ml.anchor_page', text='', icon='TRIA_LEFT')
            op.page = max(1, anchor_page - 1)
            row.label(text=f'Pose Page {anchor_page} of {page_count}')
            op = row.operator('b4ml.anchor_page', text='', icon='TRIA_RIGHT')
            op.page = min(page_count, anchor_page + 1)

        # Per-anchor rows — verbatim port of ui.py:2776-2796.
        # Frame number drawn as label; no frame-jump operator verified in draw()
        # (see open questions).
        for anchor in page_anchors:
            row = col.row(align=True)
            row.label(text=anchor.name, icon='KEY_HLT')
            row.label(text=str(round(anchor.frame)))
            retime = row.operator('b4ml.retime_anchor', text='', icon='TIME')
            retime.source_frame = anchor.frame
            ripple = row.operator('b4ml.ripple_retime', text='', icon='TRIA_RIGHT')
            ripple.source_frame = anchor.frame
            if last_anchor_frame is not None and abs(anchor.frame - last_anchor_frame) >= 1e-5:
                scale = row.operator('b4ml.pose_spacing_scale', text='', icon='FULLSCREEN_ENTER')
                scale.pivot_frame = anchor.frame
                equalize = row.operator('b4ml.pose_spacing_equalize', text='=')
                equalize.pivot_frame = anchor.frame
            if (interp == 'POSES' and first_anchor_frame is not None
                    and abs(anchor.frame - first_anchor_frame) >= 1e-5):
                edit = row.operator(
                    'b4ml.transition_timing',
                    text='Timing*' if _has_timing_override(anchor) else 'Timing',
                )
                edit.frame = anchor.frame
                cp = row.operator('b4ml.transition_timing_transfer', text='', icon='COPYDOWN')
                cp.operation = 'COPY'
                cp.frame = anchor.frame
                paste_row = row.row(align=True)
                paste = paste_row.operator(
                    'b4ml.transition_timing_transfer', text='', icon='PASTEDOWN',
                )
                paste.operation = 'PASTE'
                paste.frame = anchor.frame

        # ── Method + timing ───────────────────────────────────────────────────
        layout.prop(state, 'interpolation_method')
        if interp == 'POSES':
            layout.prop(state, 'easing')
            layout.prop(state, 'timing_bias', slider=True)
        else:
            layout.prop(state, 'temporal_strength', slider=True)
            layout.prop(state, 'temporal_smoothing')
            layout.label(text='Procedural; strength blends toward endpoint interpolation')

        # ── Primary action ────────────────────────────────────────────────────
        # copy.BUTTONS['motion.preview'] = 'Generate Preview (frames {a}-{b})';
        # strip the frame range when fewer than two distinct key-pose frames exist.
        if (first_anchor_frame is not None and last_anchor_frame is not None
                and abs(last_anchor_frame - first_anchor_frame) >= 1e-5):
            btn_text = copy_.fmt(
                copy_.BUTTONS['motion.preview'],
                a=round(first_anchor_frame),
                b=round(last_anchor_frame),
            )
        else:
            btn_text = 'Generate Preview'
        header.action_row(
            layout, st, 'motion.preview', 'b4ml.action',
            text=btn_text, icon='RENDER_ANIMATION', operation='PREVIEW',
        )

        # ── Show Timeline ─────────────────────────────────────────────────────
        # screen.space_type_set_or_cycle was not found in Bforartists 5.1 startup
        # scripts; drawing a plain label as fallback (UNVERIFIED — cut-over packet
        # should confirm operator availability and replace with the live operator).
        layout.label(text=copy_.BUTTONS['motion.show_timeline'], icon='TIME')


CLASSES = (B4ML_PT_motion,)
