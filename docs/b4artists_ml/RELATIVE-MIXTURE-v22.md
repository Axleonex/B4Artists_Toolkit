# Relative loss result v22

The fixed loss change reduces the number of failed cohorts but worsens the largest old-set failure. It is not an overall improvement and remains unqualified research. No temporal weights are bundled; the v0.17.4 addon and archive are unchanged.

## Unchanged gates

All ratios compare against the strongest matched projected linear, Hermite or shape control. Old, newer and combined exposed development partitions must pass independently. No threshold or sample changed.

| Partition | Position gain (>=5%) | Rotation (<=1.02) | Velocity (<=1.05) | Acceleration (<=1.05) | Worst cohort (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | 6.517% | 0.983823 | 0.944581 | 1.005809 | 2.450525 | FAIL |
| new_validation | 7.678% | 0.981352 | 0.970910 | 1.003779 | 1.212321 | FAIL |
| combined | 7.259% | 0.975996 | 0.952403 | 0.999063 | 2.450525 | FAIL |

Eight of96cohorts fail versus11in v21. Fifty-four improve and42worsen numerically; no previously passing v21cohort newly fails. However, 28_01/gap32/context1 worsens from1.712to2.451times the best procedural control. The newer-set worst improves from1.372to1.212. The lower failure count does not excuse the worsened maximum; v22 does not replace v21 as an overall stronger candidate, and neither qualifies for release.

## Diagnosis and isolated change

The training audit measures all466cohorts from7358windows. The largest quarter contributes79.91% of v21's position/derivative loss; the largest tenth contributes58.07%. Its unregularized objective reconstructs exactly from the independent diagnostic, at0.03116607015201659.

Three full-development ablations retain v20 learned rotations while using procedural linear, Hermite or shape positions. None meets the existing gates. Their combined position ratios are1.1342,1.0541and0.9961; v21's is0.9238. Thus learned rotations alone do not explain v21's average gain. These are diagnostic learned/procedural combinations, not new pure-procedural controls or independent validation. Nonlinear projection and differing positions prevent a simple causal interpretation of mean expert strengths.

The sole fit change allocates half of loss-weight mass equally across training cohorts and half by inverse best procedural position MSE. The error floor is1% of the median positive training error:0.00005523679827621952. Each cohort's mass is divided equally among its windows. An independent formula matches every recorded mass and error estimate. The network, original feature normalization, initialization, optimizer, parent models and inference functions remain unchanged. Error scales are training labels and never enter inference.

## Verification and limits

Nine pre-fit weighting tests pass, including exact reproduction of every original v21 fitted parameter when relative strength is zero. The14 original predictor checks remain pinned, and the inference functions are identical objects. The fit source audit isolates the change to training weights and their diagnostic record.

Two independent complete runs reproduce the model, relative weights, parent memberships, expert strengths, all training diagnostics and every non-runtime evaluation field exactly. Model SHA256:`1c3e937a12e5089508a0edbc95eb4e43d45679e7313e095a37e9e795c896ec38`. No earlier epoch, alternative fraction, floor or model was selected after seeing development results. Timings from concurrent runs are not performance comparisons.

Sixteen moving and16stationary real-rig cases pass, preserving priorities, editable generated actions and source recovery. Both host processes still crash during shutdown after assertions, exit3221225477. No UI or independent visual assessment is claimed. Runtime and package bytes match v0.17.4; prior330-case/31-suite and four offline package checks are retained evidence, not rerun suites.

Six fresh confirmation clips remain absent. There were no downloads, installs, commits or pushes. The full original goal remains active, with the same endpoint, regression floors,50total evaluations and15-hour resumed deadline.

## Next work

Loss balancing alone does not recognize the dangerous long-gap proposals. Before another fixed model, investigate observed-only descriptors of expert disagreement, curve excursion, acceleration and geometry. Generate any parent-dependent training features with the same group-excluded parent models; using the full parent on its own training rows would leak fitting information into those features. Keep v21 and v22 frozen and all confirmation clips sealed. Preserve every original learned workflow, multi-priority/intent/style/partial-body, physics/refinement, humanoid/quadruped, optional connector, distribution, responsiveness, supported-host, independent animator and equivalent Cascadeur requirement.

Evidence is under training/b4artists_ml/results: relative_mixture_v22/report.json, its independent repeat, relative-mixture-reproduction-v22.json, relative-experiment-verification-v22.json, relative-failure-attribution-v22.json, relative-training-audit-v22.json, relative-inference-audit-v22.json, mixture-training-diagnosis-v22.json and mixture-rotation-ablation-v22.json. The prospective configuration is RELATIVE-MIXTURE-PLAN-v22.md.
