"""
session_state.py — Centralized transient state for Ghost Tool viewport interaction.

This module owns all per-scene session-local state that does NOT survive
undo/redo or file save/load.  It provides a single ``SessionState`` class
holding:

- **hovered_ghost_uid**: The uid of the ghost currently under the cursor
  (used by the draw handler for highlight rendering and frame label display).
- **selection_set**: A set of ghost uids that are actively selected
  (populated via shift-click; used by the draw handler for multi-select rings).

Design notes:
    - One ``SessionState`` instance per scene, accessed via ``SessionState.get(scene)``.
    - All fields are transient — regenerating ghosts clears hover/selection
      because ghost uids change on regeneration.
    - Drawing code reads from this module.  Interaction code writes to it.
    - No Blender PropertyGroup is used — this is pure Python in-memory state.
"""

from __future__ import annotations

from typing import Optional

import bpy
from .utils import get_scene_id, debug


class SessionState:
    """Per-scene transient state for viewport interaction.

    Holds hover and selection information that the draw handler reads
    and modal operators write.  Cleared automatically when ghosts are
    regenerated (because uids change).

    Usage:
        state = SessionState.get(context.scene)
        state.hovered_ghost_uid = ghost.uid
        state.toggle_selection(ghost.uid)
    """

    # Class-level dict mapping scene names to SessionState instances.
    _instances: dict[str, SessionState] = {}

    def __init__(self) -> None:
        """Initialize with empty hover and selection state."""
        self.hovered_ghost_uid: Optional[str] = None
        self.selection_set: set[str] = set()
        self.drag_active = False

    # --- Singleton access per scene ---

    @classmethod
    def get(cls, scene: bpy.types.Scene) -> SessionState:
        """Retrieve or create the SessionState for the given scene.

        Args:
            scene: The Blender scene to look up.

        Returns:
            SessionState: The state associated with this scene.
        """
        key = get_scene_id(scene)
        if key not in cls._instances:
            cls._instances[key] = cls()
        return cls._instances[key]

    @classmethod
    def clear_all_instances(cls) -> None:
        """Remove all SessionState instances (used during addon unregistration)."""
        cls._instances.clear()

    # --- Hover management ---

    def set_hover(self, ghost_uid: Optional[str]) -> None:
        """Set the currently hovered ghost uid.

        Args:
            ghost_uid: The uid of the ghost under the cursor, or None to clear.
        """
        self.hovered_ghost_uid = ghost_uid

    def clear_hover(self) -> None:
        """Clear the hover state."""
        self.hovered_ghost_uid = None

    # --- Selection management ---

    def select(self, ghost_uid: str) -> None:
        """Add a ghost to the selection set (shift-click behavior).

        Args:
            ghost_uid: The uid of the ghost to select.
        """
        self.selection_set.add(ghost_uid)

    def deselect(self, ghost_uid: str) -> None:
        """Remove a ghost from the selection set.

        Args:
            ghost_uid: The uid of the ghost to deselect.
        """
        self.selection_set.discard(ghost_uid)

    def toggle_selection(self, ghost_uid: str) -> None:
        """Toggle a ghost's selection state (for shift-click).

        Args:
            ghost_uid: The uid of the ghost to toggle.
        """
        if ghost_uid in self.selection_set:
            self.selection_set.discard(ghost_uid)
        else:
            self.selection_set.add(ghost_uid)

    def select_only(self, ghost_uid: str) -> None:
        """Select exactly one ghost, clearing all others (plain click).

        Args:
            ghost_uid: The uid of the ghost to select.
        """
        self.selection_set.clear()
        self.selection_set.add(ghost_uid)

    def clear_selection(self) -> None:
        """Clear the entire selection set."""
        self.selection_set.clear()

    def is_selected(self, ghost_uid: str) -> bool:
        """Check whether a ghost is in the selection set.

        Args:
            ghost_uid: The uid to check.

        Returns:
            bool: True if the ghost is selected.
        """
        return ghost_uid in self.selection_set

    # --- Bulk reset ---

    def clear_all(self) -> None:
        """Reset all transient state (called after ghost regeneration)."""
        self.hovered_ghost_uid = None
        self.selection_set.clear()
        self.drag_active = False


# ---------------------------------------------------------------------------
# Undo/Redo Handler
# ---------------------------------------------------------------------------

@bpy.app.handlers.persistent
def _on_undo_redo(scene: bpy.types.Scene, *args) -> None:
    """Clear transient session state and invalidate caches after undo/redo.

    Ghost UIDs change when ghosts are regenerated, so any stored UIDs
    in hover/selection state become stale after undo. This handler
    clears all transient state to prevent referencing nonexistent ghosts.

    Also invalidates ghost caches and marks the pipeline dirty so stale
    ghosts don't persist when f-curve state changes during undo/redo.

    Args:
        scene: The scene that was affected by undo/redo.
    """
    if scene is None or not isinstance(scene, bpy.types.Scene):
        scene = bpy.context.scene
    if scene is None:
        return

    # Clear transient session state (hover, selection)
    state = SessionState.get(scene)
    state.clear_all()

    # Invalidate caches so stale ghosts don't persist after undo
    from .ghost_cache import GhostCache
    from .ghost_pipeline import GhostPipeline
    from .fcurve_utils import invalidate_keyframe_cache, clear_frame_cache

    cache = GhostCache.get(scene)
    cache.invalidate_all()

    pipeline = GhostPipeline.get(scene)
    pipeline.mark_dirty()

    # Clear sorted keyframe cache (keyframe edits may have been undone)
    invalidate_keyframe_cache()
    clear_frame_cache()

    # Undo can move any motion path and no depsgraph update says which: re-sample them all
    from .motion_paths import clear_cache
    clear_cache()
    from .ghost_pipeline import _schedule_deferred_update
    _schedule_deferred_update()
