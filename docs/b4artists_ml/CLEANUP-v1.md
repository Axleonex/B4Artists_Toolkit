# Animation cleanup — 0.32.0

Status: integrated and packaged in experimental 0.32.0. The frozen source and extracted archive have both passed their release gates.

## Animator workflow

Animation Cleanup works on the currently selected generated candidate. The animator can clean selected captured controls or every captured control, enable handle smoothing and redundant-key reduction independently, set strength and tolerance, and inspect the result before Keep or Discard. The operation is cooperative and cancellable with Escape. It publishes a separate editable action and retains the exact input for Restore Input and later Restore Source Animation.

The panel reports before/after key counts, removed keys, cleaned curves and controls, accepted-contact protection, maximum measured contact position and rotation drift, scalar derivative-jump measurements, and skipped unsafe curves. The action stores the request and result metrics used to produce it.

The implementation is deterministic and records `learned=false`. It does not satisfy the learned inbetweening requirement.

## Preservation and failure behavior

- Every captured priority frame keeps its exact authored key value, including fractional frames.
- Accepted contact controls and their pose ancestors are excluded from curve edits. Contact positions are evaluated on the input and output at each interval boundary, midpoint, and enclosed priority frame.
- Quaternion groups are validated and are never key-reduced. Axis-angle controls, sampled curves, muted or locked curves, curves with modifiers, and unsafe quaternion groups are skipped.
- Smoothing adjusts handles only. Reduction removes keys only when the reconstructed curve remains within the configured error tolerance at the original key times.
- The input action is token-checked and never edited. Changed settings, anchors, contacts, playhead, input animation, active candidate, cancellation, and validation failure restore the exact input.
- Load, save, Undo, and Redo handlers stop unfinished work. Keep/save/reload and Restore Source Animation have native coverage.

Contact sampling is grouped by unique frame. The generated Rigify cat fixture checks four accepted paw contacts at twelve contact/frame pairs using three unique frames and six dependency-graph evaluations across the before/after validation passes.

## Native evidence

The focused Bforartists suite passes five workflows: BoneForge captured-control cleanup with two accepted foot contacts, cancellation and stale-request rejection, exact fractional priorities, generated Rigify Default keep/save/reload/source recovery, and generated Rigify cat cleanup with four accepted paw contacts.

Measured focused results on the installed Bforartists 5.1.0 / Blender 5.2 Alpha host:

| Fixture | Keys | Removed | Contact samples | Max position drift | Max rotation drift | Elapsed | Step p95 | Worst step |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BoneForge humanoid | 2,942 → 2,135 | 807 | 6 | 0 | 2.98e-8 rad | 725.43 ms | 5.26 ms | 46.42 ms |
| Generated Rigify cat | 4,301 → 2,816 | 1,485 | 12 | 0 | 0 rad | 3,605.54 ms | 12.03 ms | 93.80 ms |

The humanoid derivative-jump metric changed from 0.199988 to 0.0006035 while retaining both authored priorities. These are single-run engineering measurements, not a broad responsiveness or visual-quality claim.

The fresh affected regression passes 110 tests across ten suites with no failures, errors, or skips and one consistent runtime hash set. Its SHA-256 is `51232ab29b4af228b95fe99875072ef5c89f232c5fb9a351f07211d88599e1ca`.

The real-window v4 workflow passes modal Escape, Undo/Redo, Keep, and Restore Source Animation. Its selected-control candidate removed 54 keys, completed in 208.76 ms, and measured a 36.83 ms worst cooperative step. The JSON evidence SHA-256 is `d61d8a160a00b43b1e81bad454a073bbbcc6b4b6cf80f342c2ad503216bc4d90`; the screenshot SHA-256 is `1c2c753593c6ab748bdf769af1f16a91dc6a5cbf4cbe0cc76384e2b566188184`.

Evidence files:

- `training/b4artists_ml/results/cleanup-v1.json`
- `training/b4artists_ml/results/cleanup-v1-affected-r4-regression.json`
- `docs/b4artists_ml/cleanup-ui-v4.json`
- `training/b4artists_ml/cache/cleanup-ui-v4.png`

The installed Alpha host still raises the independently isolated `ucrtbase.dll` exception during shutdown after writing passing reports. Clean shutdown is not claimed.

## Execution and review boundary

The required Code Router received the exact five-file coding packet. Windows failed in its uv trampoline; the WSL entry point then returned `REMOTE_EXECUTOR_REQUIRED` for `NUCBOX_M6ULTRA` before selecting a lane. Therefore no `actual_lane` or `actual_lane_reason` exists and none is inferred.

The live adaptive policy is owner-authorized production, starts execution at two with ceiling eight, and declares reviewer maxima S0=0, S1=1, S2=2, S3=4, and S4=4. Its Codex payload is unexpired through 2026-10-11T09:25:49.455367Z, contains a complete 21-identity workspace matrix, and matches the current source, implementation, grant reference, and expiry. The current process cannot access the required Codex host authority key, so zero identities validate. Adaptive execution and reviewer overlays fail closed to serial operation; no worker or reviewer was dispatched.

## Release boundary

The cleanup panel exposes removed-key count, accepted-contact/sample count, position and rotation drift, reduction error, derivative continuity and safely skipped curves. The complete frozen source passes 495 tests across 55 suites, and the exact archive passes 18 offline package tests. Independent animator visual assessment, learned cleanup, broader physics, and Cascadeur comparison remain open.

Ghost Tool and Anim Assist remain unchanged. No commit, merge, push, install, or package publication occurred.
