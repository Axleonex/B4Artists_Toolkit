# Ghost Tool 4.2.3 marker target fold

Date: 2026-10-12. Status: local candidate; not published.

## Findings and design plan

The user's screenshot shows the full Mixamo bone list above Show Markers, filling the popover.
`_draw_show_ghosts` wrapped every target name directly into the main section. The existing
Show Ghosts, Onion Skin and other top-level groups already have independent native fold IDs.
Three of six focused checks fail before the fix: closed targets still show all names,
there is no separate details body, and there is no compact selected-bone count.

Subject: animators inspecting marker targets without losing access to other Ghost Tool actions.
Treatment: native UI tool. Preserve the current Bforartists theme palette, fonts, row sizes,
and layout controls; add no custom color or typography tokens.
Layout: compact rig/count summary, existing Show/Clear Markers actions, a closed Marker Targets
fold containing full names, then the independent Options fold and sibling tool groups.
Tier: Show/Clear Markers remain day-to-day actions; the target fold is inspection detail.

Interaction contract: clicking Marker Targets changes only target-detail visibility. Closed
shows rig/count and keeps actions/options/other tools accessible; open wraps every full name.
Selection changes update the count and list. No selection keeps the existing recovery message.
Collapsing Show Ghosts changes only that group. Folding never changes animation or ghost data.
No onboarding is needed for a standard native disclosure arrow.

## Verification

The exact ZIP was extracted to an isolated installation. All 29 Python modules match the
working source byte for byte, and its internal version is `(4, 2, 3)`.

| Suite | Passed / run | Result |
|---|---:|---|
| Marker target UI | 6 / 6 | Pass: independent folds, selected count, all full names, object-only and missing targets |
| Header UI | 16 / 16 | Pass |
| Authoring | 20 / 20 | Pass; preserves the covered jitter protections |
| Afterimage UI | 8 / 9 | Native Tool Shelf registration assertion requires Bforartists |

Total: 50 of 51 focused checks pass on Blender 5.1.2, build `ec6e62d40fa9`, with only the
Bforartists registration gate patched. The single failure is `0 != 2` for the registered native
Tool Shelf classes. It reproduces identically against the exact published 4.2.2 ZIP;
the other eight supplemental UI checks pass in both builds. No source change masks that host limit.

The native Blender popover was rendered with 65 selected bones. Visual inspection confirms a
compact `Markers: Armature / 65 bones` summary, closed Marker Targets and Options folds, and
all sibling tool groups visible. A Bforartists screenshot and physical fold interaction on the
owner's host are not verified. The previous 230-check/five-native-move run belongs to 4.2.2;
it was not repeated or attributed to this UI-only candidate.

Inspected native preview: `C:/Users/AtonLotus/AppData/Local/Temp/ghost423-ui-preview.png`.
Focused package logs: `C:/Users/AtonLotus/AppData/Local/Temp/ghost423-test_ghost_*.py.log`.
Baseline log: `C:/Users/AtonLotus/AppData/Local/Temp/ghost422-ui-baseline.log`.

UI audit: R5 tools-apart, R8 actions-then-options, R10 show-dont-hide, R12 readable-at-width,
and R14 evolve pass the six focused checks. The new fold header has no icon (R7).
Existing top-level section header icons and operator placement remain the established add-on
convention; no unrelated panel restructuring. No operators or animation settings were changed.

Archive: `releases/b4_ghost_tool_v4.2.3.zip`, 214,475 bytes.
SHA256: `352864a728bab87675eb25e71aae5a8236a53bb13f5b4986906d1426d9396ce5`.

To check in Bforartists: install the candidate and restart. Select all bones of a large rig,
open Ghost Tool and expand Show Ghosts. Show Markers and the other tools should fit without
the name list. Open and close Marker Targets; the list alone should fold. Open Onion Skin,
collapse Show Ghosts, and confirm Onion Skin stays open. Repeat in the separate Ghost Tool
window and with only a few bones selected. Folding should not change existing ghosts or keys.

## Execution

Code Router recommended/actual: T3_PRIME_OMP. Policy fingerprint:
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
Windows preflight: RUNTIME_UNAVAILABLE because the OMP relay requires Unix sockets.
The static execution policy permits native continuation within the declared scope.
No independent model-review PASS is claimed. Merge/push/publication require owner confirmation.
