# Training tail-risk selector v28

Unqualified research candidate. The single prospective variant retains v27 soft blending, the frozen v20 trajectory parent, v26 feature normalization and 32-hidden selector architecture. It warm-starts v26 and performs 200 full-batch Adam steps. Training penalizes cohort mean position risk above 1.0 and rotation risk above 1.02, after normalizing each metric separately to its best complete procedural training control. It uses only the same 7,358 training windows and immutable projected expert labels. Original development gates are unchanged.

Seven numerical/grouping checks pass, including central-difference gradients, cohort mass, row permutation, normalization, invalid input and exact readout identity. Two independent complete training/evaluation runs produce identical weights, normalizers, probabilities, protocols and normalized reports. Model SHA-256: 64d947f7b7d5dffc750de45a417cb630a7cfae6b27b562b50e1590941131e19c.

| Development partition | Position ratio to best control | Worst cohort ratio | Original gates |
|---|---:|---:|---|
| Older, 480 windows | 0.947809 | 2.911539 | Fail |
| Newer, 288 windows | 0.924231 | 1.268680 | Fail |
| Combined, 768 windows | 0.932724 | 2.911539 | Fail |

Three of 96 groups fail the unchanged 1.10 limit. The two prior failures persist: 28_01/gap32/context1 (2.911539) and 13_12/gap32/context1 (1.342766). A new failure appears at 138_01/gap8/context1 (1.268680). Average position remains more than 5% better than the best original control, but worst-group performance rejects the candidate. No thresholds were relaxed, no development labels used in fitting, and no confirmation data opened.

The expected training objective improves from 1.081449 to 1.069738. Its maximum training cohort position risk improves from 1.414516 to 1.082576. This measures a probability-weighted cost of separately projected experts, not the actual projected blended trajectory. The separate matched 466-window training diagnostic still fails its worst-group check (6.849881); that diagnostic samples one window per cohort, so its maxima are not directly comparable to the full-cohort training objective. Recomputed features and hard proposal labels match exactly, and endpoints/physical geometry pass. The result does not establish a single cause for the remaining failures.

Across the same 1,728 raw endpoint-edit probes, maximum position amplification is 31.83, 31.88 and 30.65 for edits of 0.00001, 0.0001 and 0.001. These maxima improve over v27 (91.79, 97.91, 91.85), but the corresponding p95 values (8.115, 8.099, 7.989) do not improve. Maximum rotation change at edit 0.001 falls to 0.02842 radians. This is finite raw-proposal testing, not a proof of global continuity, actual-rig edit stability or viewport usability.

All 72 native cases pass their assertions: 16 moving, 16 stationary, 15 action/recovery and 25 cooperative lifecycle cases. The native host still exits with code 3221225477 after the assertions, consistent with the independently reproduced host shutdown issue. Related fixtures and test-local provider substitution limit these results; no learned temporal UI is accepted or bundled.

The required code-review entry point remains unavailable (uv cannot spawn its Python child). Author inspection and numerical tests are recorded, not misrepresented as independent review. Canonical assessment envelopes remain unavailable; formal observations stay unknown and historical floors remain intact.

Release 0.17.5, bundled pose models, Ghost Tool and Anim Assist are unchanged. No installation, publication, data acquisition, paid service or production promotion occurred. Full generalization, intent/style/contacts, physics/refinement, broader rigs/quadrupeds, connector, responsiveness, independent animator assessment and equivalent Cascadeur comparison remain unfinished.

Evidence: training/b4artists_ml/results/tail-risk-selector-verification-v28.json, tail-risk-selector-training-v28.json, tail-risk-selector-edit-stability-v28.json, the four native reports, and tail_risk_selector_v28/report.json. All rejected variants remain preserved for diagnosis and reproduction.
