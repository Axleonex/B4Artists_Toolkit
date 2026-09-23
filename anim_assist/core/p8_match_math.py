# --- MATCHING TRANSFORM MATH ---
"""Pure-ish transform matching and space-switch compensation math.

Provides the mathematical backbone for every matching and space switching matching and
compensation operator.  Functions that need ``bpy`` import it lazily
so unit tests can exercise the pure-math helpers without Blender.

Key concepts
------------

*Visual matrix*
    ``obj.matrix_world`` after depsgraph evaluation — the transform the
    user actually *sees* in the viewport.

*Local matrix*
    ``obj.matrix_local`` — the transform relative to the parent.  This
    is what we can *write* (via ``obj.location`` / ``rotation_euler`` /
    ``scale``) and have Blender propagate to world space.

*Match*
    Set an object's local transform so its visual (world) transform
    equals a target world matrix, optionally filtering by channel or
    axis.

*Compensate*
    Record the visual matrix, change an external property (space
    switch), force a depsgraph update, then compute the new local
    transform that recovers the original visual result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # Forward refs only.

__all__ = [
    "AxisMask",
    "MATCH_ALL",
    "MATCH_NONE",
    "ChannelFilter",
    "decompose_matrix",
    "compose_matrix",
    "visual_world_matrix",
    "parent_world_matrix",
    "compute_local_from_world",
    "is_channel_locked",
    "is_channel_driven",
    "MatchResult",
    "compute_match",
    "apply_match_result",
    "key_match_result",
    "record_visual_state",
    "compensate_after_switch",
    "mirror_name",
]


# ---------------------------------------------------------------------------
# Channel / axis mask helpers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AxisMask:
    """Per-axis toggle for loc, rot, scale."""

    x: bool = True
    y: bool = True
    z: bool = True

    def any(self) -> bool:
        """Return True if at least one axis is enabled."""
        return self.x or self.y or self.z

    def as_tuple(self) -> tuple[bool, bool, bool]:
        """Return axes as a tuple (x, y, z)."""
        return (self.x, self.y, self.z)


MATCH_ALL = AxisMask(True, True, True)
MATCH_NONE = AxisMask(False, False, False)


@dataclass(frozen=True)
class ChannelFilter:
    """Which transform channels to include in a match operation."""

    location: AxisMask = field(default_factory=lambda: MATCH_ALL)
    rotation: AxisMask = field(default_factory=lambda: MATCH_ALL)
    scale: AxisMask = field(default_factory=lambda: MATCH_ALL)

    # Convenience constructors -------------------------------------------------

    @classmethod
    def all(cls) -> ChannelFilter:
        """Match all channels (location, rotation, scale)."""
        return cls()

    @classmethod
    def loc_only(cls) -> ChannelFilter:
        """Match only location channels, skip rotation and scale."""
        return cls(rotation=MATCH_NONE, scale=MATCH_NONE)

    @classmethod
    def rot_only(cls) -> ChannelFilter:
        """Match only rotation channels, skip location and scale."""
        return cls(location=MATCH_NONE, scale=MATCH_NONE)

    @classmethod
    def scale_only(cls) -> ChannelFilter:
        """Match only scale channels, skip location and rotation."""
        return cls(location=MATCH_NONE, rotation=MATCH_NONE)

    @classmethod
    def loc_rot(cls) -> ChannelFilter:
        """Match location and rotation, skip scale.

        Most common for IK/FK switching on limbs (arms, legs) where scale
        is rarely keyed. Avoids overwriting unintended scale values.
        """
        return cls(scale=MATCH_NONE)


# ---------------------------------------------------------------------------
# Pure math — Matrix → TRS decomposition (uses mathutils via bpy)
# ---------------------------------------------------------------------------

def decompose_matrix(matrix):  # type: ignore[no-untyped-def]
    """Decompose a 4×4 matrix into (location, rotation_euler, scale).

    Returns mathutils types: ``(Vector, Euler, Vector)``.
    """
    loc = matrix.to_translation()
    rot = matrix.to_euler()
    sca = matrix.to_scale()
    return loc, rot, sca


def compose_matrix(loc, rot, sca):  # type: ignore[no-untyped-def]
    """Build a 4×4 matrix from loc/euler/scale components.

    *rot* may be an ``Euler`` or a ``Quaternion``.
    """
    from mathutils import Matrix, Vector

    mat_loc = Matrix.Translation(loc)
    if hasattr(rot, "to_matrix"):
        mat_rot = rot.to_matrix().to_4x4()
    else:
        mat_rot = Matrix.Identity(4)
    mat_sca = Matrix.Diagonal(Vector((*sca, 1.0)))
    return mat_loc @ mat_rot @ mat_sca


# ---------------------------------------------------------------------------
# Object-level queries (need bpy lazily)
# ---------------------------------------------------------------------------

def visual_world_matrix(obj):  # type: ignore[no-untyped-def]
    """Return the depsgraph-evaluated world matrix of *obj*.

    Falls back to ``obj.matrix_world`` if no depsgraph available.
    """
    import bpy
    try:
        dg = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(dg)
        return eval_obj.matrix_world.copy()
    except Exception:  # noqa: BLE001
        return obj.matrix_world.copy()


def parent_world_matrix(obj):  # type: ignore[no-untyped-def]
    """Return the parent's evaluated world matrix, or Identity if none."""
    from mathutils import Matrix

    if obj.parent is None:
        return Matrix.Identity(4)
    return visual_world_matrix(obj.parent)


def compute_local_from_world(desired_world, parent_world):  # type: ignore[no-untyped-def]
    """Compute the local matrix that, when combined with *parent_world*,
    yields *desired_world*.

    ``local = parent_world.inverted() @ desired_world``
    """
    return parent_world.inverted_safe() @ desired_world


# ---------------------------------------------------------------------------
# Channel lock / driver queries
# ---------------------------------------------------------------------------

_LOC_PATHS = ("location",)
_ROT_PATHS = ("rotation_euler", "rotation_quaternion", "rotation_axis_angle")
_SCA_PATHS = ("scale",)


def is_channel_locked(obj, channel: str, axis: int) -> bool:
    """Check whether *obj*'s transform channel is locked.

    *channel*: one of ``"location"``, ``"rotation_euler"``, ``"scale"``.
    *axis*: 0/1/2 for x/y/z.
    """
    if channel == "location":
        return obj.lock_location[axis]
    if channel in ("rotation_euler", "rotation_quaternion"):
        return obj.lock_rotation[axis]
    if channel == "scale":
        return obj.lock_scale[axis]
    return False


def is_channel_driven(obj, data_path: str, index: int = -1) -> bool:
    """Return True if a driver controls *data_path* (optionally at *index*)."""
    adata = getattr(obj, "animation_data", None)
    if adata is None:
        return False
    for drv in adata.drivers:
        if drv.data_path == data_path:
            if index < 0 or drv.array_index == index:
                return True
    return False


# ---------------------------------------------------------------------------
# High-level match: compute target local TRS to match a source world matrix
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    """Result of a match computation — what to write to the target."""

    location: tuple[float, float, float] | None = None
    rotation_euler: tuple[float, float, float] | None = None
    scale: tuple[float, float, float] | None = None
    channels_written: list[str] = field(default_factory=list)


def compute_match(
    source_world,
    target_obj,
    channel_filter: ChannelFilter | None = None,
    maintain_offset: bool = False,
    respect_locks: bool = True,
    respect_drivers: bool = True,
    use_visual: bool = True,
) -> MatchResult:
    """Compute the local TRS that makes *target_obj* visually match *source_world*.

    Parameters
    ----------
    source_world : Matrix
        The desired world-space matrix to match.
    target_obj : bpy.types.Object
        The object whose transform will be set.
    channel_filter : ChannelFilter, optional
        Which channels/axes to include.  Defaults to all.
    maintain_offset : bool
        If True, preserve the existing offset between source and target.
    respect_locks : bool
        Skip locked channels.
    respect_drivers : bool
        Skip driven channels.
    use_visual : bool
        Use evaluated world matrices for parent hierarchy.

    Returns
    -------
    MatchResult
        The computed channel values and list of what was written.
    """

    if channel_filter is None:
        channel_filter = ChannelFilter.all()

    result = MatchResult()

    # Compute the parent's world matrix.
    if use_visual:
        p_world = parent_world_matrix(target_obj)
    else:
        if target_obj.parent:
            p_world = target_obj.matrix_parent_inverse @ target_obj.parent.matrix_world.copy()
        else:
            from mathutils import Matrix
            p_world = target_obj.matrix_parent_inverse @ Matrix.Identity(4)

    # Account for parent_inverse matrix (Blender's keep-transform offset).
    # In Blender: world = parent_world @ parent_inverse @ local
    # So: local = (parent_world @ parent_inverse)^-1 @ desired_world
    effective_parent = p_world @ target_obj.matrix_parent_inverse
    desired_local = effective_parent.inverted_safe() @ source_world

    if maintain_offset:
        # Compute current offset in world space and re-apply after match.
        if use_visual:
            current_world = visual_world_matrix(target_obj)
        else:
            current_world = target_obj.matrix_world.copy()
        offset = source_world.inverted_safe() @ current_world
        desired_local = effective_parent.inverted_safe() @ (source_world @ offset)

    d_loc, d_rot, d_sca = decompose_matrix(desired_local)

    # --- Location ---
    _apply_channel_match(
        result, d_loc, target_obj, channel_filter.location,
        "location", respect_locks, respect_drivers
    )

    # --- Rotation ---
    _apply_channel_match(
        result, d_rot, target_obj, channel_filter.rotation,
        "rotation_euler", respect_locks, respect_drivers
    )

    # --- Scale ---
    _apply_channel_match(
        result, d_sca, target_obj, channel_filter.scale,
        "scale", respect_locks, respect_drivers
    )

    return result


def _apply_channel_match(
    result: MatchResult,
    desired_values,  # type: ignore[no-untyped-def]
    target_obj,  # type: ignore[no-untyped-def]
    axis_mask: AxisMask,
    channel_name: str,
    respect_locks: bool,
    respect_drivers: bool,
) -> None:
    """Helper: apply a single channel match (loc/rot/scale)."""
    if not axis_mask.any():
        return

    if channel_name == "location":
        cur_val = target_obj.location.copy()
    elif channel_name == "rotation_euler":
        cur_val = target_obj.rotation_euler.copy()
    else:  # scale
        cur_val = target_obj.scale.copy()

    new_val = list(cur_val)
    for i, (flag, axis_name) in enumerate(
        zip(axis_mask.as_tuple(), ("x", "y", "z"), strict=False)
    ):
        if not flag:
            continue
        if respect_locks and is_channel_locked(target_obj, channel_name, i):
            continue
        if respect_drivers and is_channel_driven(target_obj, channel_name, i):
            continue
        new_val[i] = desired_values[i]
        result.channels_written.append(f"{channel_name}.{axis_name}")

    # Store result
    if channel_name == "location":
        result.location = tuple(new_val)
    elif channel_name == "rotation_euler":
        result.rotation_euler = tuple(new_val)
    else:  # scale
        result.scale = tuple(new_val)


def apply_match_result(target_obj, match: MatchResult) -> None:  # type: ignore[no-untyped-def]
    """Write a MatchResult to the target object's transform channels."""
    from mathutils import Vector, Euler

    if match.location is not None:
        target_obj.location = Vector(match.location)
    if match.rotation_euler is not None:
        target_obj.rotation_euler = Euler(match.rotation_euler)
    if match.scale is not None:
        target_obj.scale = Vector(match.scale)


def key_match_result(
    target_obj, match: MatchResult, frame: int
) -> int:  # type: ignore[no-untyped-def]
    """Insert keyframes for all channels in *match*.  Returns key count."""
    if target_obj.animation_data is None:
        target_obj.animation_data_create()

    keyed = 0
    if match.location is not None and any(
        c.startswith("location") for c in match.channels_written
    ):
        target_obj.keyframe_insert(data_path="location", frame=frame)
        keyed += 1
    if match.rotation_euler is not None and any(
        c.startswith("rotation") for c in match.channels_written
    ):
        target_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        keyed += 1
    if match.scale is not None and any(
        c.startswith("scale") for c in match.channels_written
    ):
        target_obj.keyframe_insert(data_path="scale", frame=frame)
        keyed += 1
    return keyed


# ---------------------------------------------------------------------------
# Space-switch compensation helpers
# ---------------------------------------------------------------------------

def record_visual_state(obj) -> dict:  # type: ignore[no-untyped-def, type-arg]
    """Snapshot visual world matrix plus TRS for later restoration."""
    mat = visual_world_matrix(obj)
    loc, rot, sca = decompose_matrix(mat)
    return {
        "matrix_world": mat,
        "location": tuple(loc),
        "rotation_euler": tuple(rot),
        "scale": tuple(sca),
    }


def compensate_after_switch(
    obj,
    recorded_state: dict,  # type: ignore[type-arg]
    channel_filter: ChannelFilter | None = None,
    respect_locks: bool = True,
    respect_drivers: bool = True,
) -> MatchResult:
    """After a property change + depsgraph update, compute the local TRS
    that recovers the object's previously recorded visual transform.

    Call ``record_visual_state()`` *before* the property change, change
    the property, call ``context.view_layer.update()``, then call this.
    """
    return compute_match(
        source_world=recorded_state["matrix_world"],
        target_obj=obj,
        channel_filter=channel_filter,
        maintain_offset=False,
        respect_locks=respect_locks,
        respect_drivers=respect_drivers,
        use_visual=True,
    )


# ---------------------------------------------------------------------------
# Mirror naming (re-implements for matching and space switching independence)
# ---------------------------------------------------------------------------

import re as _re

_MIRROR_PATTERNS: tuple[tuple[_re.Pattern[str], str], ...] = (
    (_re.compile(r"\.L(\b|$)"), ".R"),
    (_re.compile(r"\.R(\b|$)"), ".L"),
    (_re.compile(r"_L(\b|$)"), "_R"),
    (_re.compile(r"_R(\b|$)"), "_L"),
    (_re.compile(r"(?<![a-zA-Z])Left(?![a-zA-Z])"), "Right"),
    (_re.compile(r"(?<![a-zA-Z])Right(?![a-zA-Z])"), "Left"),
    (_re.compile(r"(?<![a-zA-Z])left(?![a-zA-Z])"), "right"),
    (_re.compile(r"(?<![a-zA-Z])right(?![a-zA-Z])"), "left"),
)


def mirror_name(name: str) -> str:
    """Return the opposite-side name, or the original if no pattern matches."""
    for pat, repl in _MIRROR_PATTERNS:
        result = pat.sub(repl, name)
        if result != name:
            return result
    return name
