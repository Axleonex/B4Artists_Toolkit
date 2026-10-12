# Ghost Tool 4.2.5 display location

Date: 2026-10-12. Status: implemented and committed locally; push/publication requires owner confirmation.
Design: [approved design](design.md). Execution: [implementation plan](plan.md).

## Behavior

Edit > Preferences > Add-ons > Ghost Tool now has **Display Location** before Help:

| Choice | Home |
|---|---|
| Top Header | Existing viewport dropdown; default |
| Right Sidebar (N) | Ghost Tool tab in the right sidebar |
| Left Tool Shelf (T) | Ghost Tool tab in the Bforartists left shelf |

Switching immediately reveals the chosen side region, enables native shelf tabs when needed,
selects Ghost Tool after layout, and redraws ordinary viewports. Existing native panels remain
available. Save preferences normally to persist the choice. Side regions are not forcibly
closed when switching back to the header. Shared controls, target folds, separate-window access
and settings-editor access are present in all three homes. Dedicated Ghost Tool/settings windows
are excluded from ordinary homes to avoid duplicate controls.

Missing preferences default to the header. On an unsupported host, a saved left-shelf choice
resolves to the header and preferences explain the fallback; the stored choice is retained.
The Bforartists installation gate is unchanged. Delayed category selection cancels stale choices,
has a bounded retry, and is removed on unregister. This feature does not change frame sampling,
animation keys, scene settings or snapshot bindings.

## Evidence

The new behavioral suite initially failed all ten checks against the old source. After
implementation, its eleven checks pass, including an additional full-layout/fold regression.

The exact candidate ZIP was extracted into a separate installation; all 29 Python modules
match source bytes and its internal version is `(4, 2, 5)`.

| Suite | Passed / run |
|---|---:|
| Display location | 11 / 11 |
| Compare target UI | 6 / 6 |
| Marker target UI | 6 / 6 |
| Afterimage UI | 9 / 9 |
| Header UI | 16 / 16 |
| Authoring | 20 / 20 |
| Snapshot targets and identity | 16 / 16 |
| Total | 84 / 84 |

Host: Blender 5.1.2, build `ec6e62d40fa9`, with only the Bforartists registration gate overridden
in the test runner. Tests cover enum labels/default/save behavior, missing/invalid preferences,
exclusive home polls, unsupported-left fallback, region reveal/redraw, category selection,
stale callback cancellation, shared controls/folds and clean registration lifecycle. Supported
left-shelf polls/reveal use stand-ins; actual TOOLS registration and rendering require Bforartists.
The afterimage registration assertion now checks exact host-dependent identities: three native
shelf classes on supported hosts, zero on stock Blender. This replaces the former unconditional
two-class assertion; it is not evidence of native left-shelf acceptance.

Separate persistence checks save SIDEBAR to an isolated temporary `userpref.blend`, then load
it through `wm.read_userpref` in a fresh engine process: both pass, including correct home polls.
The user's normal preference files were untouched. Native screenshots with a 65-bone rig and
bound snapshot show the header and right sidebar rendering the same Compare controls and closed
target folds. The sidebar tab is selected automatically and the viewport header entry disappears.
Both preview error logs are empty.

Local evidence: `C:/Users/AtonLotus/AppData/Local/Temp/ghost425-location-header.png`,
`ghost425-location-sidebar.png`, `ghost425-prefs-save.log`, `ghost425-prefs-load.log`,
`ghost425-package-receipt.json`, and `ghost425-test_ghost_*.py.log` in that same directory.

## Package and remaining host check

Archive: `releases/b4_ghost_tool_v4.2.5.zip`, 216,217 bytes.
SHA256: `2fc2ab0dc1c97acfe36c76e77298ea6226123666097602666241ddb8713dad85`.
The historical 4.2.2 and 4.2.3 ZIP hashes remain unchanged. This updates the unpublished 4.2.5
candidate; no GitHub release was created or changed.

Native Bforartists is unavailable at the known `X:/5.2.0/bforartists.exe` path. Remaining
acceptance: install the candidate in Bforartists, switch through all three homes in Object and
Pose modes, check the left shelf at narrow/wide widths, expand each target fold independently,
and restart with the saved choice. Existing native Object/Pose action panels should remain
available. Verify a move with auto-key as a production-rig regression check.

UI audit: native palette/fonts/spacing, one persistent enum, shared drawer, distinct section
fold prefixes, and no extra shortcuts/dialogs. No independent model-review PASS is claimed.
Code Router recommended/actual T3_PRIME_OMP, policy fingerprint
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
Windows preflight reports RUNTIME_UNAVAILABLE because its OMP worker requires Unix sockets;
the static policy permits native continuation within the approved scope.
