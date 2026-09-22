"""Timeline marker sync and active-range management for B4Artists ML.

Implements plan §5 items 1-3: key-pose ↔ timeline marker reconciliation,
active-range set/restore (contract §STATE MAP ANCHORS_CAPTURED / PREVIEW_ACTIVE;
spike items 5 and 7).

Verified source facts:
  copy.py:144   MARKER_PREFIX = 'B4ML Pose '  (ASCII; spike item 5 requires ASCII names)
  workflow.py:640  retime_anchor(obj, scene, source_frame, expected_destination=None)
                   destination = scene.frame_current + scene.frame_subframe
  workflow.py:566  _prepare_pose_retime requires interpolation_method == 'POSES'
  obj.b4ml.anchors   CollectionProperty; each item: .frame (float), .name (str)
  obj.b4ml.candidate_action  PointerProperty(Action) (stage.py:9)
  ui.py:402    anchor_page: IntProperty — no active_anchor_index property exists;
               pull() skips marker-selected → active-index step (noted in open questions)
  spike item 7  timers do not fire in --background; register() guards this
  spike item 5  timeline_markers.new() sets marker.select=True by default → set False
"""
from __future__ import annotations

try:
    import bpy
    from bpy.app.handlers import persistent
except ImportError:
    bpy = None  # type: ignore[assignment]
    def persistent(fn):  # type: ignore[misc]
        """No-op fallback when bpy is unavailable (e.g. plain Python tests)."""
        return fn

from . import copy

# ---------------------------------------------------------------------------
# Module-level state (no bpy types retained across ticks)
# ---------------------------------------------------------------------------

_preview_state: dict[str, tuple[bool, int, int]] = {}
# rig.name → (use_preview_range, frame_preview_start, frame_preview_end) before activation

_last_state: dict[str, tuple] = {}
# rig.name → frozen tuple of (marker name, frame, select) + anchor frames

_last_candidate: dict[str, bool] = {}
# rig.name → had candidate_action last tick

# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

def _rig_ascii(name: str) -> str:
    """Encode rig name slice to ASCII, replacing non-ASCII with '?'."""
    return name.encode('ascii', 'replace').decode('ascii')


def _rigs_with_anchors() -> int:
    """Count armature objects that have at least one anchor (bpy must be live)."""
    if bpy is None:
        return 0
    return sum(
        1 for o in bpy.data.objects
        if o.type == 'ARMATURE' and len(o.b4ml.anchors) > 0
    )


def marker_name(rig, index: int) -> str:
    """Marker name for anchor at *index* (0-based) on *rig*.

    Single rig: 'B4ML Pose {n}'.
    Two or more rigs with anchors: 'B4ML Pose {n} {rig.name[:8]}' (ASCII).
    Plan §8 two-rig case.
    """
    prefix = copy.MARKER_PREFIX
    if _rigs_with_anchors() >= 2:
        return f"{prefix}{index + 1} {_rig_ascii(rig.name[:8])}"
    return f"{prefix}{index + 1}"


def is_ours(marker) -> bool:
    """True if *marker* was created by this module."""
    return marker.name.startswith(copy.MARKER_PREFIX)


def _parse_marker_index(name: str):
    """Parse a marker name into (1-based index, rig_suffix_or_None), or None."""
    if not name.startswith(copy.MARKER_PREFIX):
        return None
    rest = name[len(copy.MARKER_PREFIX):]
    parts = rest.split(' ', 1)
    try:
        idx = int(parts[0])
    except ValueError:
        return None
    return idx, (parts[1] if len(parts) > 1 else None)


def owned(scene, rig) -> list:
    """Our timeline markers that belong to *rig* in *scene*.

    Single-rig mode: markers with no rig suffix.
    Multi-rig mode: markers whose suffix matches rig.name[:8] (ASCII).
    """
    multi = _rigs_with_anchors() >= 2
    rig_prefix = _rig_ascii(rig.name[:8])
    result = []
    for m in scene.timeline_markers:
        parsed = _parse_marker_index(m.name)
        if parsed is None:
            continue
        _idx, suffix = parsed
        if multi:
            if suffix == rig_prefix:
                result.append(m)
        else:
            if suffix is None:
                result.append(m)
    return result


# ---------------------------------------------------------------------------
# Marker sync
# ---------------------------------------------------------------------------

def sync(scene, rig) -> dict:
    """Reconcile scene.timeline_markers with *rig*'s key poses.

    Creates missing markers, moves mismatched frames, removes stale ones.
    Newly created markers get select=False (spike item 5: new() selects by default).
    Never touches markers that are not ours. Idempotent.
    Returns {'created': n, 'moved': n, 'removed': n}.
    """
    anchors_sorted = sorted(rig.b4ml.anchors, key=lambda a: float(a.frame))
    expected: dict[str, int] = {
        marker_name(rig, i): int(round(float(anchor.frame)))
        for i, anchor in enumerate(anchors_sorted)
    }
    existing: dict[str, object] = {m.name: m for m in owned(scene, rig)}

    created = moved = removed = 0

    for name, frame in expected.items():
        if name in existing:
            m = existing[name]
            if m.frame != frame:
                m.frame = frame
                moved += 1
        else:
            m = scene.timeline_markers.new(name, frame=frame)
            m.select = False  # spike item 5: new() selects by default
            created += 1

    for name, m in existing.items():
        if name not in expected:
            scene.timeline_markers.remove(m)
            removed += 1

    return {'created': created, 'moved': moved, 'removed': removed}


# ---------------------------------------------------------------------------
# Marker → anchor pull
# ---------------------------------------------------------------------------

def anchors_from_markers(scene, rig) -> list[tuple[int, float]]:
    """Return [(anchor_index, marker_frame)] for owned markers mapped to an anchor."""
    count = len(rig.b4ml.anchors)
    result: list[tuple[int, float]] = []
    for m in owned(scene, rig):
        parsed = _parse_marker_index(m.name)
        if parsed is None:
            continue
        idx_1based, _suffix = parsed
        anchor_idx = idx_1based - 1
        if 0 <= anchor_idx < count:
            result.append((anchor_idx, float(m.frame)))
    return result


def pull(scene, rig) -> None:
    """Retime anchors whose timeline marker was moved by the user.

    Calls workflow.retime_anchor(obj, scene, source_frame) (workflow.py:640).
    That function reads scene.frame_current + scene.frame_subframe as the
    destination; we set and restore the scene frame around each call.
    Requires interpolation_method == 'POSES' (workflow.py:566); silently skips
    if not in that mode or if a posing/candidate session blocks retiming.
    Never touches rig.animation_data.action or fcurves.

    Open question: no active_anchor_index property found in ui.py (only
    anchor_page: IntProperty at ui.py:402); selected-marker → active-index
    step is skipped pending that property being added.
    """
    from b4artists_ml import workflow  # lazy: avoid circular import at module load

    anchors_sorted = sorted(rig.b4ml.anchors, key=lambda a: float(a.frame))
    ours_by_name: dict[str, object] = {m.name: m for m in owned(scene, rig)}

    moves: list[tuple[float, int]] = []
    for i, anchor in enumerate(anchors_sorted):
        name = marker_name(rig, i)
        m = ours_by_name.get(name)
        if m is None:
            continue
        anchor_frame = float(anchor.frame)
        marker_frame = int(m.frame)
        if abs(marker_frame - anchor_frame) > 0.5:
            moves.append((anchor_frame, marker_frame))

    if not moves:
        return

    old_frame = int(scene.frame_current)
    old_sub = float(getattr(scene, 'frame_subframe', 0.0))
    try:
        for anchor_frame, marker_frame in moves:
            try:
                scene.frame_current = marker_frame
                scene.frame_subframe = 0.0
                workflow.retime_anchor(rig, scene, anchor_frame)
            except Exception:
                pass  # POSES mode required; active session; order violation; etc.
    finally:
        scene.frame_current = old_frame
        if hasattr(scene, 'frame_subframe'):
            scene.frame_subframe = old_sub


# ---------------------------------------------------------------------------
# Preview range management
# ---------------------------------------------------------------------------

def preview_range(scene, rig, activate: bool) -> None:
    """Set or restore the scene preview range around *rig*'s key-pose span.

    activate=True (candidate present): stores previous (use_preview_range,
    frame_preview_start, frame_preview_end) and sets the range to the span.
    activate=False (keep or discard): restores the stored values.
    """
    key = rig.name
    if activate:
        if key not in _preview_state:
            _preview_state[key] = (
                bool(scene.use_preview_range),
                int(scene.frame_preview_start),
                int(scene.frame_preview_end),
            )
        anchors_sorted = sorted(rig.b4ml.anchors, key=lambda a: float(a.frame))
        if len(anchors_sorted) >= 2:
            start = int(round(float(anchors_sorted[0].frame)))
            end = int(round(float(anchors_sorted[-1].frame)))
            scene.use_preview_range = True
            scene.frame_preview_start = start
            scene.frame_preview_end = end
    else:
        if key in _preview_state:
            use_pr, start, end = _preview_state.pop(key)
            scene.use_preview_range = use_pr
            scene.frame_preview_start = start
            scene.frame_preview_end = end


def preview_range_active(rig) -> bool:
    """True if the preview range is currently managed by this module for *rig*."""
    return rig.name in _preview_state


# ---------------------------------------------------------------------------
# 0.25 s reconciliation timer
# ---------------------------------------------------------------------------

def tick() -> float:
    """Reconciliation body called every 0.25 s by bpy.app.timers (spike item 7).

    For each armature rig with anchors: syncs markers, pulls user-moved markers
    back to anchors, and transitions the preview range when candidate_action
    appears or disappears.
    Compares a frozen tuple of (marker name, frame, select) + anchor frames per
    rig; does nothing when unchanged.
    Exception-safe; never raises.
    Does not fire in --background (spike item 7); register() guards this.
    """
    try:
        if bpy is None:
            return 0.25
        scene = getattr(bpy.context, 'scene', None)
        if scene is None:
            return 0.25
        for obj in list(bpy.data.objects):
            if obj.type != 'ARMATURE':
                continue
            try:
                anchors = obj.b4ml.anchors
            except Exception:
                continue
            if len(anchors) == 0:
                continue
            rig = obj
            try:
                has_candidate = bool(rig.b4ml.candidate_action)
                state_key: tuple = (
                    tuple((m.name, m.frame, m.select) for m in owned(scene, rig))
                    + tuple(float(a.frame) for a in anchors)
                )
                had_candidate = _last_candidate.get(rig.name, False)
                unchanged = (
                    rig.name in _last_state
                    and _last_state[rig.name] == state_key
                    and had_candidate == has_candidate
                )
                _last_state[rig.name] = state_key
                _last_candidate[rig.name] = has_candidate

                if not unchanged:
                    sync(scene, rig)
                    pull(scene, rig)

                if has_candidate and not had_candidate:
                    preview_range(scene, rig, True)
                elif not has_candidate and had_candidate:
                    preview_range(scene, rig, False)
            except Exception:
                pass
    except Exception:
        pass
    return 0.25


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

@persistent
def _on_state_change(*args) -> None:
    """Sync markers for all rigs after undo, redo, or file load.

    Resets the last-state cache so the next tick performs a full reconcile.
    """
    try:
        if bpy is None:
            return
        scene = getattr(bpy.context, 'scene', None)
        if scene is None:
            return
        for obj in list(bpy.data.objects):
            if obj.type != 'ARMATURE':
                continue
            try:
                if len(obj.b4ml.anchors) > 0:
                    sync(scene, obj)
            except Exception:
                pass
        _last_state.clear()
        _last_candidate.clear()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Register / unregister (idempotent)
# ---------------------------------------------------------------------------

_HANDLER_LISTS: tuple[str, ...] = ('load_post', 'undo_post', 'redo_post')


def register() -> None:
    """Add undo/redo/load handlers; start the 0.25 s timer unless --background."""
    if bpy is None:
        return
    for name in _HANDLER_LISTS:
        lst = getattr(bpy.app.handlers, name)
        if _on_state_change not in lst:
            lst.append(_on_state_change)
    if not bpy.app.background and not bpy.app.timers.is_registered(tick):
        bpy.app.timers.register(tick, first_interval=0.25, persistent=True)


def unregister() -> None:
    """Remove handlers and stop the timer; clear module state."""
    if bpy is None:
        return
    for name in _HANDLER_LISTS:
        lst = getattr(bpy.app.handlers, name)
        if _on_state_change in lst:
            lst.remove(_on_state_change)
    if bpy.app.timers.is_registered(tick):
        bpy.app.timers.unregister(tick)
    _preview_state.clear()
    _last_state.clear()
    _last_candidate.clear()
