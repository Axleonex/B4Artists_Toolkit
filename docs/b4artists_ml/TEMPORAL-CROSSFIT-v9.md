# Cross-fitted temporal controller v9

Status: selected research candidate; full quality acceptance FAIL. No new model
is bundled in v0.14.2 and no actual-rig temporal integration is claimed.

## Implementation and experimental controls

The frozen protocol is training/b4artists_ml/crossfit_controller_protocol_v9.json.
The existing 31 training clips produce 2912 windows; ten validation clips produce
480 windows. Original split ownership and content hashes are unchanged. No data
is downloaded. Four temporary base models hold out entire CMU catalog subject
prefix groups, including every clip and overlapping window in that group.
Catalog labels do not establish independent actor identity. The fold audit records
all fit/held groups, clips, counts, and exact prediction hashes.

For each training window, a constrained least-squares target chooses a convex
blend of fixed-offset FK linear, learned-base, and contextual trajectories.
Four learned strengths separately control root and articulated rotations. The
controller trains on the group-excluded predictions. The deployed companion is
still V8's base model trained on all and only training clips. This is actual
supervised kernel learning. The contextual and linear components remain explicitly
procedural. Missing-context windows are included, so learned corrections can be
suppressed without requiring surrounding keys.

Eighteen prespecified candidates cover two observation feature schemas, three
kernel widths and three regularization values. compact_1.0_0.1 wins the frozen
validation objective and retains the prior validation position/rotation guard.
V8 confirmation is already observed; it is assessed after selection only as a
diagnostic, never called fresh or used to choose this candidate.

Both cross-fitting and blend parameterization changed relative to V8. The
experiment does not isolate their individual contribution to the improvement.

## Measured results

Errors use the existing normalized motion representation and equal-cohort metric.
They are not world meters, animator ratings or Cascadeur comparison scores.

| Evaluation | V8 position error | V9 position error | Reduction versus V8 |
|---|---:|---:|---:|
| Validation | 0.082383046 | 0.079585072 | 3.40% |
| Previously observed V8 confirmation | 0.311489933 | 0.296487095 | 4.82% |

Validation position ratio to the strongest frozen aggregate baseline is
0.856727; rotation, velocity,
acceleration, exact priorities and true source-edge length gates also pass.
The worst validation cohort ratio remains 1.605239
versus a maximum allowed 1.1. The previously observed confirmation aggregate
position ratio is 1.014848
and its worst cohort ratio is 1.820787.
Both complete acceptance results remain FAIL.

The largest validation miss is 13_19/gap16/context1; the largest observed
confirmation miss is 143_02/gap32/context1. Their contextual baselines outperform
the selected blend. These findings point toward insufficient context trust or
motion coverage, but do not prove the cause. A follow-up can test an explicitly
frozen contextual fallback prior while retaining all quality gates and split rules.

## Verification and limits

Eight focused tests pass in desktop Python and actual Bforartists NumPy. They
check complete group exclusion, convex targets, finite/bounded coefficients,
missing-context behavior, exact endpoints, model roundtrip and hidden-label
isolation. Two full training processes reproduce the selected weights, fold
prediction hashes, candidate metrics and all validation/diagnostic results exactly.
The reproduction record is crossfit-reproduction-v9.json.

Selected gate SHA256: `f9a9a442231ddc8b2cd0f345a93f2ecabc5ab987633481efbbb621ef9d8d3faf`.
Required V8 base SHA256: `857b6f005e519bac94a437a7da9648453c5e122d2849e5e58c6690fee7143611`.

Actual-host source-hierarchy inference measured load 82.19 ms,
first query 12.52 ms, and warm p95 11.54 ms
for 33 poses in one motion window. This excludes rig fitting, meshes, UI, full
memory/resource budgets and human assessment. Host shutdown again returns
3221225477; lifecycle acceptance stays failed.

The previous real-rig observation adapter uses a different rest-calibrated
17-semantic schema. Its sampled-pose reconstruction does not establish compatibility
with this 23-joint model. A verified conversion or separately qualified model is
still needed before animator-facing temporal integration. Production/imported
rigs, quadrupeds, momentum/secondary motion, independent usability, equivalent
Cascadeur comparisons and optional connector work remain unfinished.
