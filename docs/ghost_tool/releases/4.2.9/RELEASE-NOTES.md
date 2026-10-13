# Ghost Tool 4.2.9 — candidate

Every section in the Ghost menu now has an identifiable control in the viewport toolbar. Ghosts On / Turn On Ghosts is a direct state toggle. Marker options and Onion Skin options are named dropdown buttons, alongside Motion Paths, Edit Motion, Compare, Physics, Look and Settings.

Show Markers and Show Onion Skin remain adjacent one-click generation actions. Opening a section dropdown opens the existing shared controls without regenerating previews. Ghost retains the overall menu and Hide/Show Toolbar recovery.

Object/Pose viewports retain the same complete labelled row at every width and UI scale. Middle-mouse drag the native Tool Settings row horizontally to reach offscreen sections. Other modes retain their existing Ghost menu. This change adds no sampling or authoring logic.

The exact candidate ZIP passes **89 focused tests/checks in Bforartists 5.2.0**: 54 background tests and 35 native split-view checks. These cover names and master state, generation/options separation, width/scale consistency, panning, new splits, hide/show and frame/cache preservation. The new named-controls regression failed on the previous drawing code before implementation. See the [package receipt](package-receipt.json).

This is an **unpublished candidate awaiting merge, push and release approval**. The [candidate ZIP](../../../../releases/b4_ghost_tool_v4.2.9.zip?raw=1) and updated PDF are prepared locally. Published 4.2.8 and all historical receipts remain intact. After installing a candidate or release, restart Bforartists. Production rigs, complete keyboard navigation and alternate themes are outside this focused verification.

## Evidence and UI review

The new `test_named_sections_and_direct_master_state_match_the_menu` regression failed on the previous source (`'' != 'Marker options'`) and passes on this candidate. All four focused background suites pass: toolbar 8, display/migration 18, cache 8 and authoring 20. Eleven additional native per-viewport checks confirm the section names and master switch; the full native run passes 35 checks.

Inspected native captures are in `build/ghost-toolbar/release-4.2.9/`: `split-object.png` shows the direct master and named marker/skin controls in both viewports; `split-panned.png` shows the remaining named sections. The initial GUI run crashed in the host's OpenImageIO library. The successful retry limited the disposable native GUI host to two threads, using its documented `--threads` option, without changing add-on behavior or patching the platform gate. Background results were reused through a checkpoint bound to the unchanged exact ZIP. Output is captured to files to avoid Windows pipe-reader thread allocation failures.

UI review: R1/R3/R5/R9/R11 PASS through retained generation actions, menu access, shared named options and existing tooltips; R6 PASS for the native header toggle; R10 PASS through missing-target options and existing action polling; R12/R14 PASS through consistent labels, width/scale tests and native panning. The Fable contract uses existing host typography, colors and control sizes; native screenshots and the three-page PDF were inspected. No operator execution, panel-header icons, Tool Shelf placement or panel-body property styles changed. Broader keyboard/theme/rig behavior is not verified by this layout test. Deviations: none in scope.
