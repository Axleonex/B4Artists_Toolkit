# Source Research — 2026-10-12

Research was direct, scoped source reading on clean work branch `codex/anim-assist-12.4.0`, baseline `56a69c1`. No product test was run for this planning request.

| Existing source | Observed fact | Planning consequence |
| --- | --- | --- |
| `anim_assist/ui/timeline_catalog.py` | ACTIONS has 70 presets; GROUPS defines seven families; FAMILY maps presets to their real menu home. QUICK_GROUPS preserves 17 original shortcuts, including Push/Pull under a legacy Curves heading. | Use GROUPS/FAMILY for new cluster ownership, not QUICK_GROUPS. Preserve operator suffixes and argument dictionaries. |
| `anim_assist/ui/timeline_catalog.py::toolbar_plan` | Thresholds are compact below 900, Tween from 360, Timing from 1120, Keys from 1260 logical pixels. | The owned strip's new drawing must stop using these hiding thresholds. |
| `anim_assist/ui/timeline_strip.py::_draw_toolbar` | Draws all menus first, then width-dependent Tween/Timing/Keys groups, More and a gear. Reads scene `header_show_*` switches. | Replace only drawing/configuration routing; preserve strip ownership and pairing. |
| `anim_assist/ui/timeline_strip.py::_button` | One wrapper handles descriptions, availability and dispatch action IDs. | All pinned actions use this path; no duplicated direct bpy.ops buttons. |
| `anim_assist/ui/timeline_strip.py::ANIMASSIST_OT_timeline_tool` | Invokes operators against the paired Timeline and enables target Undo explicitly. | Preserve dispatch mode, arguments and single Undo ownership. |
| `anim_assist/prefs.py` | Add-on preferences use package-aware `get_prefs`; no per-action quick configuration exists. | Add stable per-action booleans and lazy preparation before preferences registration. |
| `anim_assist/__init__.py::_build_registry` | Preferences are registered through a class registry after package/UI imports finish. | This is the safe point to prepare dynamic preference annotations. |
| `anim_assist/ui/__init__.py` | Imports headers and header_toolbars as part of UI loading. | Avoid importing the UI catalog from the top level of prefs.py. |
| `anim_assist/ui/header_toolbars.py` | Existing gear labels Timeline placement as preference and category visibility as scene/shared-editor state. | Keep the legacy settings panel for other editors; give Timeline quick selection its own view. |
| `anim_assist/operators/settings_ops.py` | Export has a fixed field list; import applies compatible known preferences. Both private preference lookups use constants.ADDON_PACKAGE only. | Add quick fields to export and share get_prefs for renamed ZIP/extension packages. Preserve legacy imports with missing quick fields. |
| `tests/test_anim_assist_layout.py` | Existing native script checks menu targets, panel homes, descriptions and unregister cleanup. | Use its registration/cleanup conventions for future toolbar fixtures. |
| `docs/anim_assist/releases/12.4.0/package.py` | Packages the exact 12.3.1 inventory and enforces a fixed changed-file set and More inventory. | A new 12.5.0 builder must baseline 12.4.0 and update explicit change/quick checks. Do not rewrite the old builder or receipts. |
| `docs/anim_assist/releases/12.4.0/verification.py` | Exact-package GUI staging and effect oracles exist. | Copy/adapt in a new release directory; keep historical results immutable. |
| `.gitignore` | `.planning/` is intentionally local/ignored. | Commit the public plan snapshot; keep local GSD state and routing receipt out of Git. |

## Evidence boundary

Previously recorded 12.4.0 evidence is Blender 5.1.2 stand-in evidence. It is not proof of actual Bforartists behavior. Native panning of a long owned header, configuration persistence and this new design have not been exercised. The generated mockups are design illustrations, not runtime screenshots.

The shared GSD runtime doctor reported healthy resolution and no hard blocks. The documentation scope was classified by the Code Router; the local receipt records the actual lane and current runtime limits. Classification is not governed execution or independent plan review. No new council or subagents were dispatched.
