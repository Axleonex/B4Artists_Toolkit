"""
modal_operator.py — GhostDragOperator: modal loop for interactive ghost dragging.

This module provides the primary interaction operator for Ghost Tool.
When invoked, it enters a modal loop that:
1. Detects which ghost is under the cursor via screen-space proximity
2. Lets the user drag the ghost in 3D space with axis constraints
3. Recalculates the f-curve in real time as the ghost moves
4. Confirms with left-click release, cancels with right-click or Escape
5. Pushes to Blender's undo stack on confirmation
"""

from __future__ import annotations

import math
from typing import Optional

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix

from .ghost_data import Ghost, GhostStore
from .session_state import SessionState
from . import fcurve_utils
from .utils import log, warn, debug, tag_viewport_redraw


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_GRAB_RADIUS_PX: int = 20
"""Default screen-space radius in pixels for ghost picking."""

DRAG_SENSITIVITY: float = 0.1
"""Scaling factor for delta magnitude in non-location channel calculations."""

_CONSTRAINT_PLANE_NORMALS = {
    "YZ": Vector((1, 0, 0)),
    "XZ": Vector((0, 1, 0)),
    "XY": Vector((0, 0, 1)),
}
"""Map plane constraint names to their normal vectors."""

_AXIS_MASKS = {
    "X": (True, False, False),
    "Y": (False, True, False),
    "Z": (False, False, True),
}
"""Map single-axis constraint names to component masks (x, y, z)."""

_SINGLE_AXIS_FALLBACKS = {
    "X": Vector((0, 0, 1)),
    "Y": Vector((1, 0, 0)),
    "Z": Vector((0, 1, 0)),
}
"""Fallback normals when view is parallel to an axis constraint."""


# ---------------------------------------------------------------------------
# Helper: view and direction utilities
# ---------------------------------------------------------------------------

def _get_view_direction(region_3d: bpy.types.RegionView3D) -> Vector:
    """Extract the camera/view direction from the 3D region data.

    The view direction is the negative Z axis of the view matrix.

    Args:
        region_3d: The 3D region viewport data.

    Returns:
        Vector: Normalized view direction vector.
    """
    view_dir = Vector((region_3d.view_matrix[2][0], region_3d.view_matrix[2][1], region_3d.view_matrix[2][2]))
    view_dir.normalize()
    return view_dir


# ---------------------------------------------------------------------------
# Helper: screen-space projection
# ---------------------------------------------------------------------------

def _world_to_screen(
    context: bpy.types.Context,
    world_pos: Vector,
) -> Optional[tuple[float, float]]:
    """Project a 3D world-space point to 2D screen coordinates.

    Args:
        context: The current Blender context (must have a 3D region).
        world_pos: The point in world space.

    Returns:
        tuple[float, float] or None: Screen coordinates (x, y), or None
            if the point is behind the camera.
    """
    region = context.region
    region_3d = context.region_data
    if not region or not region_3d:
        return None

    screen_pos = view3d_utils.location_3d_to_region_2d(region, region_3d, world_pos)
    if screen_pos is None:
        return None
    return (screen_pos.x, screen_pos.y)


def _find_ghost_under_cursor(
    context: bpy.types.Context,
    mouse_x: int,
    mouse_y: int,
    grab_radius: int,
) -> Optional[Ghost]:
    """Find the closest ghost within grab_radius of the mouse position.

    Args:
        context: The current Blender context.
        mouse_x: Mouse X position in region coordinates.
        mouse_y: Mouse Y position in region coordinates.
        grab_radius: Maximum distance in pixels to consider a ghost hit.

    Returns:
        Ghost or None: The closest ghost, or None if none are within range.
    """
    store = GhostStore.get(context.scene)
    best_ghost: Optional[Ghost] = None
    best_dist_sq = grab_radius * grab_radius

    for ghost in store:
        screen_pos = _world_to_screen(context, ghost.world_position)
        if screen_pos is None:
            continue

        dx = screen_pos[0] - mouse_x
        dy = screen_pos[1] - mouse_y
        dist_sq = dx * dx + dy * dy

        if dist_sq < best_dist_sq:
            best_dist_sq = dist_sq
            best_ghost = ghost

    return best_ghost


# ---------------------------------------------------------------------------
# Helper: ray-plane intersection for 3D dragging
# ---------------------------------------------------------------------------

def _get_depth_plane(
    context: bpy.types.Context,
    point: Vector,
) -> tuple[Vector, Vector]:
    """Compute a view-facing plane through the given point.

    This plane is perpendicular to the view direction, passing through
    the point.  Used as the default drag constraint plane.

    Args:
        context: The current Blender context.
        point: A world-space point the plane should pass through.

    Returns:
        tuple: (plane_point, plane_normal) both as Vectors.
    """
    region_3d = context.region_data
    if region_3d is None:
        return (point.copy(), Vector((0, 0, 1)))
    view_dir = _get_view_direction(region_3d)
    return (point.copy(), view_dir)


def _ray_plane_intersect(
    origin: Vector,
    direction: Vector,
    plane_point: Vector,
    plane_normal: Vector,
) -> Optional[Vector]:
    """Compute the intersection of a ray with a plane.

    Args:
        origin: Ray origin point.
        direction: Ray direction (does not need to be normalized).
        plane_point: A point on the plane.
        plane_normal: The plane normal vector.

    Returns:
        Vector or None: Intersection point, or None if ray is parallel.
    """
    denom = plane_normal.dot(direction)
    if abs(denom) < 1e-8:
        return None

    t = plane_normal.dot(plane_point - origin) / denom
    if t < 0:
        return None

    return origin + direction * t


def _get_constraint_plane(
    axis_constraint: str,
    ghost_pos: Vector,
    context: bpy.types.Context,
    transform_space: str = "WORLD",
    ghost: Optional[Ghost] = None,
) -> tuple[Vector, Vector]:
    """Get the constraint plane based on the active axis constraint.

    For plane constraints (YZ, XZ, XY), returns a fixed normal.
    For single-axis constraints (X, Y, Z), projects the view direction
    onto the perpendicular plane to handle arbitrary viewing angles.

    Args:
        axis_constraint: One of "NONE", "X", "Y", "Z", "YZ", "XZ", "XY".
        ghost_pos: The ghost's current world position (plane passes through this).
        context: The current Blender context.
        transform_space: "WORLD", "LOCAL", or "VIEW" for transform space.
        ghost: The ghost object (needed for LOCAL space transform).

    Returns:
        tuple: (plane_point, plane_normal).
    """
    # Plane constraints: use fixed normals
    if axis_constraint in _CONSTRAINT_PLANE_NORMALS:
        normal = _CONSTRAINT_PLANE_NORMALS[axis_constraint].copy()

        # Transform normal to local space if needed
        if transform_space == "LOCAL" and ghost:
            obj = bpy.data.objects.get(ghost.object_name)
            if obj:
                rot_matrix = obj.matrix_world.to_3x3().normalized()
                normal = rot_matrix @ normal
                normal.normalize()

        return (ghost_pos.copy(), normal)

    # Single-axis constraints: project view direction onto the perpendicular plane
    if axis_constraint in ("X", "Y", "Z"):
        region_3d = context.region_data
        if region_3d is None:
            return (ghost_pos.copy(), Vector((0, 0, 1)))
        view_dir = _get_view_direction(region_3d)

        # Get the axis vector for this constraint
        axis_vectors = {
            "X": Vector((1, 0, 0)),
            "Y": Vector((0, 1, 0)),
            "Z": Vector((0, 0, 1)),
        }
        axis_vector = axis_vectors[axis_constraint].copy()

        # Transform axis vector to local space if needed
        if transform_space == "LOCAL" and ghost:
            obj = bpy.data.objects.get(ghost.object_name)
            if obj:
                rot_matrix = obj.matrix_world.to_3x3().normalized()
                axis_vector = rot_matrix @ axis_vector

        # Project view direction onto the plane perpendicular to the axis
        normal = view_dir - axis_vector * view_dir.dot(axis_vector)

        # If view is parallel to the axis, use a fallback normal
        if normal.length < 0.001:
            normal = _SINGLE_AXIS_FALLBACKS[axis_constraint].copy()
            if transform_space == "LOCAL" and ghost:
                obj = bpy.data.objects.get(ghost.object_name)
                if obj:
                    rot_matrix = obj.matrix_world.to_3x3().normalized()
                    normal = rot_matrix @ normal
        else:
            normal.normalize()

        return (ghost_pos.copy(), normal)

    # No constraint — use the view-facing depth plane (VIEW space)
    return _get_depth_plane(context, ghost_pos)


def _apply_axis_constraint(
    new_pos: Vector,
    original_pos: Vector,
    axis_constraint: str,
    transform_space: str = "WORLD",
    ghost: Optional[Ghost] = None,
) -> Vector:
    """Apply an axis constraint to a position delta.

    For single-axis constraints (X, Y, Z), only the constrained axis
    component is kept. For plane constraints (YZ, XZ, XY), two axes
    are kept.

    When transform_space is LOCAL, the constraint is applied in the
    object's local coordinate system, then transformed back to world space.

    Args:
        new_pos: The unconstrained new position (world space).
        original_pos: The ghost's original position before dragging (world space).
        axis_constraint: The active constraint.
        transform_space: Either "WORLD" or "LOCAL". Determines the coordinate
                        system in which the constraint is applied.
        ghost: The Ghost object (required when transform_space is LOCAL).

    Returns:
        Vector: The constrained position (world space).
    """
    # Helper function to apply the masking in a given coordinate system
    def _mask_axes(new: Vector, original: Vector, constraint: str) -> Vector:
        """Mask axes according to the constraint."""
        # Single-axis constraints: keep only the constrained axis
        if constraint in _AXIS_MASKS:
            mask_x, mask_y, mask_z = _AXIS_MASKS[constraint]
            return Vector((
                new.x if mask_x else original.x,
                new.y if mask_y else original.y,
                new.z if mask_z else original.z,
            ))

        # Plane constraints: keep two axes
        if constraint == "YZ":
            return Vector((original.x, new.y, new.z))
        elif constraint == "XZ":
            return Vector((new.x, original.y, new.z))
        elif constraint == "XY":
            return Vector((new.x, new.y, original.z))

        # No constraint
        return new.copy()

    # For LOCAL space, work in the object's coordinate system
    if transform_space == "LOCAL" and ghost:
        obj = bpy.data.objects.get(ghost.object_name)
        if obj:
            mat_inv = obj.matrix_world.inverted()
            local_new = mat_inv @ new_pos
            local_orig = mat_inv @ original_pos
            # Apply mask in local space
            result_local = _mask_axes(local_new, local_orig, axis_constraint)
            return obj.matrix_world @ result_local

    # WORLD space: mask directly
    return _mask_axes(new_pos, original_pos, axis_constraint)


# ---------------------------------------------------------------------------
# GhostDragOperator
# ---------------------------------------------------------------------------

class GhostDragOperator(bpy.types.Operator):
    """Modal operator for dragging ghost markers in the 3D viewport.

    When invoked, this operator finds the ghost nearest to the mouse cursor
    and enters a modal loop.  The user drags the ghost in 3D space, with
    optional axis constraints, and the f-curve is recalculated in real time.

    Keybindings during modal:
        MOUSEMOVE — Update ghost position
        X/Y/Z — Activate single-axis constraint
        SHIFT+X/Y/Z — Activate plane constraint (perpendicular to that axis)
        LEFT MOUSE release — Confirm and push to undo
        RIGHT MOUSE or ESC — Cancel and restore original f-curve
    """

    bl_idname = "ghost_tool.drag_ghost"
    bl_label = "Drag Ghost"
    bl_options = {'REGISTER', 'UNDO'}

    # --- Internal state annotations (initialized per-instance in invoke) ---

    _active_ghost: Optional[Ghost]
    _original_position: Optional[Vector]
    _original_local_value: float
    _axis_constraint: str
    _undo_snapshots: dict  # fcurve_key -> snapshot list
    _affected_fcurves: dict  # fcurve_key -> FCurve
    _editing_mode: str  # captured at invoke for consistency
    _temp_key_inserted: bool  # True if Model A inserted a temp key during drag
    _falloff_neighbors: list  # list of (ghost, original_value, weight) for sculpt falloff
    _transform_space: str  # WORLD, LOCAL, or VIEW
    _multi_drag_ghosts: list  # list of (ghost, original_value, original_position) for multi-ghost drag

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Check if the operator can run.

        Requires an active scene with ghost_tool settings and at least
        one ghost in the store.

        Args:
            context: The current Blender context.

        Returns:
            bool: True if the operator can execute.
        """
        scene = context.scene
        if not hasattr(scene, 'ghost_tool'):
            return False
        if not scene.ghost_tool.is_active:
            return False
        store = GhostStore.get(scene)
        return len(store) > 0

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Begin the modal ghost drag operation.

        Identifies the ghost under the cursor, snapshots affected f-curves,
        and enters modal mode.

        Args:
            context: The current Blender context.
            event: The triggering event.

        Returns:
            set[str]: {'RUNNING_MODAL'} on success, {'CANCELLED'} if no ghost found.
        """
        settings = context.scene.ghost_tool
        grab_radius = settings.grab_radius

        # Find ghost under cursor
        ghost = _find_ghost_under_cursor(
            context, event.mouse_region_x, event.mouse_region_y, grab_radius
        )

        if ghost is None:
            self.report({'WARNING'}, "No ghost under cursor — try increasing Grab Radius in Ghost Tool settings")
            return {'CANCELLED'}

        # Initialize all per-instance mutable state here — never at class level.
        self._active_ghost = ghost
        self._original_position = ghost.world_position.copy()
        self._original_local_value = ghost.local_value
        self._axis_constraint = "NONE"
        self._undo_snapshots = {}
        self._affected_fcurves = {}
        self._editing_mode = settings.editing_mode
        self._temp_key_inserted = False
        self._reusing_existing_key = False
        self._transform_space = "WORLD"
        self._falloff_neighbors = []

        # Clear frame position cache to prevent stale data from previous drags
        fcurve_utils.clear_frame_cache()

        obj = bpy.data.objects.get(ghost.object_name)
        if obj:
            fcurve = fcurve_utils.resolve_fcurve(obj, ghost.bone_name, ghost.channel)
            if fcurve:
                fc_key = f"{ghost.object_name}:{ghost.bone_name}:{ghost.channel}"
                self._undo_snapshots[fc_key] = fcurve_utils.snapshot_fcurve(fcurve)
                self._affected_fcurves[fc_key] = fcurve

        # Gather neighboring ghosts for falloff sculpting
        self._falloff_neighbors = []  # list of (ghost, original_value, weight)
        falloff_radius = settings.sculpt_falloff_radius
        if falloff_radius > 0 and obj:
            falloff_curve = settings.sculpt_falloff_curve
            store = GhostStore.get(context.scene)
            chain = store.get_chain(ghost.object_name, ghost.bone_name, ghost.channel)
            for neighbor in chain:
                if neighbor.uid == ghost.uid:
                    continue
                frame_dist = abs(neighbor.frame - ghost.frame)
                if frame_dist <= falloff_radius:
                    # Compute falloff weight
                    t = frame_dist / falloff_radius
                    if falloff_curve == "LINEAR":
                        weight = 1.0 - t
                    elif falloff_curve == "SHARP":
                        weight = (1.0 - t) ** 2
                    else:  # SMOOTH (cosine)
                        weight = 0.5 * (1.0 + math.cos(math.pi * t))

                    self._falloff_neighbors.append((neighbor, neighbor.local_value, weight))

                    # Snapshot neighbor's f-curve if not already done
                    # Use the NEIGHBOR's object, not the primary ghost's obj
                    n_obj = bpy.data.objects.get(neighbor.object_name)
                    n_fc = fcurve_utils.resolve_fcurve(n_obj, neighbor.bone_name, neighbor.channel) if n_obj else None
                    if n_fc:
                        n_key = f"{neighbor.object_name}:{neighbor.bone_name}:{neighbor.channel}"
                        if n_key not in self._undo_snapshots:
                            self._undo_snapshots[n_key] = fcurve_utils.snapshot_fcurve(n_fc)
                            self._affected_fcurves[n_key] = n_fc

        # Gather all selected ghosts for multi-drag
        self._multi_drag_ghosts = []  # list of (ghost, original_value, original_position)
        session = SessionState.get(context.scene)
        if len(session.selection_set) > 1 and ghost.uid in session.selection_set:
            store = GhostStore.get(context.scene)
            for uid in session.selection_set:
                if uid == ghost.uid:
                    continue
                other = store.get_by_uid(uid)
                if other is None:
                    continue
                self._multi_drag_ghosts.append((other, other.local_value, other.world_position.copy()))

                # Snapshot other's f-curve
                other_obj = bpy.data.objects.get(other.object_name)
                if other_obj:
                    other_fc = fcurve_utils.resolve_fcurve(other_obj, other.bone_name, other.channel)
                    if other_fc:
                        other_key = f"{other.object_name}:{other.bone_name}:{other.channel}"
                        if other_key not in self._undo_snapshots:
                            self._undo_snapshots[other_key] = fcurve_utils.snapshot_fcurve(other_fc)
                            self._affected_fcurves[other_key] = other_fc

        # Mark ghost as selected for visual feedback via SessionState
        session = SessionState.get(context.scene)
        session.select_only(ghost.uid)

        context.window_manager.modal_handler_add(self)
        self._drag_session = session
        session.drag_active = True
        tag_viewport_redraw(context)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        try:
            return self._modal_inner(context, event)
        except Exception as exc:
            try:
                self._cancel_drag(context)
            except Exception as rollback_error:
                warn(f"Drag rollback could not finish: {rollback_error}")
            finally:
                self._cleanup()
            self.report({'ERROR'}, f"Ghost drag cancelled after an error: {exc}")
            return {'CANCELLED'}

    def _modal_inner(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Handle events during the modal drag loop.

        Args:
            context: The current Blender context.
            event: The current event.

        Returns:
            set[str]: Modal state ('RUNNING_MODAL', 'FINISHED', 'CANCELLED').
        """
        ghost = self._active_ghost
        if ghost is None:
            self._cleanup()
            return {'CANCELLED'}

        # Validate parent object still exists (user may delete during drag)
        obj = bpy.data.objects.get(ghost.object_name)
        if obj is None:
            self.report({'WARNING'}, "Object was deleted during drag")
            self._cancel_drag(context)
            return {'CANCELLED'}

        # --- Axis constraint keys ---
        if event.type in {'X', 'Y', 'Z'} and event.value == 'PRESS':
            axis = event.type  # "X", "Y", or "Z"

            if event.shift:
                # SHIFT+axis → plane constraint (perpendicular to that axis)
                # Map single axis to the plane perpendicular to it
                plane_map = {"X": "YZ", "Y": "XZ", "Z": "XY"}
                new_constraint = plane_map[axis]
            else:
                new_constraint = axis

            # Toggle: pressing the same constraint again removes it
            if self._axis_constraint == new_constraint:
                self._axis_constraint = "NONE"
            else:
                self._axis_constraint = new_constraint

            self.report({'INFO'}, f"Constraint: {self._axis_constraint}")
            return {'RUNNING_MODAL'}

        # --- Transform space keys ---
        if event.type == 'L' and event.value == 'PRESS':
            if self._transform_space == "LOCAL":
                self._transform_space = "WORLD"
            else:
                self._transform_space = "LOCAL"
            self.report({'INFO'}, f"Space: {self._transform_space}")
            return {'RUNNING_MODAL'}

        if event.type == 'V' and event.value == 'PRESS':
            if self._transform_space == "VIEW":
                self._transform_space = "WORLD"
            else:
                self._transform_space = "VIEW"
            self.report({'INFO'}, f"Space: {self._transform_space}")
            return {'RUNNING_MODAL'}

        # --- Mouse movement: update ghost position ---
        if event.type == 'MOUSEMOVE':
            self._update_ghost_position(context, event)
            tag_viewport_redraw(context)
            return {'RUNNING_MODAL'}

        # --- Confirm drag with left mouse release ---
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self._confirm_drag(context)
            return {'FINISHED'}

        # --- Cancel drag with right mouse or Escape ---
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cancel_drag(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _update_ghost_position(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ) -> None:
        """Update the ghost's world position based on cursor movement.

        Casts a ray from the mouse into the scene, intersects it with
        the constraint plane, and moves the ghost to the hit point.

        Args:
            context: The current Blender context.
            event: The mouse move event.
        """
        ghost = self._active_ghost
        if ghost is None:
            return

        region = context.region
        region_3d = context.region_data
        if not region or not region_3d:
            return

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        # Build ray from mouse position
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_pos)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_pos)

        # Get the constraint plane with transform space support
        plane_point, plane_normal = _get_constraint_plane(
            self._axis_constraint, self._original_position, context,
            transform_space=self._transform_space, ghost=ghost
        )

        # Detect degenerate constraint (view parallel to axis) — only for single-axis
        if self._axis_constraint in ("X", "Y", "Z"):
            axis_vector = Vector((0, 0, 0))
            axis_vector[{"X": 0, "Y": 1, "Z": 2}[self._axis_constraint]] = 1.0
            # Transform axis vector to match the constraint's transform space
            if self._transform_space == "LOCAL" and ghost:
                local_obj = bpy.data.objects.get(ghost.object_name)
                if local_obj:
                    rot_matrix = local_obj.matrix_world.to_3x3().normalized()
                    axis_vector = rot_matrix @ axis_vector
                    axis_vector.normalize()
            if abs(plane_normal.dot(axis_vector)) > 0.999:
                self.report({'WARNING'}, "Cannot constrain to this axis from current view angle")
                self._axis_constraint = "NONE"
                return

        # Intersect ray with plane
        hit = _ray_plane_intersect(ray_origin, ray_direction, plane_point, plane_normal)
        if hit is None:
            return

        # Apply axis constraint to the hit point
        constrained_pos = _apply_axis_constraint(
            hit, self._original_position, self._axis_constraint,
            transform_space=self._transform_space, ghost=ghost
        )

        # Update ghost data
        ghost.world_position = constrained_pos

        # Convert world position delta back to f-curve value.
        # We approximate this by computing the value offset based on the
        # channel axis.  For location channels, the mapping is direct.
        # For rotation/scale, a more sophisticated conversion is needed.
        self._update_fcurve_from_position(context, ghost, constrained_pos)

    def _update_fcurve_from_position(
        self,
        context: bpy.types.Context,
        ghost: Ghost,
        new_world_pos: Vector,
    ) -> None:
        """Recalculate the f-curve to match the ghost's new world position.

        For location channels, the world-space delta is converted to
        local space and applied directly.  For other channel types,
        a proportional approximation is used.

        Args:
            context: The current Blender context.
            ghost: The ghost being moved.
            new_world_pos: The ghost's new world-space position.
        """
        obj = bpy.data.objects.get(ghost.object_name)
        if not obj:
            return

        fcurve = fcurve_utils.resolve_fcurve(obj, ghost.bone_name, ghost.channel)
        if fcurve is None:
            return

        # Determine which value axis this channel represents
        channel_lower = ghost.channel.lower()

        if "location" in channel_lower:
            # For location channels, compute the local-space value from world pos
            delta_world = new_world_pos - self._original_position

            # Convert world delta to object local space
            if obj.parent:
                parent_matrix_inverted = obj.parent.matrix_world.inverted()
                delta_local = parent_matrix_inverted.to_3x3() @ delta_world
            else:
                delta_local = delta_world.copy()

            # If this is a bone channel, convert to the bone's CHANNEL space:
            # a pose bone's location is relative to its rest matrix
            # (bone.matrix_local), re-parented under the parent's posed matrix.
            # Using only the parent's pose matrix (or only object space for a
            # root bone) dropped matrix_local and dragged the bone off-axis.
            if ghost.bone_name and obj.type == 'ARMATURE':
                pose_bone = obj.pose.bones.get(ghost.bone_name)
                if pose_bone:
                    bone = pose_bone.bone
                    if pose_bone.parent:
                        channel = (pose_bone.parent.matrix
                                   @ pose_bone.parent.bone.matrix_local.inverted()
                                   @ bone.matrix_local)
                    else:
                        channel = bone.matrix_local
                    delta_local = (obj.matrix_world @ channel).to_3x3().inverted() @ delta_world

            # Extract the relevant axis component
            if channel_lower.endswith(".x"):
                new_value = self._original_local_value + delta_local.x
            elif channel_lower.endswith(".y"):
                new_value = self._original_local_value + delta_local.y
            elif channel_lower.endswith(".z"):
                new_value = self._original_local_value + delta_local.z
            else:
                new_value = self._original_local_value + delta_local.length
        else:
            # For non-location channels, use a proportional approximation.
            # The world-space delta magnitude is mapped to a value change.
            delta = new_world_pos - self._original_position
            new_value = self._original_local_value + delta.length * DRAG_SENSITIVITY

        # Apply to the f-curve based on editing mode.
        # Model B (RESHAPE): adjust bezier handles so curve passes through new_value.
        # Model A (INSERT_KEY): insert/update a temporary keyframe for live preview.
        if self._editing_mode == 'INSERT_KEY':
            self._preview_model_a(fcurve, ghost.frame, new_value)
        else:
            mode = context.scene.ghost_tool.curve_mode.lower()
            fcurve_utils.recalculate_handles(fcurve, ghost.frame, new_value, mode=mode)

        # Update the ghost's local value
        ghost.local_value = new_value

        # Apply falloff to neighboring ghosts
        if hasattr(self, '_falloff_neighbors') and self._falloff_neighbors:
            delta_from_original = new_value - self._original_local_value
            for neighbor, orig_val, weight in self._falloff_neighbors:
                neighbor_new_val = orig_val + delta_from_original * weight
                neighbor.local_value = neighbor_new_val

                # Update neighbor's f-curve
                n_obj = bpy.data.objects.get(neighbor.object_name)
                if n_obj:
                    n_fc = fcurve_utils.resolve_fcurve(n_obj, neighbor.bone_name, neighbor.channel)
                    if n_fc:
                        mode = context.scene.ghost_tool.curve_mode.lower()
                        fcurve_utils.recalculate_handles(n_fc, neighbor.frame, neighbor_new_val, mode=mode)

        # Apply same delta to all multi-drag ghosts (skip any already updated by falloff)
        if hasattr(self, '_multi_drag_ghosts') and self._multi_drag_ghosts:
            # Build set of UIDs already updated by falloff to avoid double-update
            falloff_uids = set()
            if hasattr(self, '_falloff_neighbors') and self._falloff_neighbors:
                falloff_uids = {n.uid for n, _, _ in self._falloff_neighbors}

            value_delta = new_value - self._original_local_value
            for other_ghost, orig_val, orig_pos in self._multi_drag_ghosts:
                if other_ghost.uid in falloff_uids:
                    continue
                other_new_val = orig_val + value_delta
                other_ghost.local_value = other_new_val

                # Update the other ghost's f-curve
                other_obj = bpy.data.objects.get(other_ghost.object_name)
                if other_obj:
                    other_fc = fcurve_utils.resolve_fcurve(
                        other_obj, other_ghost.bone_name, other_ghost.channel
                    )
                    if other_fc:
                        mode = context.scene.ghost_tool.curve_mode.lower()
                        fcurve_utils.recalculate_handles(
                            other_fc, other_ghost.frame, other_new_val, mode=mode
                        )

    def _preview_model_a(
        self,
        fcurve: bpy.types.FCurve,
        frame: float,
        value: float,
    ) -> None:
        """Live preview for Model A: insert or update a temporary keyframe.

        On the first call, inserts a new keyframe at the ghost's frame.
        On subsequent calls, updates the temp key's value without reinserting.
        This gives the user an accurate preview of what the curve will look
        like with a real key at this position.

        Args:
            fcurve: The f-curve being edited.
            frame: The ghost's frame number.
            value: The new f-curve value at this frame.
        """
        if not self._temp_key_inserted:
            # Check if a real keyframe already exists at this frame
            existing = fcurve_utils.get_keyframe_at_frame(fcurve, frame, tolerance=0.01)
            if existing:
                # Real keyframe exists — modify it, don't insert a duplicate
                existing.co.y = value
                fcurve.update()
                self._temp_key_inserted = True
                self._reusing_existing_key = True
            else:
                # Insert new temp key
                keyframe = fcurve.keyframe_points.insert(
                    frame, value, options={'FAST'}
                )
                keyframe.handle_left_type = 'AUTO_CLAMPED'
                keyframe.handle_right_type = 'AUTO_CLAMPED'
                keyframe.interpolation = 'BEZIER'
                fcurve.update()
                self._temp_key_inserted = True
        else:
            # Subsequent calls — just update the value of the existing temp key
            existing = fcurve_utils.get_keyframe_at_frame(fcurve, frame, tolerance=0.01)
            if existing:
                existing.co.y = value
                fcurve.update()

    def _confirm_drag(self, context: bpy.types.Context) -> None:
        """Finalize the drag operation.

        Checks the editing mode to decide the commit strategy:
        - RESHAPE (Model B): keep the recalculated handles (already applied
          during the modal loop via ``recalculate_handles``).
        - INSERT_KEY (Model A): insert a real keyframe at the ghost's frame
          using the dragged value, turning the ghost into a key.

        Pushes the change to Blender's undo stack and deselects the ghost.
        Fires any registered ghost-moved callbacks via the API.

        Args:
            context: The current Blender context.
        """
        ghost = self._active_ghost
        editing_mode = self._editing_mode

        if ghost:
            # --- Model A: Insert Keyframe ---
            # The temp key was already inserted during the drag preview.
            # On confirm, we just keep it and finalize the handles.
            if editing_mode == 'INSERT_KEY' and self._temp_key_inserted:
                obj = bpy.data.objects.get(ghost.object_name)
                if obj:
                    fcurve = fcurve_utils.resolve_fcurve(
                        obj, ghost.bone_name, ghost.channel
                    )
                    if fcurve:
                        # Ensure the temp key has clean handle types
                        temp_key = fcurve_utils.get_keyframe_at_frame(
                            fcurve, ghost.frame, tolerance=0.01
                        )
                        if temp_key:
                            temp_key.handle_left_type = 'AUTO_CLAMPED'
                            temp_key.handle_right_type = 'AUTO_CLAMPED'
                            fcurve.update()

                            # Optionally smooth neighboring handles
                            smooth = context.scene.ghost_tool.smooth_neighbors_on_commit
                            if smooth:
                                left_kp, right_kp = fcurve_utils.get_adjacent_keyframes(fcurve, ghost.frame)
                                if left_kp and right_kp:
                                    # Apply smooth recalculation to blend the new key into the curve
                                    fcurve_utils.recalculate_handles(
                                        fcurve, ghost.frame, ghost.local_value, mode="smooth"
                                    )

                            log(f"Model A: Confirmed keyframe at f{ghost.frame:.1f}")
                        else:
                            warn(f"Model A: Temp key lost at f{ghost.frame:.1f}")

                # Mark cache dirty so live mode regenerates ghosts
                try:
                    from .ghost_cache import GhostCache
                    cache = GhostCache.get(context.scene)
                    cache.mark_dirty()
                except Exception as exc:
                    debug(f"Failed to mark cache dirty after drag: {exc}")

            # Clear selection via SessionState
            session = SessionState.get(context.scene)
            session.clear_selection()

            # Fire callbacks for external addon integration
            try:
                from . import api as ghost_api
                ghost_api._fire_ghost_moved(ghost.uid)
            except Exception as exc:
                debug(f"Ghost moved callback error: {exc}")

        # Push to undo stack
        undo_label = (
            "Ghost Tool: Insert Keyframe" if editing_mode == 'INSERT_KEY'
            else "Ghost Tool: Move Ghost"
        )
        bpy.ops.ed.undo_push(message=undo_label)

        self._cleanup()
        tag_viewport_redraw(context)

    def _cancel_drag(self, context: bpy.types.Context) -> None:
        """Cancel the drag operation and restore original f-curve state.

        All affected f-curves are reverted to their pre-drag snapshots.

        Args:
            context: The current Blender context.
        """
        ghost = self._active_ghost
        if ghost:
            # Restore ghost position
            ghost.world_position = self._original_position.copy()
            ghost.local_value = self._original_local_value

        for neighbor, original_value, _weight in self._falloff_neighbors:
            neighbor.local_value = original_value
        for other, original_value, original_position in self._multi_drag_ghosts:
            other.local_value = original_value
            other.world_position = original_position.copy()

        # Clear selection via SessionState
        session = SessionState.get(context.scene)
        session.clear_selection()

        # For Model A cancel, remove the temp key before restoring the snapshot.
        # restore_fcurve only writes values for existing keyframes — it cannot
        # remove an extra keyframe that was inserted during the drag preview.
        # Only remove if we inserted a new key (not reusing an existing one).
        if self._editing_mode == 'INSERT_KEY' and self._temp_key_inserted and ghost and not self._reusing_existing_key:
            for fc_key, fcurve in self._affected_fcurves.items():
                if fcurve:
                    temp_key = fcurve_utils.get_keyframe_at_frame(
                        fcurve, ghost.frame, tolerance=0.01
                    )
                    if temp_key:
                        try:
                            fcurve.keyframe_points.remove(temp_key)
                        except Exception as exc:
                            debug(f"Failed to remove temp key: {exc}")

        # Restore all affected f-curves to pre-drag state
        for fcurve_key, snapshot in self._undo_snapshots.items():
            fcurve = self._affected_fcurves.get(fcurve_key)
            if fcurve:
                fcurve_utils.restore_fcurve(fcurve, snapshot)

        self._cleanup()
        tag_viewport_redraw(context)
        self.report({'INFO'}, "Ghost drag cancelled")

    def _cleanup(self) -> None:
        """Reset internal state after drag completion or cancellation."""
        session = getattr(self, "_drag_session", None)
        if session is not None:
            session.drag_active = False
            self._drag_session = None
        self._active_ghost = None
        self._original_position = None
        self._original_local_value = 0.0
        self._axis_constraint = "NONE"
        self._undo_snapshots = {}
        self._affected_fcurves = {}
        self._editing_mode = "RESHAPE"
        self._temp_key_inserted = False
        self._reusing_existing_key = False
        self._falloff_neighbors = []
        self._transform_space = "WORLD"
        self._multi_drag_ghosts = []


# ---------------------------------------------------------------------------
# Generate Ghosts Operator
# ---------------------------------------------------------------------------

class GHOST_OT_generate(bpy.types.Operator):
    """Generate ghost markers for the active object and selected bones.

    Samples f-curves at midpoints between keyframes and creates Ghost
    objects for visualization and manipulation.
    """

    bl_idname = "ghost_tool.generate_ghosts"
    bl_label = "Generate Ghosts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Require an active object with animation data.

        Args:
            context: The current Blender context.

        Returns:
            bool: True if generation can proceed.
        """
        obj = context.active_object
        if not obj:
            return False
        if not obj.animation_data or not obj.animation_data.action:
            return False
        return True

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Run ghost generation via the pipeline.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'} on success.
        """
        from .ghost_data import LOCATION_CHANNELS
        from .ghost_pipeline import GhostPipeline

        obj = context.active_object
        settings = context.scene.ghost_tool

        # Determine bones to process
        bones: list[str] = []
        armature = None

        if obj.type == 'ARMATURE':
            armature = obj
            # Use selected pose bones, or all if none selected
            if context.selected_pose_bones:
                bones = [b.name for b in context.selected_pose_bones]
            elif obj.pose and obj.pose.bones:
                # Fallback: try pose bones with selection, or use all bones
                bones = [
                    b.name for b in obj.pose.bones
                    if getattr(b.bone, 'select', False)
                ]
                if not bones:
                    bones = [b.name for b in obj.pose.bones]

        # Determine frame range from range_mode settings.
        # ghost_range_mode: AROUND_CURSOR, FULL_TIMELINE, BETWEEN_KEYS, or CUSTOM
        frame_range = None
        range_mode = settings.ghost_range_mode

        if range_mode == "CUSTOM":
            frame_range = (settings.custom_range_start, settings.custom_range_end)
        elif range_mode == "FULL_TIMELINE":
            frame_range = (context.scene.frame_start, context.scene.frame_end)
        # AROUND_CURSOR and BETWEEN_KEYS are handled inside the pipeline

        # Generate for location channels by default
        channels = LOCATION_CHANNELS

        # Route through the pipeline for cache awareness
        pipeline = GhostPipeline.get(context.scene)
        count = pipeline.generate_manual(
            context=context,
            obj=obj,
            armature=armature,
            bones=bones,
            channels=channels,
            level=settings.subdivision_level,
            frame_range=frame_range,
            clear_existing=True,
        )

        # Activate display and live updates
        settings.is_active = True
        settings.live_point_ghosts = True

        # Auto-start hover detection so highlight rings and frame labels work
        GHOST_OT_hover_detect.ensure_running(context)

        # ghost_mode determines generation strategy: SUBDIVISION, FRAME_STEP, or KEYFRAMES_ONLY
        mode_label = settings.ghost_mode
        range_label = range_mode.replace('_', ' ').title()
        self.report({'INFO'}, f"Generated {count} ghosts ({mode_label}, {range_label})")
        tag_viewport_redraw(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Clear Ghosts Operator
# ---------------------------------------------------------------------------

class GHOST_OT_clear(bpy.types.Operator):
    """Remove all ghosts from the current scene.

    Clears the ghost store, invalidates the cache, and optionally clears
    any mesh ghost objects if they exist.
    """

    bl_idname = "ghost_tool.clear_ghosts"
    bl_label = "Clear All Ghosts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Clear the ghost store, cache, and any mesh ghosts.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'}.
        """
        from .ghost_pipeline import GhostPipeline

        # Clear point ghosts via pipeline (also clears cache)
        pipeline = GhostPipeline.get(context.scene)
        count = pipeline.clear(context)

        # Also clear mesh ghosts if they exist
        try:
            from .mesh_ghosts import clear_mesh_ghosts
            mesh_count = clear_mesh_ghosts(context)
            if mesh_count > 0:
                count += mesh_count
        except ImportError:
            debug("mesh_ghosts module not available for clear")

        self.report({'INFO'}, f"Cleared {count} ghosts")
        tag_viewport_redraw(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Pin / Unpin Ghost Operators
# ---------------------------------------------------------------------------

class GHOST_OT_pin_ghost(bpy.types.Operator):
    """Toggle pin state on the ghost nearest to the cursor."""

    bl_idname = "ghost_tool.pin_ghost"
    bl_label = "Pin/Unpin Ghost"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Require active ghost display.

        Args:
            context: The current Blender context.

        Returns:
            bool: True if ghost display is active.
        """
        return hasattr(context.scene, 'ghost_tool') and context.scene.ghost_tool.is_active

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Find and toggle the pin state of the nearest ghost.

        Args:
            context: The current Blender context.
            event: The triggering event.

        Returns:
            set[str]: {'FINISHED'} or {'CANCELLED'}.
        """
        settings = context.scene.ghost_tool
        ghost = _find_ghost_under_cursor(
            context, event.mouse_region_x, event.mouse_region_y,
            settings.grab_radius,
        )

        if ghost is None:
            self.report({'WARNING'}, "No ghost under cursor to pin")
            return {'CANCELLED'}

        ghost.is_pinned = not ghost.is_pinned
        state = "pinned" if ghost.is_pinned else "unpinned"
        self.report({'INFO'}, f"Ghost {state} at frame {ghost.frame:.1f}")
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_unpin_all(bpy.types.Operator):
    """Unpin all pinned ghosts in the current scene.

    Iterates through the ghost store and resets the is_pinned flag on all
    ghosts that are currently pinned.
    """

    bl_idname = "ghost_tool.unpin_all"
    bl_label = "Unpin All Ghosts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Unpin every ghost.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'}.
        """
        store = GhostStore.get(context.scene)
        count = 0
        for ghost in store:
            if ghost.is_pinned:
                ghost.is_pinned = False
                count += 1
        self.report({'INFO'}, f"Unpinned {count} ghosts")
        tag_viewport_redraw(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Hover Detection Operator (timer-based)
# ---------------------------------------------------------------------------

class GHOST_OT_hover_detect(bpy.types.Operator):
    """Modal operator that runs a lightweight timer to track which ghost
    is under the cursor.

    While active it continuously updates ``SessionState.hovered_ghost_uid``
    so the draw handler can render highlight rings and frame labels.
    The operator self-terminates when ghost display is deactivated.

    Lifecycle:
        - Auto-started by ``GHOST_OT_generate`` after ghost generation.
        - Self-terminates when ``is_active`` goes False or ghosts are cleared.
        - Has a ``force_reset()`` classmethod for recovery from stuck state.
        - Auto-resets if no modal events received for 10 seconds.
    """

    bl_idname = "ghost_tool.hover_detect"
    bl_label = "Ghost Hover Detect"
    bl_options = set()  # No undo — this is purely visual state

    _timer: Optional[object] = None
    _running: bool = False
    _last_mouse_x: int = -1
    _last_mouse_y: int = -1
    _last_activity: float = 0.0

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Allow only when ghost display is active and not already running.

        Also auto-resets if no modal events received for 10 seconds (timeout).
        """
        if cls._running:
            # Auto-reset if no modal events received for 10 seconds
            import time
            if cls._last_activity > 0 and time.time() - cls._last_activity > 10.0:
                cls._running = False
                cls._timer = None
                return False
            return False
        return (
            hasattr(context.scene, 'ghost_tool')
            and context.scene.ghost_tool.is_active
        )

    @classmethod
    def force_reset(cls) -> None:
        """Reset the running flag without a context.

        Call this if the operator gets stuck (e.g. exception during modal).
        After calling, the operator can be re-invoked normally.
        """
        cls._running = False
        cls._timer = None
        cls._last_activity = 0.0

    @classmethod
    def ensure_running(cls, context: bpy.types.Context) -> None:
        """Start hover detection if it is not already running.

        Safe to call repeatedly — no-ops if already active.

        Args:
            context: The current Blender context (must have a window).
        """
        if cls._running:
            return
        if not hasattr(context.scene, 'ghost_tool'):
            return
        if not context.scene.ghost_tool.is_active:
            return
        try:
            bpy.ops.ghost_tool.hover_detect('INVOKE_DEFAULT')
        except Exception as exc:
            debug(f"Could not auto-start hover detection: {exc}")

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Start the hover-tracking timer.

        Args:
            context: The current Blender context.
            event: The triggering event.

        Returns:
            set[str]: {'RUNNING_MODAL'}.
        """
        import time
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, window=context.window)
        wm.modal_handler_add(self)
        GHOST_OT_hover_detect._running = True
        GHOST_OT_hover_detect._last_activity = time.time()
        self._last_mouse_x = -1
        self._last_mouse_y = -1
        debug("Hover detection started")
        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Update hover state on timer tick and mouse moves.

        Wrapped in try/except so an unhandled error cannot leave _running
        stuck True, which would permanently disable hover detection.

        Args:
            context: The current Blender context.
            event: The current event.

        Returns:
            set[str]: Modal state.
        """
        try:
            return self._modal_inner(context, event)
        except Exception as exc:
            warn(f"Hover detection error — stopping: {exc}")
            self._stop(context)
            return {'CANCELLED'}

    def _modal_inner(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ) -> set[str]:
        """Core modal logic, separated for clean error handling."""
        import time
        # Update activity timestamp on any event
        GHOST_OT_hover_detect._last_activity = time.time()

        # Self-terminate when ghost display is off
        if not hasattr(context.scene, 'ghost_tool') or not context.scene.ghost_tool.is_active:
            self._stop(context)
            return {'CANCELLED'}

        # Only scan on MOUSEMOVE (skip TIMER if mouse hasn't moved)
        if event.type == 'MOUSEMOVE':
            self._last_mouse_x = event.mouse_region_x
            self._last_mouse_y = event.mouse_region_y
            self._do_hover_scan(context)
        elif event.type == 'TIMER':
            # Timer tick — only scan if we have valid mouse coords and mouse moved
            if self._last_mouse_x >= 0:
                self._do_hover_scan(context)

        return {'PASS_THROUGH'}

    def _do_hover_scan(self, context: bpy.types.Context) -> None:
        """Run the proximity scan and update hover state."""
        settings = context.scene.ghost_tool
        grab_radius = settings.grab_radius
        session = SessionState.get(context.scene)

        ghost = _find_ghost_under_cursor(
            context, self._last_mouse_x, self._last_mouse_y, grab_radius,
        )

        new_uid = ghost.uid if ghost else None
        if new_uid != session.hovered_ghost_uid:
            session.set_hover(new_uid)
            tag_viewport_redraw(context)

    def _stop(self, context: bpy.types.Context) -> None:
        """Remove timer and clear running flag."""
        if self._timer is not None:
            try:
                context.window_manager.event_timer_remove(self._timer)
            except Exception as exc:
                debug(f"Failed to remove timer: {exc}")
            self._timer = None
        GHOST_OT_hover_detect._running = False
        try:
            SessionState.get(context.scene).clear_hover()
        except Exception as exc:
            debug(f"Failed to clear hover state: {exc}")
        debug("Hover detection stopped")


# ---------------------------------------------------------------------------
# Ghost Select Operator (click / shift-click)
# ---------------------------------------------------------------------------

class GHOST_OT_select_ghost(bpy.types.Operator):
    """Select or toggle-select the ghost under the cursor.

    Plain click: select one ghost (clear others).
    Shift-click: toggle the ghost in/out of the multi-selection set.
    """

    bl_idname = "ghost_tool.select_ghost"
    bl_label = "Select Ghost"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Require active ghost display with ghosts."""
        if not hasattr(context.scene, 'ghost_tool'):
            return False
        if not context.scene.ghost_tool.is_active:
            return False
        return len(GhostStore.get(context.scene)) > 0

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Pick the ghost under the cursor and update selection.

        Args:
            context: The current Blender context.
            event: The triggering event (expects mouse click).

        Returns:
            set[str]: {'FINISHED'} or {'CANCELLED'}.
        """
        settings = context.scene.ghost_tool
        ghost = _find_ghost_under_cursor(
            context, event.mouse_region_x, event.mouse_region_y,
            settings.grab_radius,
        )

        session = SessionState.get(context.scene)

        if ghost is None:
            # Click on empty space → clear selection
            session.clear_selection()
            tag_viewport_redraw(context)
            return {'CANCELLED'}

        if event.shift:
            session.toggle_selection(ghost.uid)
        else:
            session.select_only(ghost.uid)

        tag_viewport_redraw(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    GhostDragOperator,
    GHOST_OT_generate,
    GHOST_OT_clear,
    GHOST_OT_pin_ghost,
    GHOST_OT_unpin_all,
    GHOST_OT_hover_detect,
    GHOST_OT_select_ghost,
)


def register() -> None:
    """Register all modal operator classes."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister all modal operator classes."""
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


# ---------------------------------------------------------------------------
# Test notes
# ---------------------------------------------------------------------------
#
# Test 1: Operator poll
# >>> # With a cube with 3 keyframes and ghosts generated:
# >>> bpy.ops.ghost_tool.drag_ghost('INVOKE_DEFAULT')
# >>> # Should enter modal mode if cursor is near a ghost
#
# Test 2: Axis constraints
# >>> # During drag, press X → ghost should only move along X axis
# >>> # Press SHIFT+X → ghost moves in YZ plane
# >>> # Press X again → constraint released
#
# Test 3: Cancel restores original
# >>> # Drag a ghost, then press ESC
# >>> # F-curve should return to pre-drag state
#
# Test 4: Undo after confirm
# >>> # Drag and release left mouse → Ctrl+Z should undo the move
