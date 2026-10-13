# Native Timeline Toolbar Implementation Plan

> For the executing agent: follow subagent-driven-development with separate native/application and add-on ownership; spec review precedes quality review. The owner's approved design authorizes implementation. Developer instructions take precedence over skill examples: do not add or run formal tests without a separate user request.

**Goal:** deliver a portable, patched Bforartists application and Anim Assist 12.6.0 using a genuine second native Timeline row with direct configurable tools, search and accurate functional coverage.

**Architecture:** add `RGN_TYPE_TOOL_HEADER` to Bforartists' Action space and expose its native visibility/sizing operation. Anim Assist draws into that region in the current Timeline, preserves its catalogue/preferences, extends existing-tool access and migrates old marked editor strips once. Native geometry handles resizing; Python never repairs height by repeatedly joining/splitting editors.

**Tech Stack:** Bforartists v5.2.0 / C++ / RNA / Python bpy; Visual Studio 2022 Build Tools, CMake and Ninja; Windows x64 portable output.

## Approved contracts

Read together: [native design](../superpowers/specs/2026-10-12-native-timeline-toolbar-design.md) and [tool access](../superpowers/specs/2026-10-12-native-timeline-toolbar-access.md), approved by the owner on 2026-10-13.

UI treatment: native operated tool. Inherit Bforartists theme colors, fonts, header height, button styling and DPI scaling; introduce no custom palette or animation. Gear and Search precede the seven familiar inline family clusters. Unavailable actions stay visible with a prerequisite. Success means a tool acts in the current Timeline, and continuous adjustment can be committed or cancelled while preserving keys. Explicit hide remains respected; show restores the same row. Existing preferences and animation data survive transitions.

## Task 1 — Prepare pinned source and dependencies

- Source directory: `G:/LapArt/Projects/Blender_Addons/Bforartists_Native_Timeline`.
- Clone upstream `v5.2.0`, verify commit `0a1ca45552dba1006ae0fb5c4dd36657622a4e66`, finish checkout before further mutation, then use branch `codex/native-timeline-toolbar`.
- Read source-local instructions and upstream Windows scripts. Use pinned Windows library submodule commit `60d6e96b917568278d400a4024c98da0fb777338`; record actual dependency revisions. Do not update the application branch to upstream main.
- Locate VS2022 C++ environment, bundled CMake/Ninja, Git and Python. Keep source, build and portable output distinct. Log dependency/configuration/build outcomes.

## Task 2 — Implement native header region

Files under the native source checkout: `source/blender/editors/space_action/space_action.cc`, `source/blender/makesrna/intern/rna_space.cc`.

- Add a Timeline-only native tool-header region before the playback header. Follow View3D's header callbacks and DPI-aware sizing; do not enable an empty row when Anim Assist is absent.
- Extend the Dope Sheet region-toggle mask with `(1 << RGN_TYPE_TOOL_HEADER)`, exposing `show_region_tool_header`.
- On Action-space initialization, supply a missing native region for old saved layouts. Preserve other regions and state. No official file-version bump.
- Define a stable application interface for the add-on: `bpy.ops.screen.timeline_toolbar_set(enabled=True)`. Its poll requires a Timeline/window, never the actual mouse to be on an editor boundary. Native invocation toggles the row and makes sufficient room once.
- Commit scoped native changes locally, then perform separate spec and quality reviews before treating the packet complete.

## Task 3 — Native sizing and lifecycle

Native files: `source/blender/editors/screen/screen_geometry.cc`, `screen_ops.cc`, declarations in `source/blender/editors/include/ED_screen.hh`, and native Action/RNA files as needed for the visibility hook.

- Introduce a shared per-area minimum-height helper: ordinary editors retain the old minimum; a Timeline with a visible native tool header reserves all visible native header heights plus 48 scaled pixels and native borders for ruler/keys.
- Apply the same helper to initial enable, edge-drag limits, window resizing and loaded short layouts. Move only native shared-edge vertices within adjacent area/window constraints. Never split/join for sizing.
- Explicitly hidden toolbar returns to normal sizing. Reject impossible geometry safely; preserve the row and existing areas, with a clear limitation rather than visibility oscillation.
- Identify the custom application patch/build in its delivered instructions and revision metadata. Do not call it an official Bforartists upstream release.

## Task 4 — Integrate native Anim Assist controls

Toolkit files: `anim_assist/ui/timeline_strip.py`, `header_toolbars.py`, `headers.py`, `timeline_catalog.py`, `anim_assist/prefs.py`.

Core header definition:

```python
class ANIMASSIST_HT_timeline_tools(bpy.types.Header):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'TOOL_HEADER'

    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TIMELINE'
```

Complete registration/drawing must additionally account for native capability and saved preference, using the actual existing draw implementation. Dispatch invokes mapped target operators with the current Timeline's WINDOW region; preserve target operator undo/modal behavior.

- Capability is the native RNA toggle plus callable `screen.timeline_toolbar_set`; do not infer support from the executable's name.
- Keep `timeline_toolbar_row` as the persisted Boolean; label it Native Timeline Toolbar. Fresh defaults show the row; saved false values remain false. Lifecycle callbacks reconcile only new/opened Timeline state, never continuously repair geometry or reverse native user hiding.
- Perform one-time owned, adjacent legacy-strip joins on enable/load. Preserve Timeline, selection, playhead and view. Do not alter unrelated Text Editors.
- Remove repeating legacy strip creation/resizing and Text Header replacement. Unpatched Bforartists gets configurable controls in its existing native Timeline header, with a native-row requirement explanation in preferences.
- Add visible search beside Gear. Search executes or pins validated presets; each catalogue entry is directly pinnable. Family menus, existing 70 preset IDs, 13 defaults and existing quick preference values remain.
- Add existing selected-key clipboard and accurately named reference-bookmark controls. Assess configured rig-space/matching commands for safe catalogue inclusion. Expose only valid target properties and context; never invent an absent backend or advertise helper objects as functional editable pivots.
- Native options are available without forcing an unnecessary dialog before primary actions. Existing modal tools retain feedback, commit/cancel and supported ranges. Produce a coverage matrix with operator IDs, parameters, gestures, scope, access and partial/unverified status.
- Commit scoped toolkit changes locally, then spec review followed by quality review.

## Task 5 — Compile portable application

- Finish pinned library acquisition and upstream CMake configuration using the verified VS2022 environment. Upstream `make.bat ninja release` is the initial build route; inspect `parse_arguments.cmd` and actual cache rather than assuming the output directory.
- Compile/install with bounded parallelism appropriate to the host; no broad test target. Fix actual diagnostics through narrowly scoped repair packets. Preserve logs and distinguish successful compilation from runtime usability.
- Package the installed application into a portable directory/ZIP, including required runtime resources, Python and licensing/source-patch material.

## Task 6 — Native acceptance observations

Use an isolated existing CONFIG/SCRIPTS/DATAFILES tree. Assert the resolved CONFIG before launching. No owner-preference writes or in-place application install.

- Launch the actual patched Bforartists, enable the exact matching add-on and capture the native two rows in a fresh default Timeline.
- Observe shrink/expand and window resize at 100%/150%, including during the drag. Confirm the same area count and no owned Text Editor is created.
- Observe direct tool actions, search, pin/reset/empty selection, family menus, header panning, disabled prerequisites and continuous commit/cancel.
- Observe old marked-strip migration, save/reopen, workspace changes, multiple Timelines/windows and hide/show/disable/re-enable. Observe native playback/scrubbing/keying and unchanged adjacent editor behavior.
- These are the design's manual acceptance observations. Do not substitute a formal test suite or claim unobserved cases pass. Separate known inherited operator findings from new interface defects.

## Task 7 — Exact packaging and review checkpoint

Toolkit files: version tuple/string, manifest, `CHANGELOG.md`, release builder/receipt/notes/qualification/coverage under `docs/anim_assist/releases/12.6.0/`; native patch/build record under `native_patches/bforartists/5.2.0/`.

- Record exact baseline, native patch revision, application build options/dependency revisions and SHA256 hashes.
- Build add-on 12.6.0 and verify package/source/version consistency while keeping historical archives unchanged.
- Deliver both portable application and matching add-on ZIP, with instructions that clearly distinguish custom application and add-on installation.
- Complete final integration review. Local commits are allowed. Keep public version/download metadata at 12.5.1 until a concrete publication diff has received a fresh Confirm merge update for this new release.

## Progress ledger

1. Pinned source checkout/dependencies — started.
2. Native region — pending.
3. Native sizing — pending.
4. Add-on integration/access — pending.
5. Compilation/portable output — pending.
6. Native acceptance — pending.
7. Packaging/review — pending.

Endpoint: actual compiled native application plus matching exact add-on artifact and observed usability evidence. Source-only implementation is incomplete.
