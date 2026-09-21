# Reviewed paw-contact suggestions — experimental 0.31.0

Generated Rigify cat, horse and wolf candidates can now suggest four-paw holds using evaluated motion and an explicit support plane or static planar mesh. Suggestions remain provisional until the animator accepts them. They feed the existing copied-action correction workflow; they do not generate a learned gait.

## Workflow

1. Generate and select a Pose Blending candidate with all four native limbs in IK.
2. Open Four-Paw Contacts. Choose a static planar Support Surface or set the support plane point and normal.
3. Set the distance, speed, minimum-hold and gap thresholds. Quadruped distance and speed use the evaluated body-to-paw reference distance; humanoid thresholds retain leg-length units.
4. Click Suggest Paw Contacts. Inspect each provisional interval, score and reason, then accept, edit or reject it. Matching grounded priority poses and low surface speed are heuristics, not reviewed training labels.
5. Click Preview Four-Paw Correction. Inspect the result, then keep, discard or restore it through the existing candidate controls.

Accepted contacts survive rescanning. Escape cancels scanning without publishing partial proposals. Save/reload preserves provisional status and accepted holds. Fractional priority frames are included in sampling.

## Correctness fix

A new native regression reproduced three early-preparation failures: changes to scene frame rate, priority-pose frames or the rig transform after the first cooperative yield did not cancel scanning. Their snapshots now precede that yield. The same test passes after the fix; failed evidence remains in `training/b4artists_ml/results/paw-suggestions-stale-v1-regression.json`.

## Evidence

The affected source first passed 17 tests across four factory-startup suites: quadruped suggestions, humanoid suggestions, quadruped correction and interval detection. The extracted 0.31.0 archive passed 10 focused tests with Python outbound/process calls denied and all loaded add-on modules verified inside the extracted package.

A subsequent frozen-source regression passed all 487 tests in 53 factory-startup suites with no assertion failures, errors, failures or skips. Every suite recorded the same runtime hash set, and that set matches both the current source and the exact 0.31.0 package manifest. The aggregate SHA-256 is `d58e9cb40dd9dc75ce717286106bbe9bcae6ae3d81a2122950d33b49935daa06`; the compact result is `training/b4artists_ml/results/full-regression-031-v1.json`.

| Generated rig | Suggestions | Scan time, 11 frames | Corrected maximum normalized error |
|---|---:|---:|---:|
| Cat | 4 | 79.1 ms | 0.0000010064 |
| Horse | 4 | 87.0 ms | 0.0000005999 |
| Wolf | 4 | 80.3 ms | 0.0000004697 |

These are single background fixture measurements, not real-window responsiveness or production-scene benchmarks. Correction error is normalized by body-to-paw distance, with the existing acceptance bound of 0.0002.

Evidence: `paw-suggestions-v2-regression.json` and `paw-suggestions-package-v1.json` under `training/b4artists_ml/results/`. The 49-file package is `releases/b4artists_ml_v0.31.0.zip`; SHA-256 is `8e80a4acf7f0ae388e2ad58522bf2987e1d87b90f6368dbe759d657b1c15c453`.

## Limits and orchestration

Arbitrary/deforming surfaces, moving platforms, imported/custom quadrupeds, learned gait, independent animator assessment and matched Cascadeur comparisons remain unqualified. The installed Bforartists Alpha build still exits with its previously isolated `ucrtbase.dll` shutdown crash after recording results. The 487-test regression qualifies source behavior, not clean host shutdown.

The canonical coding entrypoint was attempted but failed before lane selection because its Windows evidence interpreter could not launch. The refreshed owner-production verifier also failed closed on Windows and WSL because neither process could access a qualifying host signing key; the unexpired production state, source/implementation bindings, grant reference and Codex `workspace` identity otherwise matched. Work therefore continued serially under the current native-fallback policy. No parallel workers, adaptive reviewers or career overlays were admitted, and no lane or reviewer authority was invented.

The existing goal ID and 78 completed evaluations are preserved. The user-authorized deadline is September 13, 2026 at 05:22:33 Eastern, with a total ceiling of 100 evaluations. Formal assessment remains pending: the issuer reports that the goal workspace is not host-approved. No acceptance checks, regression floors or history were reset, and no signed acceptance was fabricated.
