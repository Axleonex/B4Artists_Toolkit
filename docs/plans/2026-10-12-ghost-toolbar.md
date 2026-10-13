# Ghost Toolbar Implementation Plan

Historical implementation plan. The toolbar was merged as commit `9ee8840` and initially packaged as 4.2.6. The current release is **4.2.8**, with the toolbar visible by default and migration from the retired Top Header setting. See [4.2.8 release notes](../ghost_tool/releases/4.2.8/RELEASE-NOTES.md). Original implementation constraints below describe the approved scope at that time.

> **For the executing agent:** Use the subagent-driven-development skill to implement this plan task-by-task. The owner approved implementation on 2026-10-12; no repeated design approval is needed.

**Goal:** Add the approved persistent Ghost action strip to the native viewport Tool Settings row, with shared feature options and reliable hide/show recovery.

**Architecture:** Append to `VIEW3D_HT_tool_header`, preserving its native draw implementation. Share existing feature drawers between location panels and toolbar popovers. Persist display location and Ghost-only visibility in add-on preferences; reveal native regions only through explicit preference/operator actions. Use conservative layout bands with per-area hysteresis because Blender's append API does not expose the preceding native controls' occupied width.

**Tech Stack:** Python, Blender/Bforartists bpy UI, native Panel/Menu/Header, unittest and disposable Blender 5.1.2 stand-in processes.

## Constraints and endpoint

Approved spec: `docs/ghost_tool/toolbar/design.md`. Keep version 4.2.5, source backend sampling/authoring logic, saved location, legacy window-launch removal, and independent target folds. Do not overwrite the released 4.2.5 ZIP; package only a local candidate under ignored `build/`. Stop after implementation, evidence, documentation and a local work-branch commit; pushing/merging needs a before→after table and `Confirm merge update?`.

## Task 1: Native location and recovery

Modify `ghost_tool/preferences.py` and `ghost_tool/ui_panel.py`; extend `tests/test_ghost_display_location.py`.

1. Add `('TOOLBAR', 'Top Toolbar', 'Keep Ghost actions in the viewport Tool Settings row')` without changing HEADER default or existing identifiers.
2. Add saved `show_toolbar = BoolProperty(default=True)` with an update callback. When true in TOOLBAR, explicitly reveal `show_region_tool_header` across ordinary viewports; when false, redraw only.
3. Add `ghost_tool.set_toolbar_visibility` with hidden/skip-save Boolean action value; poll on available add-on preferences. Show sets TOOLBAR plus visible and reveals native row even if already true. Hide changes only the Ghost preference.
4. Keep header recovery available for HEADER and TOOLBAR; exclude dedicated legacy windows/editor contexts. Leaving TOOLBAR does not close native regions. Limit delayed category selection to SIDEBAR/TOOLS.
5. Test saved default, all choices, multi-viewport recovery, hidden native row respected by draw, switch cancellation, and registration teardown. Run the existing display-location suite before/after.

## Task 2: Shared feature destinations and toolbar

Modify `ghost_tool/ui_panel.py`, `ghost_tool/ghost_data.py`, `ghost_tool/modal_operator.py`, `ghost_tool/mesh_ghosts.py`; create `tests/test_ghost_toolbar_ui.py`.

1. Extract action helpers for Show Markers / Show Onion Skin. Keep existing shared drawers; add an `options_only` mode for these two drawers so arrows do not duplicate generation actions. Cached visibility checkbox comes first in feature popovers.
2. Add eight named feature popover Panels reusing GHOST_SECTIONS drawers. Reuse the existing Motion Paths popover. Options remain reachable regardless of target validity; native operator poll handles the individual action.
3. Add full Ghost command popover in fixed order, and More with identical relative order. Keep Compare Save/Restore inside Compare.
4. Append `_draw_viewport_tool_header`; wide includes all groups, compact first four plus More, narrow Ghost menu only. Inherit native theme and labels. Use UI-scale-normalized conservative Object/Pose bands and narrow fallback for modes with extensive native controls; record native evidence for constants. Hysteresis adds an arrow-width reserve before expansion, no timer.
5. Update generation and cached-visibility tooltips truthfully. Do not modify execution, sampling or dirty state.
6. Test destinations at every tier, disabled generation with reachable options, drawers/folds, no draw-time frame evaluation or scheduling, hide/show cache preservation, and append/remove reload. Run focused existing UI suites for regression.

## Task 3: Native verification and review

Create `tests/test_ghost_toolbar_native.py` and a local verification runner/evidence under `docs/ghost_tool/toolbar/`.

1. Use disposable config/scripts and only patch the Bforartists registration gate in stock Blender. Check native row in Object/Pose, wide/narrow, UI scale, main-header recovery, menu/popover rendering and multi-viewports. Capture real engine images. Report Bforartists-only validation separately.
2. Run `tests/test_ghost_native_authoring.py` with toolbar selected and visible to verify auto-key transforms remain unsampled during gestures and refresh after settle. Run authoring and snapshot suites unchanged.
3. Inspect changed bpy APIs and actual native behavior; resolve failures using systematic debugging. Perform spec review, then quality review, and final integration review.

## Task 4: Documentation, candidate and local commit

Modify `README.md`, `docs/ghost_tool/README.md`, `docs/ghost_tool/GhostTool_User_Manual.md`; add `docs/ghost_tool/toolbar/verification.md`.

1. Document four locations, persistent toolbar, generation vs cached visibility, full menu recovery, native Tool Settings alignment, and overflow behavior.
2. Build an ignored candidate ZIP from exactly the source modules; compare extracted bytes and validate registration/toolbar from that install. Do not relabel or replace the existing released archive.
3. Record native screenshots, test counts, known host limitations, routing receipts and B4Artists/Fable rule audit. Save concise public evidence without ephemeral server files or harness paths.
4. Review `rtk proxy git diff --check` and scope. Commit source/tests/docs on `codex/ghost-tool-authoring-pause`, excluding `.superpowers/` and raw local council/server data. Recap commit and ask `Confirm merge update?` only for the concrete push/merge result.

## Verification commands

All commands below use PowerShell, from the existing worktree. Use a dedicated runner to invoke each suite in an isolated factory-startup host and capture nonempty unittest results:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --factory-startup --python-exit-code 1 --python-expr "import sys,runpy;sys.path.insert(0,'.');import ghost_tool;ghost_tool._is_bforartists=lambda:True;runpy.run_path('tests/test_ghost_display_location.py',run_name='__main__')"
rtk proxy git diff --check
```

Expected: no UI registration exceptions, all relevant assertion cases pass, append list clean on unregister/reload, no native authoring regression. A browser mockup alone is not evidence of native behavior.

## Completion evidence

Implemented and independently reviewed on 2026-10-12. The source needed display-only cached flags for markers and skins, including hidden-marker picking guards; existing skin generation toggles were destructive and could not meet the approved behavior. No sampling scheduler changes were made.

All 178 checks/cases passed in the installed Blender stand-in. Real engine images, candidate/source integrity, preserved release checksum, host limits and the rule audit are recorded in [verification](../ghost_tool/toolbar/verification.md). Bforartists native validation remains unavailable and is explicitly NOT VERIFIED. Raw council/server files stay local; the public design and evidence are curated separately. Version remains 4.2.5. Push/merge awaits owner confirmation after the local work-branch commit.
