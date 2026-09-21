# Learned position mixture result v21

The fixed learned mixture improves average motion error and reduces difficult-case failures, but still fails qualification. It remains research code; no temporal weights are bundled. The v0.17.4 runtime and installable ZIP are unchanged, and the full original goal remains active.

## Unchanged quality gates

Each ratio uses the strongest matched projected linear, Hermite or shape control for that metric. Old and v19-added validation are both exposed development data; both partitions and their combination must pass independently.

| Partition | Position gain (need >=5%) | Rotation (<=1.02) | Velocity (<=1.05) | Acceleration (<=1.05) | Worst position cohort (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | 7.396% | 0.983566 | 0.942261 | 1.006719 | 1.712332 | FAIL |
| new_validation | 7.749% | 0.980554 | 0.972527 | 1.005908 | 1.371989 | FAIL |
| combined | 7.622% | 0.975391 | 0.952790 | 1.000860 | 1.712332 | FAIL |

Average position now passes in every partition. Worst-cohort ratios improve from 3.048 to 1.712 on the old set and from 3.142 to 1.372 on the newer set, but still fail the unchanged 1.10 ceiling. Exact priority transforms and physical edge lengths pass. All procedural control reports, source windows, data ownership and projection settings are unchanged.

Of 96 cohorts, 11 fail, compared with 25 in v20. Fifty-four improve and 42 worsen numerically. Two formerly passing cases now fail: 118_01/gap32/context1 and 13_12/gap32/context1. The remaining old worst case is 28_01/gap32/context1. These failures cannot be hidden by the aggregate gains, and this candidate is not promoted.

## What was learned

A 548-input, 32-hidden-unit tanh network learns four softmax weights from known pose/context/timing features. The weights combine linear, Hermite, shape and frozen v20 positions across the interval. Raw rotations remain v20 predictions; final rig projection can change rotations in response to the new positional targets. Each positional coordinate stays within the four raw expert proposals; that bound does not guarantee better quality than the best expert, collision avoidance or physical acceptance.

For each of the 7358 training windows, the learned v20 expert comes from the existing parent model that excluded the entire catalog group. Exact fold membership and model hashes are checked. The gate sees all training labels; this is training evidence, not independent gate validation. One prospectively fixed configuration was fit, with no hyperparameter grid or validation tuning. Both development partitions were loaded only after weights were frozen.

The recorded training objective decreased 12.58%. Separating the weight penalty shows a 5.72% reduction in the trajectory data objective itself, so the decrease was not solely weight decay. This training result does not establish generalization or animator quality. Existing parent weights were reused and verified, not retrained in this experiment.

## Verification

Fourteen pre-fit checks pass: explicit versus compressed trajectory loss, finite-difference gradients, supervised hidden-feature learning, parent preservation, convex position bounds, unchanged raw parent rotations, exact priorities, label separation, stationary and masked-context invariants, exact serialization, malformed-model rejection, query validation and stable softmax. The initial learning check used nearly identical motion experts and missed its feature-change threshold; its source and result are preserved. A controlled synthetic positional signal strengthened the fixture without changing the model or lowering the assertion.

Two independent complete runs produce byte-identical model archives, memberships, expert strengths, diagnostics and non-runtime reports. Model SHA256: `47848f9577d0c80c2942987534ac961c402dde5bd81a8cf1dc13802d6cf7b620`. Concurrent execution timings are not used for a performance claim.

Sixteen moving and sixteen stationary actual-rig cases pass on the eight existing fixtures with context on/off. Generated actions remain editable, priorities and stationary poses are preserved, and Discard restores original state. Both host processes still crash during shutdown after assertions complete, with exit3221225477; host lifecycle remains unqualified.

The addon and v0.17.4 archive match their previously verified bytes. The 330-case/31-suite runtime regression and four offline package cases are retained evidence, not newly rerun suites. Six fresh confirmation clips remain absent. No downloads, installed changes, Git commits or pushes occurred.

## Next investigation

Use the saved cohort/weight attribution to define the next training-only experiment. Compare the loss's average-error emphasis with the worst-cohort requirement, and measure whether observed expert disagreement or an amplitude-aware loss can identify unreliable proposals. Diagnose raw position and rotation contributions separately before asserting that the gate selected a bad reference: the matched controls carry their own rotations, while the mixture retains learned v20 rotations and shares nonlinear rig projection. Any new candidate must keep these development gates and preserve confirmation ownership.

This mixture does not add multi-priority intent/style learning, partial-body motion editing, full contacts/physics/refinement, broad production humanoid/quadruped coverage or the optional connector. Those original requirements, independent animator assessment, supported-host lifecycle, responsiveness and equivalent Cascadeur comparisons remain. Preserve the same goal ID, 50-evaluation limit and unchanged 15-hour resumed deadline.

Evidence: mixture_trajectory_v21/report.json and mixture_trajectory_v21_repeat/report.json; mixture-trajectory-reproduction-v21.json; mixture-experiment-verification-v21.json; mixture-failure-attribution-v21.json; mixture-training-attribution-v21.json, under training/b4artists_ml/results. The prospective design is MIXTURE-TRAJECTORY-PLAN-v21.md.
