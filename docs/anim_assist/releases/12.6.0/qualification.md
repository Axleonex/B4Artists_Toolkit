# Native Timeline qualification — 12.6.0

Status: the available-host validation matrix passed after the repairs below.
The local Windows application and matching add-on are built and unpublished.
Windows display-DPI transitions and continuous window-border render coverage
remain outside the qualified evidence.

## Build identity

- Custom Bforartists Windows x64 application, source baseline `v5.2.0`
  (`0a1ca45552dba1006ae0fb5c4dd36657622a4e66`), native patch commit
  `f5f550195e2299239f020f8e5b3cc5c391dadb43`.
- Release/Ninja build completed with MSVC 19.44.35228.0 and two build jobs.
  The four-job attempt exhausted compiler heap/PDB resources; the failed
  targets compiled after resuming at two jobs. An interrupted exit-zero run
  without an application was excluded.
- Executable SHA256:
  `f6647c50792f1be94ff1473c83cdd19c33702ea6181c2188a0d54175a898587b`.
  The application UI identifies as Bforartists 5.2.0; `bpy.app.version`
  reports `[5, 3, 0]` in this build.
- Matching Anim Assist add-on `12.6.0`: 577,101 bytes,
  SHA256 `60d4c7f10d9f14adde17e0cd5269bb07d4a4fc8f96810a4cd6e67903e5e73193`.
- The portable archive omits the three optional PDB debug-symbol files.
  GPU rendering/device coverage is not established by this Timeline build.

## Initial manual observations

| Case | Observation |
|---|---|
| Fresh Timeline | The native Anim Assist TOOL_HEADER and native playback HEADER appeared together on the same Timeline without reveal dragging. The ruler and keys remained visible. |
| Direct action | Nudge Right moved the selected keyframes from frames 1/20/40 to 2/21/41. Selection, Bezier interpolation and both handle offsets were preserved. |
| Search and pin | Search found Copy Selected Keys with Handles; Pin added a direct COPY button, and invoking it reported nine copied keys. |
| Options and anchor help | Tween options opened with mode, masks and inbetween count. The 50% tooltip explained that a key on the playhead is the previous anchor; an empty frame uses surrounding keys. |
| Settled resize at 100% | Screenshots before, after expansion and at minimum height show both header rows remaining visible with key data. |
| UI scale at 150% | The add-on row, native playback row, ruler and keys remained visible. Scale returned to 100% before exit. |
| Modal Escape | Smooth showed live adjustment feedback. Escape restored the evaluated pose. Before/after snapshots show identical key coordinates, selection, Bezier interpolation and handles. |

Screenshots 01–16 and the exact stage summary are in `native-evidence/`;
`native-observations.json` stores the underlying application snapshots.
Qualification used the compiled binary and the exact 12.6.0 ZIP in a
task-owned profile. Preference autosave was disabled. The scene was discarded
on exit.

## Completed validation — 2026-10-13

The owner requested complete validation. Native GUI integration assertions and
actual Windows input ran in a disposable CONFIG/SCRIPTS/DATAFILES profile.
The corrected ZIP's 203 files match the installed bytes after restart. The
native executable hash is unchanged. Source spec review passed before quality
review; quality review approved the repaired product files.

| Case | Result |
|---|---|
| Fresh enable and process restart | Both native rows appear without reveal dragging. Empty pins and a custom 14-button selection persist through separate full restarts. |
| Catalogue | All 89 presets resolve registered targets and valid arguments; all presets can be pinned into their family. Reset restores the 13 defaults. |
| Immediate actions | All 80 actions passed an explicit state/effect assertion in the patched host and genuine unpatched Bforartists baseline `0a1ca45552db`. |
| Modal actions | All nine actions passed live curve-geometry changes, commit retaining the adjusted snapshot, Escape restoring the original snapshot, and native handler cleanup: nine commit/cancel pairs, comprising 18 required cases. |
| Copy, paste, reference | Nine keys copied with handles; paste uses the configured absolute-time offset; bookmark recall changes the reference without moving the playhead. |
| Pose, bake, motion | Object matching, numeric rig switching, two-bone pose operations, configured bake ranges, reduction, proxies and trajectory-cache changes passed on their independent fixtures. |
| Action Offset | Handle translation, full cancellation, inserted-key removal, custom easing, fast mode and masks passed. Moving the playhead rebases the cancellation snapshot; Escape restores that latest baseline. |
| Search and quick controls | Actual Search typing, filtered execution, Pin/Unpin and the visible Reset button passed. Empty selection keeps family menus and Search available. |
| Editor border resize | Expand and shrink at 100% and 150% have valid native framebuffer samples during the measured gestures. Both rows and the key region remain nonblank in those samples. Capture limits were not reached. |
| Window resize | Actual width changes at 100%/150% and a height change at 150% retained both rows and a visible key region. Render samples cover before/after, not the interval inside the Windows size loop. |
| Panning and small windows | Native header panning reaches clipped families. The 150% task window was reduced to 650 × 610 client pixels with both rows and keys visible. |
| Lifecycle | Workspace switches, three Timelines across two windows, ordinary/maximized disable/re-enable, explicit hiding and explicit preference reveal passed. The lifecycle callback may take up to one second. |
| Saved layouts | Loading with `load_ui=True` restored two windows/three Timelines and explicit saved hiding. A disabled Load UI preference correctly retains the current layout. |
| Legacy migration | A marked adjacent Text Editor was joined once; the Timeline and animation survived. Unmarked, nonadjacent and later-marked editors were preserved. |
| Native animation controls | Actual native playback, pause, mouse scrubbing and Location-key insertion passed. One-step Undo and native Edit-menu Redo restored exact key/handle snapshots. |
| Unpatched host | Feature detection selected the existing native header. All 80 immediate fixture effects passed with no helper editor created; actual header panning exposed the fallback families. |

The evidence audit retains the original failed reproductions and fixture/input
errors, with dispositions and successful retests. It reports no unresolved
failed assertion in this matrix. The apparent redo failure was an input-tool
defect: a native event probe recorded Ctrl+Z without Shift; native menu Redo
passed with unchanged product code. Initial saved-hide failures used Load UI
disabled; explicit saved-layout loading passed.

Evidence: [audit summary](native-evidence/full-validation/summary.json),
`assertions.json`, `immediate-actions.json`, `modal-actions.json`, measured
gesture/render records, and request/response reproductions in the same folder.
The three validation scripts are under `tests/`.

## Repairs found by validation

- Re-enable now uses the owning window's screen implicitly, avoiding the rejected
  explicit screen override while a Timeline is maximized.
- Ease availability and help explain its two-key prerequisite.
- Action Offset reads the installed package's preferences, translates Bezier
  handles with values, and restores geometry, key types, selection and easing
  parameters on cancellation.

## Limits

Discrete in-drag editor samples do not prove that every possible flicker is
absent. Window-border captures contain no in-gesture native render samples.
Windows display-DPI changes were not run; authorization to temporarily change
the global display setting was requested. Bforartists UI scale is a separate
setting and was tested at 100% and 150%.

These independent fixtures qualify tool access and representative effects,
not every algorithm edge case, production rig, GPU device or render engine.
The existing motion-trail accuracy findings remain separate from trajectory
cache/display access. Full AnimBot algorithm/gesture parity and owner acceptance
of the new interface are not claimed.
