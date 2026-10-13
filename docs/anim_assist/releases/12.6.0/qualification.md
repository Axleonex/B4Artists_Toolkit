# Native Timeline qualification — 12.6.0

Status: the local Windows application and matching add-on are built. Manual
native UI qualification is partial. Only the cases listed as observed below
are qualified.

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
- Matching Anim Assist add-on `12.6.0`: 576,442 bytes,
  SHA256 `221afae332a3b2217d3e33c6075bac24c22def82cdd7bbf909a2e14f5de72a1b`.
- The portable archive omits the three optional PDB debug-symbol files.
  GPU rendering/device coverage is not established by this Timeline build.

## Observed in the native application

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

## Limits

Continuous no-flicker behavior during border dragging is not qualified. The
screenshots were returned after the drag ended; the native modal-operator
observer yielded zero samples on its first pass and one ambiguous sample on
the second. A geometry-delta observer was saved but not exercised. The
before/after screenshots establish settled behavior only, not absence of
flashing while dragging.

These cases remain unobserved: border/window resize at 150% and Windows display
DPI changes; modal commit, Reset and empty pins; exhaustive actions and header
panning; paste offsets, bookmarks, object matching and numeric rig switching;
legacy-strip migration; save/reopen; multiple editors/windows; hide/show and
disable/re-enable lifecycle; native playback/scrub/keying; and fallback in an
unpatched runtime. Keep those claims open.

The catalogue statically exposes 89 existing Anim Assist actions across seven
families, with direct quick buttons, Search and Pin. Representative toolbar
actions were used above; every operator algorithm was not individually
qualified. This release does not claim full AnimBot algorithm or gesture
parity. No formal test suite was run.
