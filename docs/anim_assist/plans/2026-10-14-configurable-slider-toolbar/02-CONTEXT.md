# Phase 02 context

## Locked user decisions

- Keep the add-on second row; A is the primary design. Visible favorite sliders
  and direct-drag temporary sliders are configurable per tool.
- Order: Tween, Timing, Curves, Keys, Pose, Bake, Motion; utilities at right.
- Two recommended inline sliders: Breakdown and Smooth; avoid overwhelming
  first use. Others can be selected by the artist, not permanently excluded.
- Native settings windows determine visibility, display mode and tool options.
- Save layouts under user-entered names and keep them across sessions.
- Verify existing bar tools before changing their access, and regress afterward.
- No separate application or resize-repair loop; mockup annotations are not UI.

## Implementation choices derived from those decisions

Use a versioned JSON preference record with stable action IDs. Do not use names
as IDs, scatter a new RNA property for every slider field, or serialize live
modal objects. Native dialogs stage edits until accepted. Keep scene settings
separate from layout presentation. Eight one-dimensional adapters use the same
transaction API; Anim Offset stays a session button. Existing Button invocation
can keep its current click-to-confirm semantics; slider modes use hold/release.
Plan review is inline; no subagent work is requested for this packet.

## Reusable assets

timeline_catalog.py (89 action mappings), timeline_strip.py (guarded dispatcher,
Search/More/family options), timeline_overlay.py (pixel band/keymaps), prefs.py
(package-aware preference accessor), operators/settings_ops.py (JSON transfer),
existing snapshot/core math and the isolated native verification scripts.

## Approval and assumptions

User's 'That sounds good', 'Sounds good' and request for a GSD plan establish
the design basis. UI choices can be reviewed before implementation; do not
re-ask already settled second-row/default decisions. Scope is stock Bforartists
and a local add-on artifact. No version bump during planning. Planned release
number is resolved against latest repository versions when packaging.
