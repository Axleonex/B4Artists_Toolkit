# Ghost Tool 4.2.1 authoring repair

Verification date: 2026-10-11. Publication: [4.2.1 prerelease](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.1), 2026-10-12; Bforartists viewport acceptance pending.

The reported symptom was jitter and inability to author a new keyframe with Ghost Tool enabled.
Direct repository inspection found that object depsgraph changes schedule live frame sampling.
`utils.scene_sampling` previously restored only the frame and subframe. Returning to that frame
evaluates the existing animation again, replacing unkeyed object and bone channels.

## Reproduction and change

Two behavioral tests failed before the fix in Blender 5.1.2. An authored object location of
`(8, 9, 10)` became `(0.4638671875, 0, 0)` after sampling or a live refresh.
The playhead still returned to frame 7.25, so frame restoration alone did not protect the edit.

Sampling now saves and restores original object and pose transform inputs, object delta
transforms, numeric object/bone custom controls, and shape-key values. Restoration runs after
frame restoration and before sampling suppression ends, including nested and error paths.
Scene view layers update afterward so the viewport uses the restored pose.

Live refresh, forced mesh refresh, and deferred path marker refresh wait while a native
transform operator is active. Persistent Ghost Tool hover operators do not block refresh.
Draw to Keys explicitly opts out of pose restoration because it intentionally writes animation.

The source change from committed 4.2.0 touches five modules: `__init__.py` (version only),
`utils.py`, `ghost_pipeline.py`, `motion_paths.py`, and `draw_to_keys.py`.

## Verification

The package runner extracted the exact ZIP into a temporary installation and ran each suite
in a separate factory-startup Blender process. It checked archive bytes against working source.
All 29 modules matched. Host: Blender 5.1.2, build `ec6e62d40fa9`.
Only the Bforartists detection gate was patched in the test bootstrap; shipped code keeps its gate.

- 13 focused authoring checks passed: repeated live refresh followed by new key insertion;
  frame/subframe restoration; same-frame sampling; nested/error restoration; Euler, quaternion,
  axis-angle and delta channels; custom controls; shape keys; real mesh and motion-path sampling;
  native transform deferral; marker deferral; and intentional Draw to Keys writes.
- Across 10 suites, 239 checks ran and 229 passed.
- Nine annotation cases fail because this Blender stand-in cannot construct annotation strokes
  through the test's `strokes.new()` API. The prior 4.2.0 ZIP fails the same nine cases with
  the same exception signatures. A separate new test supplies synthetic stroke geometry and
  exercises the actual Draw to Keys operator and resulting animation evaluation successfully.
- One fresh-process persistence case fails because the child Blender process correctly refuses
  Bforartists-only registration. The prior 4.2.0 ZIP fails the same case at the same gate.

Full output and baseline comparisons are beside this report. Machine-readable results,
source hashes and archive SHA-256 are in `package-receipt.json`.

## Evidence audit

| Gate | Failing state | Evidence | Boundary |
|---|---|---|---|
| Unkeyed edit survives sampling | Existing keyed value replaces authored location | Both reproduction tests were red before the change and green afterward | Real Blender evaluation, disposable synthetic rig |
| Authored pose can be keyed | New key stores old animation values | Repeated refresh, insert, seek away and return; compare authored values | Real Blender key insertion |
| Native transform blocks sampling | Timer runs generation while transform is active | Generation mocks must receive zero calls, then resume after modal removal | Simulated modal list; viewport interaction pending |
| Archive matches tested source | One archived module differs from source | Compare every module byte; import only extracted package | Packaging integrity, not usability |
| No newly introduced supplemental failures | Candidate fails additional cases or different reasons | Prior 4.2.0 ZIP run through identical test/host path | Ten host-limited cases remain unresolved |

These checks were written and inspected in this session. They do not replace an independent
review or a test on the owner's production rig in Bforartists.

## Owner check

Install `releases/b4_ghost_tool_v4.2.1.zip` over 4.2.0 and restart Bforartists.
With Ghost Tool and live ghosts enabled, move/rotate a keyed control at another frame,
confirm the transform, wait for refresh, then insert a new key. The authored pose should remain
stable during the operation and after refresh. Seek away and return to confirm the new key.
Repeat with auto-key enabled and with a mesh ghost or pinned motion path visible.

[PowerShell] Reverify the existing ZIP without replacing it:

```powershell
rtk proxy python docs/ghost_tool/authoring-fix/package.py
```
