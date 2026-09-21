# Observed kinematic conditioning result v20

The learned548-input candidate improves average error but fails qualification. No temporal weights are promoted. The original full goal remains active and experimental addon0.17.2 is unchanged.

## Unchanged gates

Every ratio uses the strongest matched projected linear, Hermite or shape control for that metric. Old, v19-added and combined validation are independently gated. Both individual sets are exposed development data.

| Partition | Position improvement (need >=5%) | Rotation ratio (<=1.02) | Velocity ratio (<=1.05) | Acceleration ratio (<=1.05) | Worst positional cohort ratio (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | 4.130% | 0.984941 | 0.978272 | 1.035119 | 3.048147 | FAIL |
| new_validation | 6.785% | 0.979993 | 0.989606 | 1.021501 | 3.142469 | FAIL |
| combined | 5.828% | 0.975508 | 0.975514 | 1.019753 | 3.142469 | FAIL |

Position improvement now passes on the newer and combined sets, but still misses5% on the original set. Worst-cohort protection fails in every partition and deteriorates relative to v19: old2.26349 to3.04815, new2.90697 to3.14247. Every remaining gate passes, including exact priority transforms and true physical edges. All six original per-partition control reports and all combined control reports remain exactly unchanged.

The old worst cohort28_01/gap32/context1 has learned error0.227447 versus projected linear0.074618. The new worst cohort138_11/gap8/context1 has error0.044582 versus Hermite0.014187. Aggregate improvement cannot conceal these regressions or qualify the model. Neither acceptance thresholds nor holdout membership changed.

## Evidence

The corrected feature representation retains34 explicit motion amplitudes alongside306 normalized motion descriptors and208 unchanged pose/rest/mask/timing values. Complete feature-only reconstruction, time-scaling and theoretical bounds pass across7358 training windows. Seven synthetic/corpus feature checks and seven learned calculus/inference checks pass. The original weaker reconstruction receipt and its pre-fit correction are retained; see KINEMATIC-TRAJECTORY-PLAN-v20.md. No hidden validation labels entered feature construction or model fitting.

On training-only catalog-prefix-excluded predictions, raw positional error falls from0.145961 in v19 to0.142662; the shape reference remains0.146644. This is2.71% below that reference, versus0.47% previously. The diagnostic is separate from projected validation and provides no human-quality or physics qualification.

Two complete independent runs reproduce all six NPZ artifacts exactly. Protocol, manifest, fold assignments, training diagnostics and frozen selection are also identical. Non-runtime reports match after verifying actual model paths/hashes and normalizing only their output-directory prefixes. Model SHA256: `9e4d2a6f4f5a08bd6b9f814df064eaee276866afaddc5b1ceaa0faefe9c996a3`. Both runs retain the same training settings,64 hidden units and612 output values; the34 extra inputs add2176 weights. No performance conclusion is drawn from concurrent runs.

Sixteen moving and sixteen stationary actual-rig cases pass on the eight existing fixtures, including context off/on, editable generated actions and source recovery. The known background host shutdown crash persists after assertions complete (exit3221225477). A bounded check of obvious X-drive/Program Files locations found no alternative Bforartists installation; this is not an exhaustive machine inventory.

Six fresh confirmation clips remain absent because development gates fail. No new data was downloaded. The0.17.2 package and addon source remain byte-identical, preserving prior317-case behavioral coverage,124 offline package cases and six actual-window events as retained evidence. Those complete suites were not rerun. No install, commit or push occurred.

## Next work

The next learned investigation should distinguish the loss function's emphasis on average error from the requirement to protect difficult cohorts, using training-only evidence before another prospectively fixed model. Do not tune v20 on these development results or expose confirmation.

Also prioritize a concrete motion-review artifact that makes failed examples inspectable and measured viewport-responsiveness work. Research metrics alone do not complete an animator workflow. Original physics/refinement, style/timing and partial-body interpolation, production humanoid/quadruped support, optional connector, distribution evidence, independent usability and equivalent Cascadeur comparison remain required. Preserve the same goal ID,50 total evaluations and15-hour resumed cap.
