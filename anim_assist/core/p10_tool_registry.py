# --- ORCHESTRATION AND RECOVERY ---
"""Operator metadata registry for orchestration orchestration layer.

Provides a central catalog of every Anim Assist operator with metadata
(phase, category, display name, icon, tags) so the quick shelf, search,
favorites, recent tools, and pie menus can query tools without hard-coding
operator IDs throughout the UI.

Public API:
    register_tool(entry)       — add a ToolEntry to the registry
    get_tool(op_id)            — look up by operator bl_idname
    get_tools_by_phase(phase)  — all tools from a given phase
    get_tools_by_tag(tag)      — all tools matching a tag
    search_tools(query)        — case-insensitive substring search
    all_tools()                — full registry snapshot
    clear()                    — wipe for shutdown/reload
"""

from __future__ import annotations

from dataclasses import dataclass

from .logging import get_logger

__all__ = [
    "ToolEntry",
    "register_tool",
    "register_tools",
    "get_tool",
    "get_tools_by_phase",
    "get_tools_by_tag",
    "get_tools_by_category",
    "search_tools",
    "all_tools",
    "get_categories",
    "get_phases",
    "clear",
]

_log = get_logger(__name__)


@dataclass(frozen=True)
class ToolEntry:
    """Immutable metadata record for one Anim Assist operator."""

    op_id: str                              # e.g. "animassist.breakdown_current_frame"
    label: str                              # e.g. "Breakdown"
    phase: int                              # 1-10
    category: str                           # e.g. "Breakdown", "Mirror"
    icon: str = "NONE"                      # Blender icon name
    tags: tuple[str, ...] = ()              # free-form search tags
    description: str = ""                   # one-liner tooltip
    is_modal: bool = False                  # True if operator runs MODAL
    supports_batch: bool = True             # can be run in batch/macro


# ---------------------------------------------------------------------------
# Module-level registry
# ---------------------------------------------------------------------------

_registry: dict[str, ToolEntry] = {}


def register_tool(entry: ToolEntry) -> None:
    """Add or overwrite a tool entry."""
    if entry.op_id in _registry:
        _log.debug("Overwriting tool entry: %s", entry.op_id)
    _registry[entry.op_id] = entry


def register_tools(entries: list[ToolEntry] | tuple[ToolEntry, ...]) -> None:
    """Batch-register multiple tool entries."""
    for entry in entries:
        register_tool(entry)


def get_tool(op_id: str) -> ToolEntry | None:
    """Return the ToolEntry for the given operator ID, or None."""
    return _registry.get(op_id)


def get_tools_by_phase(phase: int) -> list[ToolEntry]:
    """Return all tools belonging to the given phase number."""
    return [t for t in _registry.values() if t.phase == phase]


def get_tools_by_tag(tag: str) -> list[ToolEntry]:
    """Return all tools that carry the given tag."""
    tag_lower = tag.lower()
    return [t for t in _registry.values() if tag_lower in (x.lower() for x in t.tags)]


def get_tools_by_category(category: str) -> list[ToolEntry]:
    """Return all tools in the given category."""
    cat_lower = category.lower()
    return [t for t in _registry.values() if t.category.lower() == cat_lower]


def search_tools(query: str) -> list[ToolEntry]:
    """Case-insensitive substring search across label, category, tags, description."""
    q = query.lower()
    results: list[ToolEntry] = []
    for t in _registry.values():
        if (
            q in t.label.lower()
            or q in t.category.lower()
            or q in t.description.lower()
            or q in t.op_id.lower()
            or any(q in tag.lower() for tag in t.tags)
        ):
            results.append(t)
    return results


def all_tools() -> list[ToolEntry]:
    """Return all registered tool entries sorted by (phase, category, label)."""
    return sorted(_registry.values(), key=lambda t: (t.phase, t.category, t.label))


def get_categories() -> list[str]:
    """Return a sorted list of unique categories."""
    return sorted({t.category for t in _registry.values()})


def get_phases() -> list[int]:
    """Return a sorted list of unique phase numbers."""
    return sorted({t.phase for t in _registry.values()})


def clear() -> None:
    """Wipe the registry (called during addon shutdown)."""
    _registry.clear()
