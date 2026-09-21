# Fixed sequence-model development comparison

Both tested model families fail the original development requirements. No temporal weights are promoted or bundled. This conclusion applies to these fixed configurations and this corpus; it does not establish that temporal convolution or conditional diffusion is unsuitable in general.

All four runs completed 60 epochs on the same 5,778 canonical windows from 78 training clips, using two seeds per family. All weights and the evaluation protocol were frozen before development data was loaded. The three projected procedural control reports reproduce the original reference exactly on old, new and combined partitions. All six confirmation clips remain unopened.

| Model / seed | Combined position error vs best control | Velocity error ratio | Acceleration error ratio | Worst cohort position ratio |
|---|---:|---:|---:|---:|
| direct-20260909 | 1.150 | 1.127 | 1.156 | 6.770 |
| direct-20260910 | 1.154 | 1.139 | 1.173 | 7.409 |
| diffusion-20260909 | 1.231 | 1.156 | 1.150 | 7.271 |
| diffusion-20260910 | 1.210 | 1.141 | 1.118 | 9.350 |

Ratios below 1 indicate less error. The required position ratio is at most 0.95; velocity/acceleration at most 1.05; each cohort at most 1.10. Every model failed position, velocity, acceleration and cohort gates in both partitions. Endpoint positions/rotations and physical edge lengths passed. Passing those geometric invariants does not establish learned motion quality.

## What the experiment establishes

The new sequence architecture and local NumPy export work technically, but they do not improve development motion. Both seeds tell the same broad story, so selecting a favorable seed is not justified. The calibration correction, known-pose restoration and masked-input checks remain independently testable numerical contracts. Repeatedly exposed development clips remain development data, not a fresh unbiased confirmation set.

The corpus audit measures 1,026.296 seconds (17.1 minutes) of distinct motion. Window overlap, context variants and partial masks enlarge the optimization set but do not create new performances. The full-corpus training losses fell from roughly 0.164-0.173 to 0.075-0.084; a four-window capacity check fit much more closely. These observations are consistent with several causes (coverage, model capacity, conditioning or optimization); this comparison does not isolate a cause. More data is a hypothesis to test, not a demonstrated cure.

## Next ML decision

Pause further nearby fitting variants. Audit training coverage by motion, subject, timing, root trajectory and proportions; verify that training requests match actual authored-pose use. Define contact/intent conditioning and a broader task representation explicitly, since the current research condition contains pose observations, masks, rest shape and timing but no explicit contact or style intent. Any new data/model proposal needs its own rights, storage, compute and split plan before acquisition or fitting. Preserve these development failures and the sealed confirmation clips.

Continue usable host work in parallel with that investigation. Private-rig projection is a measured performance opportunity, independent of model promotion. Learned pose completion, full physics, animator visual assessment and equivalent Cascadeur comparison remain separate incomplete requirements.

Evidence: training/b4artists_ml/results/sequence-development-v1/report.json (SHA-256 21e7a385780abac75336e7f3d9d17c39487701b21135044f5cd154ad88e873f0).

## Training-only follow-up

The coverage audit found 25 normalized rest-shape groups among the 78 clips. Context availability and all three mask patterns are balanced; all five gap lengths are represented. Median distinct clip duration is 7.5 seconds. These counts describe converted training geometry and performances, not proof of deployment coverage.

A frozen diagnostic on all 1,926 boundary-mask training windows compared both direct seeds with their linear/SLERP request baseline. Raw position MSE ratios were 0.160 and 0.151; weighted loss ratios were 0.383 and 0.379. Both models therefore learned a substantial improvement on these training examples. This is not the projected development metric, so the raw-training and projected-development numbers must not be compared as equivalent scores. Generalization, conditioning distribution and projection effects remain possible explanations for failed deployment gates; another fit is not yet justified.

Evidence: sequence-coverage-audit-v1.json and sequence-training-diagnosis-v1/report.json under training/b4artists_ml/results. No new assets, fitting or confirmation access occurred in these follow-ups.
