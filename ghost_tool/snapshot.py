"""
snapshot.py — Ghost snapshot storage, comparison, and restoration.

Snapshots freeze the current ghost configuration as a reference overlay.
Animators can compare their current motion timing against previous states,
or restore f-curves to a snapshot's values.

Snapshots are stored per-scene and survive within a Blender session.
For cross-session persistence, use the export/import system.
"""

from __future__ import annotations

import time
import math
import copy
import uuid
from dataclasses import dataclass, field
from typing import Optional

import bpy
from mathutils import Vector

from .ghost_data import GhostStore, Ghost
from .utils import log, warn, debug, get_scene_id, tag_viewport_redraw


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_SNAPSHOTS: int = 10
"""Maximum number of snapshots per scene (FIFO eviction beyond this)."""


# ---------------------------------------------------------------------------
# GhostSnapshot Dataclass
# ---------------------------------------------------------------------------

@dataclass
class GhostSnapshot:
    """A frozen copy of a ghost configuration for reference comparison.

    Attributes:
        name: User-provided name for the snapshot.
        uid: Unique identifier.
        timestamp: Unix timestamp when the snapshot was taken.
        ghost_data: List of ghost dicts (serialized Ghost objects).
        object_names: Set of object names involved in this snapshot.
        bone_names: Set of bone names involved.
        is_visible: Whether this snapshot should be drawn as an overlay.
    """

    name: str
    uid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: float = field(default_factory=time.time)
    ghost_data: list[dict] = field(default_factory=list)
    object_names: set[str] = field(default_factory=set)
    bone_names: set[str] = field(default_factory=set)
    is_visible: bool = True
    curve_data: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize the snapshot for JSON export.

        Returns:
            dict: All snapshot fields as JSON-serializable types.
        """
        return {
            "name": self.name,
            "uid": self.uid,
            "timestamp": self.timestamp,
            "ghost_data": self.ghost_data,
            "object_names": list(self.object_names),
            "bone_names": list(self.bone_names),
            "is_visible": self.is_visible,
            "curve_data": copy.deepcopy(self.curve_data),
        }

    @classmethod
    def from_dict(cls, data: dict) -> GhostSnapshot:
        """Deserialize a snapshot from a dictionary.

        Args:
            data: Dictionary with snapshot field values.

        Returns:
            GhostSnapshot: Reconstructed snapshot.
        """
        if not isinstance(data, dict):
            raise ValueError("Snapshot must be an object")
        for name in ('name', 'uid'):
            if name in data and (not isinstance(data[name], str) or not data[name]):
                raise ValueError(f"Invalid snapshot {name}")
        for name in ('ghost_data', 'curve_data', 'object_names', 'bone_names'):
            if name in data and not isinstance(data[name], list):
                raise ValueError(f"Snapshot {name} must be a list")
        for name in ('object_names', 'bone_names'):
            if any(not isinstance(value, str) for value in data.get(name, [])):
                raise ValueError(f"Invalid snapshot {name}")
        if not isinstance(data.get('timestamp', 0), (int, float)) or not math.isfinite(data.get('timestamp', 0)):
            raise ValueError("Invalid snapshot timestamp")
        if type(data.get('is_visible', True)) is not bool:
            raise ValueError("Invalid snapshot visibility")
        ghosts = [Ghost.from_dict(value).to_dict() for value in data.get('ghost_data', [])]
        for curve in data.get('curve_data', []):
            if not isinstance(curve, dict) or any(not isinstance(curve.get(k), str) for k in ('object_name', 'bone_name', 'channel')):
                raise ValueError("Invalid snapshot curve reference")
            from .fcurve_utils import validate_curve_snapshot
            validate_curve_snapshot(curve.get('keys'))
        return cls(
            name=data.get("name", "Unnamed"),
            uid=data.get("uid", uuid.uuid4().hex[:8]),
            timestamp=data.get("timestamp", time.time()),
            ghost_data=ghosts,
            curve_data=copy.deepcopy(data.get("curve_data", [])),
            object_names=set(data.get("object_names", [])),
            bone_names=set(data.get("bone_names", [])),
            is_visible=data.get("is_visible", True),
        )


# ---------------------------------------------------------------------------
# SnapshotStore — Per-scene snapshot container
# ---------------------------------------------------------------------------

class SnapshotStore:
    """Scene-level container for ghost snapshots.

    Follows the same singleton-per-scene pattern as GhostStore.
    Enforces a maximum count via FIFO eviction.

    Usage:
        snap_store = SnapshotStore.get(context.scene)
        snap_store.take_snapshot("Before adjustment")
        snap_store.restore_snapshot(snapshot_uid)
    """

    _instances: dict[str, SnapshotStore] = {}

    def __init__(self) -> None:
        """Initialize an empty snapshot store."""
        self._snapshots: list[GhostSnapshot] = []
        self._index: dict[str, GhostSnapshot] = {}

    @classmethod
    def get(cls, scene: bpy.types.Scene) -> SnapshotStore:
        """Retrieve or create the SnapshotStore for the given scene.

        Args:
            scene: The Blender scene.

        Returns:
            SnapshotStore: The store for this scene.
        """
        key = get_scene_id(scene)
        if key not in cls._instances:
            cls._instances[key] = cls()
        return cls._instances[key]

    @classmethod
    def clear_all_instances(cls) -> None:
        """Remove all SnapshotStore instances (used during addon unregistration)."""
        cls._instances.clear()

    # --- Snapshot operations ---

    def take_snapshot(self, name: str, scene: bpy.types.Scene) -> tuple[GhostSnapshot, Optional[str]]:
        """Freeze the current ghost configuration as a snapshot.

        If the store is at capacity, the oldest snapshot is evicted.

        Args:
            name: Human-readable name for the snapshot.
            scene: The Blender scene to read ghosts from.

        Returns:
            tuple[GhostSnapshot, Optional[str]]: The newly created snapshot and the name of
                the evicted snapshot (if any), so callers can report it to the user via UI.
        """
        ghost_store = GhostStore.get(scene)

        # Serialize current ghost state
        ghost_data = ghost_store.to_dict_list()

        # Collect involved objects and bones
        object_names = set()
        bone_names = set()
        for ghost_entry in ghost_data:
            object_names.add(ghost_entry.get("object_name", ""))
            # Extract bone name if present (empty string means no bone constraint)
            bone_name = ghost_entry.get("bone_name", "")
            if bone_name:
                bone_names.add(bone_name)

        from . import fcurve_utils
        curves = []
        seen = set()
        for ghost in ghost_store:
            key = (ghost.object_name, ghost.bone_name, ghost.channel)
            if key in seen:
                continue
            seen.add(key)
            obj = scene.objects.get(ghost.object_name)
            curve = fcurve_utils.resolve_fcurve(obj, ghost.bone_name, ghost.channel)
            if curve is not None:
                curves.append(dict(object_name=ghost.object_name, bone_name=ghost.bone_name,
                                   channel=ghost.channel, keys=fcurve_utils.snapshot_fcurve(curve)))

        snapshot = GhostSnapshot(
            name=name,
            ghost_data=ghost_data,
            curve_data=curves,
            object_names=object_names,
            bone_names=bone_names,
        )

        # Evict oldest if at capacity
        evicted_name = None
        if len(self._snapshots) >= MAX_SNAPSHOTS:
            oldest = self._snapshots.pop(0)
            self._index.pop(oldest.uid, None)
            evicted_name = oldest.name
            warn(f"Evicted oldest snapshot: '{oldest.name}'")

        self._snapshots.append(snapshot)
        self._index[snapshot.uid] = snapshot

        return snapshot, evicted_name

    def restore_snapshot(self, snapshot_uid: str, scene: bpy.types.Scene) -> bool:
        """Restore f-curves to match a snapshot's ghost values.

        Writes each ghost's stored local_value back through the f-curve
        recalculation system.

        Args:
            snapshot_uid: UID of the snapshot to restore.
            scene: The Blender scene to modify.

        Returns:
            bool: True if restoration succeeded, False otherwise.
        """
        from . import fcurve_utils

        snapshot = self._index.get(snapshot_uid)
        if snapshot is None:
            warn(f"Snapshot '{snapshot_uid}' not found")
            return False

        if snapshot.curve_data:
            targets = []
            for entry in snapshot.curve_data:
                obj = scene.objects.get(entry['object_name'])
                curve = fcurve_utils.resolve_fcurve(obj, entry['bone_name'], entry['channel'])
                if curve is None:
                    warn("Snapshot restore aborted: an original curve is missing")
                    return False
                targets.append((curve, entry['keys'], fcurve_utils.snapshot_fcurve(curve)))
            try:
                for curve, keys, _backup in targets:
                    if not fcurve_utils.restore_fcurve(curve, keys):
                        raise ValueError("Snapshot curve restore failed")
            except Exception as exc:
                for curve, _keys, backup in targets:
                    fcurve_utils.restore_fcurve(curve, backup)
                warn(str(exc))
                return False
            from .ghost_pipeline import GhostPipeline
            GhostPipeline.get(scene).mark_dirty()
            if scene == bpy.context.scene:
                from .api import refresh_ghosts
                refresh_ghosts()
            tag_viewport_redraw(bpy.context)
            return True

        # Legacy snapshots contain ghost samples only, so use their original
        # approximate handle-restoration behavior for backward compatibility.
        restored_count = 0
        skipped = 0
        for gd in snapshot.ghost_data:
            obj_name = gd.get("object_name", "")
            bone_name = gd.get("bone_name", "")
            channel = gd.get("channel", "")
            frame = gd.get("frame", 0.0)
            local_value = gd.get("local_value", 0.0)

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                skipped += 1
                continue

            fcurve = fcurve_utils.resolve_fcurve(obj, bone_name, channel)
            if fcurve is None:
                skipped += 1
                continue

            settings = scene.ghost_tool
            # Mode defaults to "free" if not explicitly set in curve_mode property
            mode = settings.curve_mode.lower() if hasattr(settings, 'curve_mode') else "free"

            if fcurve_utils.recalculate_handles(fcurve, frame, local_value, mode=mode):
                restored_count += 1

        log(f"Restored {restored_count} ghost values from snapshot '{snapshot.name}'")
        if skipped > 0:
            warn(f"Skipped {skipped} ghost(s) during restoration (missing objects/bones)")
        return restored_count > 0

    def toggle_visibility(self, snapshot_uid: str) -> bool:
        """Toggle the visibility of a snapshot overlay.

        Args:
            snapshot_uid: UID of the snapshot.

        Returns:
            bool: The new visibility state, or False if not found.
        """
        snapshot = self._index.get(snapshot_uid)
        if snapshot is None:
            return False
        snapshot.is_visible = not snapshot.is_visible
        return snapshot.is_visible

    def delete_snapshot(self, snapshot_uid: str) -> bool:
        """Delete a snapshot permanently.

        Args:
            snapshot_uid: UID of the snapshot to delete.

        Returns:
            bool: True if the snapshot was found and deleted.
        """
        snapshot = self._index.pop(snapshot_uid, None)
        if snapshot is None:
            return False
        try:
            self._snapshots.remove(snapshot)
        except ValueError:
            warn(f"Snapshot '{snapshot_uid}' not found in list (index/list mismatch)")
        return True

    def get_visible(self) -> list[GhostSnapshot]:
        """Return all snapshots that are currently set to visible.

        Returns:
            list[GhostSnapshot]: Visible snapshots.
        """
        return [s for s in self._snapshots if s.is_visible]

    def get_all(self) -> list[GhostSnapshot]:
        """Return all snapshots.

        Returns:
            list[GhostSnapshot]: All snapshots in the store.
        """
        return list(self._snapshots)

    def get_by_uid(self, uid: str) -> Optional[GhostSnapshot]:
        """Look up a snapshot by UID.

        Args:
            uid: The snapshot UID.

        Returns:
            GhostSnapshot or None.
        """
        return self._index.get(uid)

    def to_dict_list(self) -> list[dict]:
        """Serialize all snapshots for export.

        Returns:
            list[dict]: Serialized snapshots.
        """
        return [s.to_dict() for s in self._snapshots]

    def load_from_dict_list(self, data: list[dict]) -> None:
        """Load snapshots from serialized data (import).

        Args:
            data: List of snapshot dictionaries.
        """
        snapshots = [GhostSnapshot.from_dict(item) for item in data]
        if len({snapshot.uid for snapshot in snapshots}) != len(snapshots):
            raise ValueError("Duplicate snapshot IDs")
        self._snapshots = snapshots[-MAX_SNAPSHOTS:]
        self._index = {snapshot.uid: snapshot for snapshot in self._snapshots}


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class GHOST_OT_take_snapshot(bpy.types.Operator):
    """Take a snapshot of the current ghost configuration."""

    bl_idname = "ghost_tool.take_snapshot"
    bl_label = "Take Snapshot"
    bl_options = {'REGISTER'}

    snapshot_name: bpy.props.StringProperty(
        name="Name",
        description="Name for this snapshot",
        default="Snapshot",
    )  # type: ignore[assignment]

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Create a new snapshot.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'}.
        """
        store = SnapshotStore.get(context.scene)
        snapshot, evicted_name = store.take_snapshot(self.snapshot_name, context.scene)
        self.report({'INFO'}, f"Snapshot '{snapshot.name}' taken ({len(snapshot.ghost_data)} ghosts)")
        if evicted_name:
            self.report({'WARNING'}, f"Snapshot limit reached; evicted oldest: '{evicted_name}'")
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_restore_snapshot(bpy.types.Operator):
    """Restore f-curves to match a selected snapshot."""

    bl_idname = "ghost_tool.restore_snapshot"
    bl_label = "Restore Snapshot"
    bl_options = {'REGISTER', 'UNDO'}

    snapshot_uid: bpy.props.StringProperty(
        name="Snapshot UID",
        description="UID of the snapshot to restore",
    )  # type: ignore[assignment]

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Restore the specified snapshot.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'} or {'CANCELLED'}.
        """
        store = SnapshotStore.get(context.scene)
        success = store.restore_snapshot(self.snapshot_uid, context.scene)
        if success:
            self.report({'INFO'}, "Snapshot restored")
            tag_viewport_redraw(context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Failed to restore snapshot")
            return {'CANCELLED'}


class GHOST_OT_toggle_snapshot(bpy.types.Operator):
    """Toggle the visibility of a snapshot overlay."""

    bl_idname = "ghost_tool.toggle_snapshot"
    bl_label = "Toggle Snapshot Visibility"

    snapshot_uid: bpy.props.StringProperty(
        name="Snapshot UID",
        description="Internal identifier of the snapshot whose visibility will change",
    )  # type: ignore[assignment]

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Toggle snapshot visibility.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'}.
        """
        store = SnapshotStore.get(context.scene)
        new_state = store.toggle_visibility(self.snapshot_uid)
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_delete_snapshot(bpy.types.Operator):
    """Delete a snapshot permanently."""

    bl_idname = "ghost_tool.delete_snapshot"
    bl_label = "Delete Snapshot"
    bl_description = "Delete this snapshot permanently. This cannot be undone"

    def invoke(self, context, event):  # type: ignore[no-untyped-def]
        wm = context.window_manager
        try:
            return wm.invoke_confirm(self, event, message="Delete this snapshot? This cannot be undone.", confirm_text="Delete", icon="WARNING")
        except TypeError:  # pragma: no cover - Blender < 4.1
            return wm.invoke_confirm(self, event)

    snapshot_uid: bpy.props.StringProperty(
        name="Snapshot UID",
        description="Internal identifier of the snapshot to delete",
    )  # type: ignore[assignment]

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Delete the specified snapshot.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'} or {'CANCELLED'}.
        """
        store = SnapshotStore.get(context.scene)
        success = store.delete_snapshot(self.snapshot_uid)
        if success:
            self.report({'INFO'}, "Snapshot deleted")
            tag_viewport_redraw(context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Snapshot not found")
            return {'CANCELLED'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    GHOST_OT_take_snapshot,
    GHOST_OT_restore_snapshot,
    GHOST_OT_toggle_snapshot,
    GHOST_OT_delete_snapshot,
)


def register() -> None:
    """Register snapshot classes."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister snapshot classes and clean up stores."""
    SnapshotStore.clear_all_instances()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


# ---------------------------------------------------------------------------
# Test notes
# ---------------------------------------------------------------------------
#
# Test 1: Take and restore snapshot
# >>> store = SnapshotStore.get(bpy.context.scene)
# >>> snap = store.take_snapshot("Test", bpy.context.scene)
# >>> assert snap.name == "Test"
# >>> assert len(snap.ghost_data) >= 0
#
# Test 2: FIFO eviction
# >>> for i in range(12):
# ...     store.take_snapshot(f"Snap {i}", bpy.context.scene)
# >>> assert len(store.get_all()) <= MAX_SNAPSHOTS
#
# Test 3: Visibility toggle
# >>> uid = store.get_all()[0].uid
# >>> store.toggle_visibility(uid)
# >>> assert store.get_by_uid(uid).is_visible == False
