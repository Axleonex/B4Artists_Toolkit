# Ghost Tool 4.2.2 authoring pause

Date: 2026-10-12. Status: local repository test build; Bforartists production-rig acceptance pending.

The owner still sees jitter in 4.2.1 with auto-key and Update While Scrubbing enabled.
The requested behavior is a stable cached overlay during a move, then a refresh after the move ends.
Both timeline-update controls must default off and use distinct names.

## Findings and change

Inspection found that both properties defaulted on and both Show operators unconditionally enabled
them again. The old guard checked only `TRANSFORM_OT_*`; a native gizmo, pose operator or timeline
scrub can own another modal handler. The dependency handler also scheduled sampling for any Object
notification, including our ghost meshes and unchanged objects.

- The controls are **Live Update Markers** and **Live Update Skin**, both default off. Show Markers
  and Show Onion Skin preserve each setting. Existing saved scenes retain saved choices.
- Native modal operations hold the cached overlay. The final sampling boundary also refuses to
  step frames during a native gesture. Ghost Tool's own controlled gestures retain their existing
  SessionState protection and are allowed to sample.
- Original object/pose channels, custom controls, source mesh geometry, shape keys and Action contents distinguish an
  authored change from selection, frame evaluation and our own display updates. Ghost meshes are
  excluded. Constraint and modifier control changes also invalidate the source state.
- Animation changes keep a pending refresh while moving. The live timer waits for the gesture to
  end and a 150 ms quiet period, then refreshes existing marker and skin snapshots. The live toggles
  separately decide whether each overlay follows timeline movement. Freeze pauses automatic updates.
- Frame changes remember the newly evaluated source state without classifying normal scrubbing as
  an edit. With both live toggles off, scrubbing leaves the cached geometry in place.

Selection alone does not pause updates indefinitely. Holding a move, rotate, scale, native pose
gesture or scrub does. A completed edit updates the snapshot at the current frame.

## Evidence

The six new background regression cases failed on the previous source before the change, covering
defaults, generation overrides, native modal ownership, the sampling boundary, ghost notification
feedback and edit refresh with timeline following disabled. The guard cases simulate modal lists;
they do not prove native gizmo interaction on the owner's host. A source-geometry regression
also failed during development and passed after restoring detection of mesh-coordinate/topology
edits without feeding generated ghost mesh notifications back into sampling.

The package runner extracts the exact 4.2.2 ZIP into an isolated installation and verifies all
29 source modules byte for byte. It runs nine separate background processes, plus a factory GUI
engine with real native event simulation. Results and the archive checksum are in
[package-receipt.json](package-receipt.json); native cases are in [native-results.json](native-results.json).

- **230 background checks pass** across nine suites, including **20 authoring regressions**.
- **Five native GUI cases pass**: object moves with live updates off/on, pose-bone moves with live
  updates off/on, and cancellation of an object move. All use the real `TRANSFORM_OT_translate`,
  numeric keyboard input and auto-key. For three timer ticks during each move, the authored position
  remains stable, cached marker/skin geometry stays unchanged and the live backend runs zero times.
  One refresh occurs after confirming or cancelling. Seeking away and back verifies the keyed pose.
  With live updates off, seeking also preserves the last cached overlay.
- Host: Blender 5.1.2, build `ec6e62d40fa9`. Only the Bforartists registration gate is patched;
  native transforms, auto-key, mesh deformation, frame evaluation and shipped sampling logic run
  unchanged. Bforartists is unavailable on this host.
- The nine-suite run does not repeat the stand-in annotation or fresh-child persistence suites;
  their earlier host limitations remain documented in the [4.2.1 report](../authoring-fix/verification.md).

The old 4.2.1 release and ZIP are retained as history. This candidate is not published. These checks
do not establish that the owner's production rig is free of jitter.

## UI and execution record

The existing two property locations remain. R6 setting-not-button and R11 explains-itself pass:
the renamed controls draw as checkboxes and explain timeline following, edit refresh and gesture
pause. The existing Freeze toggle stays in place to avoid an unrelated panel change. Bforartists
panel width and native gizmo/pose gesture usability remain unverified.

Code Router: recommended/actual `T3_PRIME_OMP`, policy fingerprint
`29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8`.
Code Evaluator classification returned INCONCLUSIVE; no independent reviewer was invoked.
Windows preflight reports that the Unix-socket OMP relay cannot run in this process. The static
policy permits native continuation within the declared repair, tests, packaging and documentation
scope. Doctor reports Orca blocked and Windows Herdr runnable. No provider or infrastructure change
was made. No independent model-review PASS is claimed.

## Owner check

Install `releases/b4_ghost_tool_v4.2.2.zip`, then restart Bforartists. In an existing saved scene,
turn **Live Update Markers** and **Live Update Skin** off once if their old values are still on.

With auto-key enabled, grab the animated object or pose control. Hold and move it for several
seconds. The model should follow your input; cached ghosts should remain still. Confirm, wait for
the refresh, then scrub away and return. The authored key should survive, and the cached overlay
should remain at its last refresh when live updates are off. Repeat with a gizmo, rotation, scale,
cancel, and both live settings enabled. Also test the existing Ghost Tool marker and path-handle
drags. Record the Bforartists build and the first failing step if jitter remains.

[PowerShell] Reverify the unchanged candidate:

```powershell
rtk proxy python docs/ghost_tool/authoring-pause/package.py
```
