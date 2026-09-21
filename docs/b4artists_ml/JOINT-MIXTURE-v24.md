# Per-joint mixture result v24

The fixed joint position/rotation mixture is rejected for motion quality. It improves aggregate rotation accuracy but worsens positional quality and increases failed cohorts from seven to eighteen. The earlier v23 candidate is preserved; neither is qualified or bundled. Runtime and ZIP 0.17.4 remain unchanged.

## Unchanged development gates

Every ratio compares against the strongest matched projected linear, Hermite or shape control. Each partition must pass independently.

| Partition | Position gain (>=5%) | Rotation (<=1.02) | Velocity (<=1.05) | Acceleration (<=1.05) | Worst cohort (<=1.10) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| old_validation | -2.820% | 0.955772 | 0.993267 | 1.003078 | 7.864863 | FAIL |
| new_validation | 7.452% | 0.954552 | 0.971369 | 0.998839 | 1.708019 | FAIL |
| combined | 3.752% | 0.948930 | 0.967703 | 0.994733 | 7.864863 | FAIL |

All seven formerly failing v23 cohorts still fail; eleven additional cohorts now fail. Thirty-two cohorts improve numerically and sixty-four worsen. The largest failure remains 28_01/gap32/context1, whose ratio rises from 1.587 to 7.865. These regressions prohibit promotion even though the model wins the combined selection score and aggregate rotation accuracy improves. Selection by an aggregate score is explicitly separate from qualification.

Newly failing cohorts: 28_01/gap8/context1, 28_02/gap16/context1, 08_04/gap8/context1, 122_17/gap8/context1, 118_01/gap8/context1, 122_01/gap8/context1, 13_19/gap8/context1, 13_12/gap32/context1, 138_11/gap16/context1, 122_01/gap16/context1, 138_20/gap16/context1.

## Controlled diagnosis and implementation

Before fitting, two diagnostics held v23 positions fixed and replaced proposed rotations with linear or Hermite rotations before the same physical projection. Both failed qualification. The global Hermite substitution reduced the old worst ratio to 1.514 and the new worst to 1.174, but remained above 1.10. This justified investigation of learned selectivity; it did not prove the cause of the failures or guarantee an improvement.

The new model uses the same 596 observed inputs and 32 hidden units with 119 outputs: separate four-position-expert and three-rotation-expert softmax weights for each of 17 joints. Rotation proposals are converted to valid, hemisphere-aligned unit quaternions and normalized after mixing. Fixed linear-reference mass prevents zero norm. Priority poses remain exact; C1 continuity at hemisphere ambiguity is not guaranteed.

The full 153-channel supervised objective and original derivative weights train both position and rotation selections. Its normalization differs from the earlier 51-channel position-only objective, so absolute losses are not comparable across architectures. Within this experiment, the fixed 40-epoch fit lowers the objective from 0.0561760 to 0.0522756. All 17 position and rotation readouts move away from their zero initialization, and every joint has observation-dependent strengths. This is evidence of learning, not successful generalization.

Training rows retain the same group-excluded parent for both expert trajectories and observed curve features. Both development sets remain exposed development data. The model freezes before evaluating either; the six fresh confirmation clips remain absent. No configuration was retuned.

## Verification and limits

Eighteen pre-fit checks cover explicit loss, all gradients through quaternion normalization, mixed sequence lengths, rotation convention/nondegeneracy, supervised learning, frozen parents, positional bounds, proper rotations, exact priorities, query-density independence, label separation, stationary/masked inputs, serialization and invalid queries. The author source review is recorded separately and is not an independent review or animator assessment.

Two complete runs reproduce identical model bytes, training diagnostics, feature audits, memberships, strengths and all non-runtime reports. Model SHA256: `ab8829d1dab9116ec5c73260f5251569015dd78e42fe1c9093e0fabc4b35d402`. Concurrent runtime measurements are not latency comparisons.

Sixteen moving and sixteen stationary actual-rig cases pass with editable candidates and complete source recovery. Both host processes still exit 3221225477 during shutdown after assertions. Supported-host lifecycle therefore remains failed. Prior 330-case/31-suite runtime and four exact-package offline checks are retained under unchanged source/archive hashes, not rerun.

The next useful diagnosis is a crossed substitution of frozen v23/v24 positions and rotations to separate the contribution of joint position selection from rotation selection before choosing further architecture changes. A projection-aware training objective may warrant investigation, but current evidence does not establish it as the cause or solution. Preserve both models and original thresholds.

All original learned workflow, multi-priority/intent/style/partial-body, physics/refinement, humanoid/quadruped, connector, distribution, responsiveness, independent animator and equivalent Cascadeur requirements remain. No download, installation, commit or push occurred. The same goal ID, 50-total-evaluation cap and resumed 15-hour deadline remain in force.

Evidence: joint_mixture_v24/report.json and its repeat; joint-mixture-reproduction-v24.json; joint-experiment-verification-v24.json; joint-failure-attribution-v24.json; joint-learning-audit-v24.json; joint-source-review-v24.json; fixed-position-rotation-ablation-v24.json. See JOINT-MIXTURE-PLAN-v24.md and the frozen protocol for the prospective design.
