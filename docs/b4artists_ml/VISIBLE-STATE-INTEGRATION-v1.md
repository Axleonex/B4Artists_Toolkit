# Exact pose comparison integration

The local source now uses reusable RNA buffers to compare the source pose during temporal generation. It retains frame, raw and derived rotation, channel availability, rig modes and object transform checks. Every existing transaction guard and its frequency remain unchanged. No live bone pointers are cached. Unsupported batch reads fall back to the original complete comparison.

The prior implementation is preserved in training/b4artists_ml/results/visible-state-production-baseline-v1/temporal_generation.py. The revision receipt verifies that all other functions/classes and VisibleState.restore retain identical ASTs.

## Evidence and limits

- Research differential checks: 100 cases agreed with the original, including all rotation modes and active/inactive channels; transaction rejections also passed.
- Fixed serial default-Rigify workflow comparison: original median 24.4608 seconds, bulk median 21.3636 seconds, 12.66% less elapsed time, exact curves/handles and preserved source/inventory. This measured the isolated candidate before integration.
- Integrated native checks: 24 tests across four suites pass, covering exact comparisons, private generation, fallback, source-edit rejection, cancellation and preview recovery.
- A first test attempt failed its own restoration assertion: switching rotation modes converts stored RNA values. The corrected fixture restores both the enum and original channel values. The failed result and original fixture remain preserved.
- The remaining 39 native suites are running under the frozen visible_state_production_regression_plan_v1.json. Combined qualification requires all 414 cases across 43 unique suites, unchanged runtime hashes and zero skips/errors/failures.
- Native processes still report the previously reproduced post-assertion access violation (3221225477). Passing assertions do not establish clean host shutdown or GUI usability.

No new archive has been built. Experimental 0.19.1 remains the previously tested build and does not contain this source change. No commit, push or installation occurred. The complete learned-motion, physics, human usability and Cascadeur comparison requirements remain open; nearby model fitting stays paused.

Next: finish the current regression handle, verify the integrated implementation in the serial workflow benchmark, then build and check the exact new archive if validation passes. Preserve the original goal and its limits.
