# Procedural whole-body preview strength v1

## Result

The B4Artists temporal preview now exposes a bounded `Procedural Motion Strength` control from `0.0` through `1.0`. This is an animator-facing control for the existing authored-motion procedural preview; it is not a learned model, a learned-motion claim, or a model-promotion event.

- `0.0`: exact endpoint-interpolation baseline.
- `1.0`: the full deterministic procedural trajectory proposed by the current preview backend.
- Between `0.0` and `1.0`: linear position blending and shortest-path quaternion slerp between those two procedural results.
- The selected value is captured when generation starts. Changing it during a live preview aborts that preview and requires regeneration, preventing a mixed-strength candidate.
- The candidate action records `b4ml_temporal_strength` and `b4ml_temporal_learned=False`.
- The visible source is restored through the existing preview transaction (`finish_preview`), and the candidate remains separately editable.

The UI labels the feature explicitly as procedural and tells the animator that the strength blends toward endpoint interpolation. It does not alter Ghost Tool or Anim Assist, and it does not close the learned-temporal, independent-animator, or Cascadeur gates.

## Verification

Source-level checks passed on 2026-09-13:

- Focused strength contract: 4 tests passed.
- Combined temporal/data regression set: 47 tests passed.
- AST parsing: all six modified runtime/test files passed.

The focused Bforartists host suite ran 9 assertions and reported `TEMPORAL_PREVIEW_RESULT: PASS`, including capture/marking of a 25% procedural candidate, cancellation, save/reload cancellation, source recovery, operator behavior, and duplicate-hook protection. The Bforartists process still exited with the previously recorded `ucrtbase.dll` shutdown access violation (`3221225477`) after the passing assertions; this is recorded as an unclean host exit, not hidden as a clean pass.

Host provenance:

- Executable: `X:/5.1.0/bforartists.exe`
- Core: Blender 5.2.0 Alpha, build `dd23ab17120d`
- Executable SHA-256: `C0BF2F3A3FCDDE65C2285FE7FBA3F387A6DB2AA09F35309D2B1716DD08BB723A`
- Command: `bforartists.exe --background --factory-startup --python-exit-code 1 --python tests/test_b4artists_ml_temporal_preview_v1.py`

Machine-readable evidence is in `training/b4artists_ml/results/temporal-procedural-strength-v1.json`.

### Current-worktree ownership recheck (2026-09-14)

The preview entry point, production private generator, and research cooperative
generator now use the same fail-closed ownership boundary. In addition to pose,
body, quadruped, candidate, contact, flight, and retained-motion-layer state,
they reject live body solving, contact suggestion, secondary motion, cleanup,
and body-live work. A conflicting workflow that appears between cooperative
pauses is rejected before temporal publication while preserving the visible rig,
source Action, playhead, object inventory, and ownership cleanup.

The current-worktree recheck runs the three affected suites in separate
Bforartists processes. This avoids save/reload tests carrying earlier generated
Rigify fixtures into later suites; that fixture accumulation is a harness cost,
not product behavior. All 31 assertions passed with zero failures, errors, or
skips: 10 preview lifecycle, 10 production private-generation, and 11 research
cooperative-generation tests. Each host wrote its passing marker before the
established `ucrtbase.dll` shutdown access violation, so clean host exit remains
unclaimed.

Evidence:

- `training/b4artists_ml/results/current-temporal-ownership-recheck-v1.json`
- `training/b4artists_ml/results/current-temporal-ownership-recheck-validation-v1.json`
- Receipt SHA-256: `ff3209965971932db20e012005bc0c27b5fd5a0fd89f52d7ef6d9a888a5d316e`

This is current-worktree workflow-ownership and recovery evidence only. It does
not qualify an exact package, learned temporal quality, model training or
promotion, independent animator usability, Cascadeur parity, or the full goal.

### Full affected temporal matrix (2026-09-14)

The same isolated-host method now covers all eight affected temporal suites.
All 81 tests passed with zero failures, errors, or skips. Coverage includes the
preview and production private paths, guarded source and cooperative projection,
exact observation parity, all supported humanoid adapters, authored-anchor
sampling, cancellation, stale-edit rejection, failure rollback, editable
candidate publication, and save/reload source recovery.

The receipt binds all 44 current runtime Python modules plus 17 direct temporal,
fixture, runner, and validator sources. Each of the eight Bforartists processes
wrote a passing assertion marker before the established alpha-host
`ucrtbase.dll` shutdown fault; clean process shutdown remains unqualified.

Evidence:

- `training/b4artists_ml/results/current-temporal-affected-recheck-v1.json`
- `training/b4artists_ml/results/current-temporal-affected-recheck-validation-v1.json`
- Receipt SHA-256: `56b30e3b6394a681047b7956cef84c248ed6adca7452bf5b40ba1bd6206d1a7d`

This broader result remains current-worktree regression evidence. It does not
replace exact-package qualification or satisfy learned-quality, independent
animator, matched Cascadeur, or full-goal acceptance.

## Changed surfaces

- `b4artists_ml/temporal_math.py`
- `b4artists_ml/temporal_generation.py`
- `b4artists_ml/temporal_preview.py`
- `b4artists_ml/ui.py`
- `tests/test_b4artists_ml_temporal_strength_v1.py`
- `tests/test_b4artists_ml_temporal_preview_v1.py`

This slice advances the required preview/strength/selectivity workflow while preserving the product boundary: procedural output remains procedural, and failed learned holdout candidates remain research-only.
