# Phase 02 verification

Status: **Local technical qualification; owner usability pending**.
Release 12.6.2, SHA256
`5492e94a773a0398e281d0b3a0410de0b75c9e92fd5f4b4980373e39474643f7`.
Native host: stock Bforartists 5.2.0 / runtime 5.3 Alpha / build 0a1ca45552db.

| Requirement | Status | Evidence / scope |
| --- | --- | --- |
| ST-01 existing default/immediate effects | Pass after repairs | Original exact 12.6.1 exposed mirror/trail/redo defects; repaired baseline and final 80 effects/native routes pass |
| ST-02 nine original interactive tools | Pass in fixtures | 18 preview/commit/cancel cases, including real Anim Offset, and native recovery |
| ST-03 display modes | Pass | Eight numeric four-mode schemas; ordinary two-mode; all Inline/Popout routes exercised |
| ST-04 Recommended defaults | Pass | Two inline sliders, presets, Timing nudges/Scale popout, Copy/Paste/Mirror/Bake/Trails; actual screenshot |
| ST-05 order/migration | Pass | Seven family order, within-family ordering, pure tests and native explicit custom/empty legacy migration |
| ST-06 immediate drag/recovery | Pass | 32 actual row cases, independently calculated values, exact cancellation snapshots, 56 full recovery assertions |
| ST-07 individual settings | Pass in fixtures | Actual staged dialogs accept/cancel, precision/snapping/preset effects; scene-options link uses existing scope |
| ST-08 extended/neutral values | Pass for measured cells | Native Smooth −100/200, seven neutral values; positive Scale/Breakdown limits validated. Arbitrary very large ranges unverified |
| ST-09 named layouts | Pass | Native save/load/rename/delete/reset/transfer; pure update/name/protection checks |
| ST-10 safety/persistence | Pass | Layout changes preserve animation; normal restart restores exact active record/library and automatic enable |
| ST-11 size/architecture | Pass for measured cells | Actual 1.5/2 scale, 477/1117px splits, manual 85px height retained; no add-on-created helper editor/repair loop |
| ST-12 native input/lifecycle | Partial | Scrub/pan/zoom/play, two windows, disable/re-enable, active cleanup, workspace loss, scene reload pass. Renamed extension install and keyboard-only use unverified |
| ST-13 final regression | Pass in fixtures | All 89 actions accounted for; eight × two slider modes; undo/redo and evaluated world-space trails |
| ST-14 artifact/owner checkpoint | Technical pass; owner pending | Byte-compared installation, receipt/version/hash, screenshots, gate audit and UAT checklist |

## Evidence index

- baseline/repaired-baseline/undo-diagnostic: original defects and measured repairs.
- adapters/row/layouts: intermediate implementation evidence.
- final: earlier regression before timer-finalization repair; current strict
  artifact receipt and 23 pure tests. Its old package-identity hash is superseded.
- qualified-full/ui/layouts: delivered exact ZIP regression, default row/dialog
  cancellation, library transfer and normal restart.
- stress-complete: reached measured scale/header/navigation/multiwindow/precision/
  snapping/manual-height and active-disable cells on the delivered hash. Its
  false aggregate is retained: native area_move was unavailable during BLOCKING
  modal. A completed tail tests real workspace loss instead of relabelling this
  diagnostic as a full pass.
- stress-tail: completed active-disable, workspace loss and scene reload.
- edges-final: preset/reset, seven neutral scalar settings, locked/hidden scope
  and actual narrow split.
- Earlier stress folders preserve fixture errors and the real timer-cleanup
  failure; they are not counted as successful suite runs.

All evidence is under evidence/. Task-owned profiles assert CONFIG and module
paths and compare installed bytes with the ZIP. Source hashes are in the artifact
receipt. Synthetic fixtures in a real host do not establish production-rig
quality. The author also wrote the tests; [gate audit](GATE-AUDIT.md) explains
falsifiers, real failures and the independent-review limitation.

## Checkpoint and limits

See [release qualification](../../releases/12.6.2/qualification.md) for exact
results, screenshots and unsupported cells. This is a supported POST_PIXEL
canvas band with native keymaps, not a true second native HEADER. A completely
collapsed canvas needs expansion. The first space attempt runs once; later
manual resizing is respected. Top-header placement leaves the frame ruler above
the band. Some icon-only entries use generic glyphs.

Native border movement during a BLOCKING drag, renamed extension installations,
alternate platforms/themes, mixed-monitor DPI and keyboard-only accessibility
remain unverified. Still images cannot settle flashing in the owner's workspace.
No continuous recording was made. Algorithms are existing Anim Assist tools,
not full AnimBot parity. Compilation, FINISHED status, screenshot existence and
totals alone are not treated as functional proof.

Local technical endpoint reached. Follow [02-UAT.md](02-UAT.md) for owner
usability. No push, merge or publication occurred; exact Confirm merge update
approval is a separate checkpoint.
