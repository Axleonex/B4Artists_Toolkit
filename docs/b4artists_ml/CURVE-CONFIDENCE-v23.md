# Curve descriptor result v23

The additional curve descriptors reduce difficult-case failures, but the candidate remains unqualified. No temporal weights are bundled. The v0.17.4 runtime and installable archive are unchanged.

## Unchanged quality gates

Every ratio uses the strongest matched projected linear, Hermite or shape control. Old, newer and combined exposed development sets must pass independently.

| Partition | Position gain (>=5%) | Rotation (<=1.02) | Velocity (<=1.05) | Acceleration (<=1.05) | Worst cohort (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | 7.733% | 0.983840 | 0.940870 | 1.007666 | 1.586986 | FAIL |
| new_validation | 7.351% | 0.980246 | 0.971100 | 1.004818 | 1.206508 | FAIL |
| combined | 7.489% | 0.975287 | 0.951390 | 1.000313 | 1.586986 | FAIL |

Seven of 96 cohorts fail, compared with eleven for v21, the prospectively chosen equal-cohort reference. Sixty-two improve and 34 worsen numerically; no previously passing v21 cohort newly fails. The worst ratios improve from 1.712/1.372 to 1.587/1.207. Average position improves on the old set and worsens slightly on the newer set. Neither the lower failure count nor average gains override the failed worst-case limits.

The comparison with v22 is also retained: seven failures versus eight, with 118_01/gap32/context1 newly failing, while 13_12/gap32/context1 and 118_01/gap8/context1 newly pass. This is not a claim that every previous experimental result improved.

## Implementation and verification

The model appends 48 observed-proposal descriptors to the original 548 inputs and retains 32 hidden units, four position-mixture weights, the original equal-cohort loss and the frozen v20 parent. The added input rows introduce 1,536 weights. Descriptor construction uses nine fixed query times and reads no hidden frames or target labels. Each training row uses its group-excluded parent for both the proposed motion and the added features. All 7,358 rows have finite features; descriptor values range from 0 to about 1.997.

Eighteen pre-fit checks pass, including explicit trajectory loss, finite-difference gradients, supervised feature learning, input preservation, scale/translation invariance, proposal sensitivity, masked context, stationary behavior, exact priorities, label separation and serialization. A separate rotation-invariance and zero-extension check passes on four synthetic windows: padding the established gate with zero feature weights reproduces its predictions exactly in those fixtures. This does not claim that separately trained models are identical.

Two independent complete runs produce identical model bytes, feature audits, memberships, expert strengths and non-runtime reports. Model SHA256: `dd6ff0959f058e48b5a5bdc834d5513d1f7921bee7889ea5b15852474f9f39a8`. No configuration was retuned after development evaluation. Concurrent timings are not performance comparisons.

Sixteen moving and sixteen stationary actual-rig cases pass with editable actions and source recovery. Both host processes still crash during shutdown after their assertions, exit 3221225477. This remains an unresolved host failure. Prior 330-case/31-suite runtime coverage and four offline package cases are retained under unchanged source/archive hashes, not rerun.

## Remaining work

A cross-reference of the seven failures shows that all three diagnostic procedural-position choices with fixed learned rotations fail on 28_01/gap32/context1 and 28_02/gap8/context1. This does not prove that every positional mixture must fail: mixtures and nonlinear projection can outperform their individual components. The next controlled diagnostic should hold v23 positions fixed and change rotation proposals to measure their contribution before choosing another architecture.

Six fresh confirmation clips remain absent. No downloads, installs, commits or pushes occurred. The original full learned workflow, multi-priority/intent/style/partial-body editing, physics/refinement, humanoid/quadruped coverage, optional connector, distribution, responsiveness, supported-host lifecycle, independent animator and equivalent Cascadeur requirements remain. Preserve the same goal ID, 50 total evaluations and unchanged 15-hour resumed deadline.

Evidence is under training/b4artists_ml/results: curve_mixture_v23/report.json and its repeat; curve-mixture-reproduction-v23.json; curve-experiment-verification-v23.json; curve-failure-attribution-v23.json; curve-compatibility-v23.json; curve-rotation-crosscheck-v23.json; and curve-v22-comparison-v23.json. See CURVE-CONFIDENCE-PLAN-v23.md for the prospective design.
