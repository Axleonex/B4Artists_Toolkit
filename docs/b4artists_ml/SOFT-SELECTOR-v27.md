# Soft probability readout v27

Experimental and unqualified. The same frozen v26 learned weights use temperature-one probability marginals over position and rotation experts. No refit, new data or production change occurred. Rotations use hemisphere-aligned normalized quaternion blending; it is only locally continuous away from hemisphere boundaries and rejects a near-zero mixture.

Two complete evaluations reproduce identical model, protocol, probabilities and normalized reports. The original gates, projection and matched controls remain unchanged. Confirmation is sealed.

| Development partition | Position ratio to best control | Worst cohort ratio | Original gates |
|---|---:|---:|---|
| Older, 480 windows | 0.945767 | 2.901379 | Fail |
| Newer, 288 windows | 0.919597 | 1.084385 | Pass |
| Combined, 768 windows | 0.929024 | 2.901379 | Fail |

Two of 96 cohorts still fail the unchanged 1.10 limit: 28_01/gap32/context1 and 13_12/gap32/context1. One prior failure clears; no new cohort fails. Both partitions are exposed development data, not fresh confirmation or independent animator assessment.

The matched 1,728 raw endpoint-edit probes reproduce v26 exactly. For edits of size 0.001, maximum position amplification falls from 1626.89 to 91.85 and maximum rotation change from 2.997 to 0.0452 radians. For smaller edits of 0.00001 and 0.0001, maximum position amplification worsens from about 38.9 to 91.8 and 97.9. These probes precede actual-rig projection and do not establish viewport or global stability.

All 72 native cases pass: 16 moving, 16 stationary, 15 action/recovery and 25 cooperative lifecycle cases. They reuse related fixtures and test different paths; they are not 72 independent quality assessments. The host still exits with 3221225477 after passing assertions, matching the separately reproduced host shutdown failure. Nine readout unit tests and 466 training-only geometry probes pass; the latter show a worst training diagnostic ratio of 6.74 and cannot qualify quality.

The full v26 training, all 88,296 projected candidate windows, model and evaluation have also now reproduced exactly. See results/projected-selector-reproduction-v26.json. Neither v26 nor v27 is bundled or promoted. Release 0.17.5, Ghost Tool and Anim Assist are unchanged. Full motion generalization, intent/style/contacts, physics, broader rigs, quadrupeds, connector, responsiveness, human usability and direct Cascadeur comparison remain unfinished.

Evidence lives under training/b4artists_ml/results: soft-selector-verification-v27.json, soft-selector-training-v27.json, soft-selector-edit-stability-v27.json, and the four soft-selector native reports. Current shared assessment transport cannot authenticate observations; prior floors/history remain preserved and formal observations remain unknown.
