# Ghost Tool 4.2.5 Compare target folds

Date: 2026-10-12. Status: local candidate; not published.

## Findings and interaction plan

Compare wraps the entire capture target list before Save Snapshot, and every saved snapshot's
targets before its actions. Long rigs make both lists fill the panel. Native `UILayout.panel`
requires full-width layout and cannot be placed inside the existing snapshot boxes.

Subject: animators keeping Compare actions accessible while inspecting large target lists.
Treatment: native UI tool, retaining Bforartists theme palette, fonts and row spacing.
Layout: scope, compact capture summary, Save Snapshot, then a closed Capture Targets fold.
Saved references keep their summary and actions in their cards; each has a full-width
Snapshot Targets fold immediately after its card, identified by the stable snapshot UID.
No new styling tokens or action locations outside Compare. Existing Show Markers folds remain.

Interaction contract: opening/closing one target fold changes only that list. Counts, snapshot
actions and binding warnings stay visible. Full names wrap when expanded. Missing targets keep
recovery messages visible; folding never captures, restores, edits selection or assigns IDs.
No onboarding beyond the native disclosure arrow. Version 4.2.5 is explicitly requested.

## Verification

Before the fix, five of six focused checks fail (four assertions and the missing compact-label
API); only the empty-capture recovery case passes. After the fix, all six pass.

The exact 4.2.5 ZIP was extracted to an isolated install. All 29 Python modules match working
source byte for byte. Its internal version is `(4, 2, 5)`; 4.2.4 was skipped as requested.

| Suite | Passed / run |
|---|---:|
| Compare target UI | 6 / 6 |
| Marker target UI | 6 / 6 |
| Header UI | 16 / 16 |
| Authoring | 20 / 20 |
| Snapshot targets and identity | 16 / 16 |
| Afterimage UI | 8 / 9 |

Total: 72 of 73 checks pass on Blender 5.1.2, build `ec6e62d40fa9`, with only the Bforartists
registration gate patched. The single failure is the same native Tool Shelf registration
assertion (`0 != 2`) documented for 4.2.3 and reproduced against 4.2.2. Bforartists native UI
and production-rig acceptance remain pending. The older broad/native-move results remain
attributed to their original builds; they were not repeated for this UI change.

The focused checks cover closed/open capture details, unique target counts without writes,
independent snapshot folds with stable UIDs through rename/reorder, no target recovery, binding
warnings and action visibility. The recording layout rejects folds inside snapshot boxes.
Real rendering with a 65-bone rig and a bound snapshot confirms the native popover fits the
summary, Save Snapshot, Hide, Restore, Save Variant, Delete and both closed folds without
the full name lists. No draw error appears in the native preview log.

Preview: `C:/Users/AtonLotus/AppData/Local/Temp/ghost425-compare-preview.png`.
Package receipt: `C:/Users/AtonLotus/AppData/Local/Temp/ghost425-package-receipt.json`.
Logs: `C:/Users/AtonLotus/AppData/Local/Temp/ghost425-test_ghost_*.py.log`.

UI audit: R5 tools-apart, R8 actions-then-options, R10 show-dont-hide and R14 evolve pass the
focused checks. Expanded full names wrap at 220 px (R12); new fold headers have no icons (R7).
Existing section header icons and operator homes remain the add-on convention. No operators,
snapshot binding authority, animation settings or stored reference contents were changed.

Archive: `releases/b4_ghost_tool_v4.2.5.zip`, 214,774 bytes.
SHA256: `24035c68700bdca208ed0a07ee8e86cb4b5d22b545a7198952364243da3fe339`.

Owner check: install 4.2.5 and restart Bforartists. Select many pose bones, show markers, then
open Compare. Capture Targets should start closed; Save Snapshot stays visible. Save two
references and open one Snapshot Targets fold: the other should remain closed. Close/open
Compare and the other tool groups independently. Recheck empty selection and imported/unbound
references: warnings and Bind to Active Target must stay visible. No keys should change by folding.

## Execution

Code Router recommended/actual: T3_PRIME_OMP. Policy fingerprint:
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
Windows preflight reports RUNTIME_UNAVAILABLE: the OMP relay requires Unix sockets.
The static policy permits native continuation within the declared scope.
No independent model-review PASS is claimed. Merge/push/publication require owner confirmation.
