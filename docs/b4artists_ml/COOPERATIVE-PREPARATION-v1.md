# Cooperative rig preparation

The temporary evaluation rig now prepares in stages on the main thread. The live solver can cancel between dependency analysis, data copying, bounded driver and constraint batches, scene creation and bone pruning. It never yields in a temporary context override or Edit Mode. Direct synchronous callers use the same preparation sequence without waiting for timer events.

Every resumed solver stage retains source validation. A source-state error also revalidates before automatic proxy fallback, preventing a new host fit after the original frame or ownership has changed. Closing a pending stage restores the preceding preview and releases temporary objects, armatures and scenes. Fitting mathematics, learned weights, finite-difference probes, constraint closure, acceptance tolerances and final pose checks remain unchanged. Preparation timing excludes time suspended between timer events.

The original profile identified a 144 ms first solve tick, including 79 ms preparation, under cProfile. Those numbers are cost-center observations, not qualification. Two separate counterbalanced comparisons without cProfile used the immutable 0.17.2 release and current source, with the same real-rig fixtures, logical clock, two edits and source recovery. The final comparison repeats after the source-invalidation guard fix.

| Default Rigify, final comparison | Released | Staged |
| --- | ---: | ---: |
| Average first active tick |146.6 ms|39.5 ms|
| Average of each solve's worst tick |146.6 ms|95.6 ms|
| Total active solve work ratio |1.00|1.091|

Both comparison batches passed the declared preparation gates. Each tested pose, authored request, accuracy metric, evaluation count and iteration count exactly matches the released version on all five profiles. Rigify basic also showed shorter pauses. The single basic/default metarig pairs and BoneForge results are diagnostic; no universal speedup is claimed. Default metarig total active work increased 16.2% in the final pair. Scheduling extra validation checkpoints adds overhead even when it shortens individual pauses.

The first candidate comparison had default Rigify first/worst averages 35.9/82.3 ms versus 152.9 ms released, with 8.3% more total work. The final comparison above is the current-source evidence. Variability between batches is retained; neither batch is a real UI event-queue latency measurement. Remaining ticks exceed 50 ms and complete solves still take seconds. The original full responsiveness gate remains failed.

Thirteen staged proxy cases passed, covering 25 random control samples on each of five profiles, complete host/proxy solves, cancellation at every preparation boundary, failure cleanup, pose-mode context preservation, frame-dependent drivers, external-dependency rejection, mismatched-copy fallback and save/reload cleanup. An initial new test expected the live-layer frame error wording; it was corrected to the existing solver-layer message, with the original failure and source snapshot retained. A later review added an explicit zero-fit-after-source-invalidation assertion for automatic fallback.

The complete wider regression passed 321 cases on the current behavior, including 13 staged proxy cases. Four additional checks loaded the exact 0.17.3 ZIP, denied outbound Python networking/process launches and verified two target edits followed by Keep or Discard on BoneForge/default Rigify. Only the version literal changed after the full regression; archive/source parity is checked. Current-package UI events and independent human assessment remain unverified. The host continues to crash on shutdown after assertions; that is not treated as a clean host exit. No temporal model, independent animator approval or Cascadeur parity is claimed.

Evidence: `training/b4artists_ml/cooperative_preparation_plan_v1.json`, `results/active-preview-profile-v1.json`, `results/preparation-benchmark-v1.json`, `results/preparation-benchmark-v2.json`, `results/cooperative-proxy-final-v1.json`, and their process/source receipts.
