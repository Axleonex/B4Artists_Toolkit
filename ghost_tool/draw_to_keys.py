"""draw_to_keys.py — Draw to Keys (design §8 decision 15): annotation strokes to location keys.

Reads annotation strokes the way the Annotate tool stores them in Bforartists 5.1.2 (plan Task G1):
``scene.annotation`` is a ``bpy.types.Annotation``; the active layer is ``layers[layers.active_index]``
(``layers.active_note`` is only its name, a string); a layer's
frame for the playhead is the last frame at or before it; each stroke's ``points[i].co`` is a world-space
point when ``display_mode`` is '3DSPACE' (Surface or 3D Cursor placement). A View-placed stroke in the 3D
viewport is screen-locked ('2DSPACE'), has no depth, and is refused. The geometry is in
draw_to_keys_math (no bpy).
"""

from __future__ import annotations

from typing import Optional

import bpy
from mathutils import Vector


def _frame_at(layer, frame_current: int):
    """The annotation frame shown at ``frame_current``: the last one at or before it (frames hold), or None
    before the first frame (nothing is drawn there yet). Always computed from the frame list:
    ``layer.active_frame`` is None headless and is not checked against the playhead (review 976236d6)."""
    frames = sorted(layer.frames, key=lambda fr: fr.frame_number)
    if not frames:
        return None
    held = [fr for fr in frames if fr.frame_number <= frame_current]
    return held[-1] if held else None


def annotation_strokes(scene) -> tuple[list[list[Vector]], int]:
    """(3D strokes of the active annotation layer at the playhead, number of strokes refused for not being
    in 3D space). Hidden layers and strokes with fewer than two points are skipped."""
    annotation = getattr(scene, "annotation", None)
    layer: Optional[bpy.types.AnnotationLayer] = None
    if annotation is not None and 0 <= annotation.layers.active_index < len(annotation.layers):
        layer = annotation.layers[annotation.layers.active_index]
    if layer is None or layer.annotation_hide:
        return [], 0
    frame = _frame_at(layer, scene.frame_current)
    if frame is None:
        return [], 0
    strokes, refused = [], 0
    for stroke in frame.strokes:
        if stroke.display_mode != '3DSPACE':
            refused += 1
            continue
        points = [Vector(p.co) for p in stroke.points]
        if len(points) >= 2:
            strokes.append(points)
    return strokes, refused
