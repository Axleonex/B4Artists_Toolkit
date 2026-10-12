# Ghost Tool display location implementation plan

**Goal:** Offer a persistent choice of Top Header, Right Sidebar (N), or Left Tool Shelf (T) in the unpublished 4.2.5 build.

**Architecture:** Register full-home panels once and use preference polls for exclusive visibility. Reuse the existing full drawer and footer; reveal the selected native region without changing scene data. Fall back to the header when native left-shelf support is absent.

**Tech stack:** Python, Blender/Bforartists RNA, unittest, native viewport panels, ZIP packaging.

Execution uses native Codex tools under the repository routing policy. The approved design requires no further design confirmation. Push and merge retain the owner's separate confirmation gate.

## Task 1: Define behavior in focused tests

Create `tests/test_ghost_display_location.py`. Verify enum default/choices, missing preferences, exclusive polls, dedicated-window isolation, unsupported-left fallback, region reveal/redraw, shared controls/folds, and clean lifecycle. Update the former no-sidebar invariant in `tests/test_ghost_header_ui.py` to the approved optional sidebar. Update the supported-host shelf identity assertion in `tests/test_ghost_afterimage_ui.py` for the additional full-home panel.

Run the new suite before implementation; expect missing API failures. Tests run in factory-startup Blender with only the Bforartists installation gate overridden. Real left-shelf usability remains a separate Bforartists acceptance check.

## Task 2: Add preference and location access

Modify `ghost_tool/preferences.py`: add `display_location` EnumProperty with identifiers HEADER, SIDEBAR, TOOLS; default HEADER; labels from the design. Add it before Help. A lazy UI update callback reveals and redraws viewports. Explain unavailable native left-shelf support in preferences. Avoid a module-level circular import.

Modify `ghost_tool/ui_panel.py`: safely read the add-on preference, resolve unsupported TOOLS to HEADER, and exclude dedicated/editor windows from ordinary homes. Keep the viewport header available only for HEADER. Add right UI and conditional left TOOLS panels, both using `draw_ghost_tool` with distinct prefixes and the shared footer. Register the left home alongside native quick-action panels only when SpaceView3D supports `show_toolshelf_tabs`.

Reveal sidebar/shelf and enable Bforartists shelf tabs for TOOLS. Select the category after redraw through a bounded timer; cancel stale selections when the choice changes and remove pending callbacks on unregister. Do not alter unrelated panel state.

## Task 3: Verify integration and persistence

Run `[PowerShell] & 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --factory-startup --python-exit-code 1 --python-expr <gate override and runpy test runner>` for the location, marker, Compare, header, authoring, snapshot-target and afterimage suites.

Enable the add-on in an isolated temporary user-config directory, save SIDEBAR preferences, restart and confirm SIDEBAR is loaded. Never save the user's actual preferences. Render header/right-sidebar previews with the native engine; inspect the shared controls and closed target folds. Record host limits explicitly.

## Task 4: Package and document

Rebuild only `releases/b4_ghost_tool_v4.2.5.zip` from the exact 29 source modules. Verify byte equality and version, then rerun the focused suites from its extracted installation. Update `README.md`, `docs/ghost_tool/README.md`, `releases/VERSIONS.md`, and `docs/ghost_tool/compare-targets/verification.md`; add `docs/ghost_tool/display-location/verification.md`. Preserve historical release bytes.

Commit the plan and implementation locally on `codex/ghost-tool-authoring-pause`. Show a before/after table and request the owner's exact merge confirmation before pushing.
