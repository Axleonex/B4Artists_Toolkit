# Native Timeline toolbar — Bforartists application patch

Date: 2026-10-12. Direction approved by the owner: a true native second row through a Bforartists application patch. This written specification awaits review before implementation, as required by the brainstorming workflow.

## Outcome

An enabled Anim Assist displays its configurable toolbar immediately above the native Timeline playback/keyframing header. Both rows belong to the same Timeline editor. Resizing changes that editor's key canvas, with no separate Text Editor, recurring joins/splits, or toolbar replacement during the drag.

```text
One native Timeline editor
┌──────────────────────────────────────────────────────────┐
│ Gear  Tween + quick buttons  Curves  Timing  Keys …       │
│ Native playback, frame, keying and Timeline controls      │
│ Frame ruler and editable keys                            │
└──────────────────────────────────────────────────────────┘
```

The seven family clusters, 70 existing presets, 13 defaults and saved quick selections carry over. The toolbar uses native buttons, menus, tooltips and horizontal header scrolling.

## Evidence and baseline

- Released Bforartists baseline: `v5.2.0`, commit `0a1ca45552dba1006ae0fb5c4dd36657622a4e66`, confirmed through the upstream GitHub API.
- Its Action/Timeline space creates a native header and footer, but no tool header. The footer poll excludes Timeline mode. Source: [space_action.cc](https://github.com/Bforartists/Bforartists/blob/v5.2.0/source/blender/editors/space_action/space_action.cc).
- Its Dope Sheet RNA region-toggle mask does not expose a tool header. Source: [rna_space.cc](https://github.com/Bforartists/Bforartists/blob/v5.2.0/source/blender/makesrna/intern/rna_space.cc).
- The 3D View already supplies the native tool-header creation, visibility and UI-handler pattern to follow. Source: [space_view3d.cc](https://github.com/Bforartists/Bforartists/blob/v5.2.0/source/blender/editors/space_view3d/space_view3d.cc).
- Native screen resizing currently treats a header height as the minimum area height. The patch must account for both visible Timeline headers and the key canvas. Source: [screen_geometry.cc](https://github.com/Bforartists/Bforartists/blob/v5.2.0/source/blender/editors/screen/screen_geometry.cc).
- Anim Assist 12.5.1 repairs strip height by joining and splitting its owned pair. That recurring editor replacement is the behavior being removed.
- Visual Studio 2022 Build Tools with the C++ component, bundled CMake and Ninja are installed on the current Windows host. A Bforartists source/build checkout and its libraries have not been prepared. No patched executable has been compiled or launched.

## Application changes

1. Add a native `RGN_TYPE_TOOL_HEADER` to the Action space. Its native poll permits Timeline mode only. Place it immediately above the Timeline playback header; preserve the user's top/bottom header convention when the header is flipped.
2. Register native header sizing, drawing, scrolling and input handlers, following the existing 3D View pattern. Add-on Python draws the tools; C++ owns the region and its geometry.
3. Expose `SpaceDopeSheetEditor.show_region_tool_header` through RNA. New regions start hidden until a toolbar provider enables them, so Bforartists without Anim Assist does not gain an empty bar.
4. Ensure old saved Action spaces receive a missing tool-header region when initialized. The migration adds a region inside the existing editor and preserves its type, view and animation state. It must not create another editor or require a new official Blender file-version number.
5. When Anim Assist first enables the native row, the application makes room once through native shared-edge sizing. The minimum height is the sum of visible header heights, borders and 48 UI-scaled pixels for the frame ruler/key canvas. Interactive resize and window-resize constraints use the same minimum while the row is enabled. Hiding it restores ordinary native sizing.
6. Limit this sizing behavior to Timeline editors using the native tool row. Respect neighboring editors' minimum sizes. If the whole window cannot satisfy those constraints, keep native controls visible and report the space limitation; do not oscillate visibility or silently reconstruct the layout.

Application files: `source/blender/editors/space_action/space_action.cc`, `source/blender/makesrna/intern/rna_space.cc`, `source/blender/editors/screen/screen_geometry.cc`, `source/blender/editors/screen/screen_ops.cc`, and declarations in `source/blender/editors/include/ED_screen.hh` as needed by the shared sizing helper.

The planned dedicated source checkout is `G:/LapArt/Projects/Blender_Addons/Bforartists_Native_Timeline`, based on the pinned upstream commit. Work stays on a `codex/` branch. Existing installations and unrelated projects are not modified.

## Anim Assist integration

1. Register a native `Header` for `DOPESHEET_EDITOR` / `TOOL_HEADER`, polling only for Timeline mode and an enabled native toolbar preference.
2. Reuse the existing family catalogue, quick-selection preferences and draw layout. Commands target the current Timeline's window region directly; they no longer search for a different editor below the toolbar.
3. Retain the stored `timeline_toolbar_row` preference for compatibility, with the visible label changed to Native Timeline Toolbar. Existing false values remain false. Fresh enabled add-ons show the row without manual resizing. Explicit user hiding remains respected.
4. On enable or file load, perform at most one migration of a directly paired, marked legacy Text Editor strip. Keep the Timeline as the surviving editor. Preserve keys, playhead, zoom and quick selections. Unrelated Text Editors and unpaired editors are not joined or overwritten.
5. Remove ongoing strip creation and size-repair logic. Any lifecycle callback may reconcile region visibility for a newly opened Timeline, but must not perform recurring geometry repairs or reverse an explicit user hide.
6. On an unpatched Bforartists build, use the existing native Timeline header for the configurable quick controls and explain the native-row requirement in preferences. Do not revive the separate-editor workaround. Disable/unregister removes add-on controls and hides its native row cleanly.

Primary add-on files: `anim_assist/ui/timeline_strip.py`, `anim_assist/ui/header_toolbars.py`, `anim_assist/ui/headers.py`, and `anim_assist/prefs.py`. Catalogue targets and animation math remain unchanged. Existing Redo and trail-position findings are outside this interface change.

## Build and release scope

- Build a portable Windows x64 Bforartists application using its upstream Windows build scripts and free dependencies. This is a custom application build; it must be identified as Bforartists 5.2.0 with the Anim Assist native Timeline patch, not represented as an official upstream release.
- Package the matching add-on as the next minor release, proposed **Anim Assist 12.6.0**, once implementation and packaging are complete. The public 12.5.1 source, ZIP and version numbers remain current during design/build preparation.
- Deliver a reproducible native source patch against the pinned commit, the portable application, the matching add-on ZIP, source revision information, hashes and launch/install instructions. An add-on ZIP alone cannot supply the native C++ region.
- Prepare and launch the custom application with an isolated profile. Do not overwrite or install over the owner's Bforartists. Any publication, new main integration or release upload receives its own concrete before/after review and the required owner confirmation.

## Acceptance and evidence

Completion requires a compiled native Bforartists executable and recorded evidence for the following behavior; a source diff, a mockup, or Blender stand-in screenshots cannot qualify the native application patch.

- Fresh default workspace: native tool row appears on Anim Assist enable; playhead, ruler and keys remain visible without dragging to reveal it.
- Repeated shrinking, expanding and window resizing at 100% and 150% scale: both header regions remain stable, the screen area count is unchanged, and no marked Text Editor strip is created. Capture before/during/after evidence, not just a settled screenshot.
- Default and saved quick selections, empty selection, reset, family menus and header panning remain usable. Commands operate on the current Timeline and retain their existing prerequisites.
- Old 12.5.1 layouts migrate once without losing keys/view state or affecting unrelated editors. Saving/reopening, workspace changes, multiple Timelines/windows, hide/show, disable and re-enable retain one native row per enabled Timeline.
- Native keying, playback and scrubbing remain usable. Other editor sizing, Ghost Tool and BoneCraft UI remain intact.
- The add-on on unpatched Bforartists uses the documented native-header fallback and never starts the legacy split/join timer.

No tests have been added or run during this design stage. The implementation plan must distinguish compilation, manual native acceptance, any separately authorized test runs, and unverified cases. Record build or usability failures as failures rather than publishing a success claim.

## Review checkpoint

The owner has approved the application-patch direction. Review this concrete design before the detailed implementation plan and application/add-on coding. Current implementation status: design only; no native patch or executable yet.
