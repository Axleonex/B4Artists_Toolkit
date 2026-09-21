# Subject-disjoint Temporal Holdout v1

## Status

Complete as a research-only evaluation on 2026-09-13. The frozen gravity-conditioned learner was evaluated on four cached CMU clips from subjects 16 and 35, which are absent from both the original training/validation manifest and the expanded v4 training manifest. The learner failed the preregistered acceptance gates and remains unpromoted. This is not learned-motion acceptance, actual-rig evidence, animator usability evidence, or Cascadeur parity evidence.

## Protocol and provenance

- Protocol: `training/b4artists_ml/holdout_protocol_v1.json`, SHA-256 `b8c3996a3d467d158bdfdad0ab2a1bcec68ab16e76d10bc811b3f338b11670e4`.
- Evaluator: `training/b4artists_ml/evaluate_temporal_holdout_v1.py`, SHA-256 `b23dec020a33c09ddbec0a638e6f210dc2bf461ec2343dc924d40ace6af2bfda`.
- Result: `training/b4artists_ml/results/temporal-holdout-v1.json`, SHA-256 `465711b827620d7d7ac8b02e54cd33a08c8ffaf7b08c38c782212f66b6e044fc`.
- Source manifest: `data_manifest.json`, SHA-256 `467ebc675ff29a32e34ce0798e7caaab80e6680ad9a64b33d640d43213b8b190`.
- Model-training manifest: `results/training_manifest_v4.json`, SHA-256 `9973a7f2b8935c33cb8d9b819d46658485bab931fdaabb59b6434ff0e3d78fe8`.
- Selected model receipt requires validation-only selection and `observed_development_loaded: false`; the receipt excludes all four holdout clips from its validation and observed-development cohorts.
- The already-frozen V3 `motion_relative_kernel.npz` candidate is included as a secondary comparison; it was not retrained or selected using this holdout.
- No new raw motion, package, dependency, paid compute, model promotion, or runtime change was used.

The holdout contains `16_01`, `16_17`, `35_01`, and `35_17` from the frozen source `test` partition. Subject 13's `13_20` test clip is intentionally excluded because subject 13 appears in earlier training and confirmation material. The evaluator creates an in-memory derived holdout manifest and never rewrites the source manifest.

## Evaluation

The frozen v4 selected gravity-direction model was compared with the retained v3 kernel control and deterministic baselines across 192 windows and 3,776 query frames at 30 fps, using gaps 8, 16 and 32 with context on and off.

| Metric | Selected learner | v3 control | Learner/control ratio | Gate |
|---|---:|---:|---:|---|
| Position | 0.1616576094 | 0.1610876200 | 1.0725448540 | Fail; position must improve by 5% |
| Rotation | 0.1739879711 | 0.1748186160 | 1.0184956407 | Pass; maximum 1.02 |
| Velocity | 1.1867984977 | 1.1794033784 | 1.0775490416 | Fail; maximum 1.05 |
| Acceleration | 18.1971733187 | 18.1250185656 | 1.0512646461 | Fail; maximum 1.05 |
| True edge length | 3.3845e-16 | 3.3714e-16 | — | Pass |

The maximum cohort position ratio is `4.9105749884`, so the cohort gate also fails. Endpoint position (`3.6637359813e-15`) and endpoint rotation (`1.2212453271e-15`) remain within their gates. Total evaluation time was 2.6717604 seconds on Python 3.14.3 / NumPy 2.4.4 with four OpenBLAS threads.

The retained V3 motion-relative candidate reaches position `0.1607876697`, slightly below the v3 raw control, but its velocity is `1.1978188077` and acceleration is `18.3852222362`; it therefore does not repair the temporal quality failure. It remains a research comparison, not an accepted model.

## Decision and next work

The result is `COMPLETE_GATES_FAILED`. The learner is not accepted, not packaged, and not connected to the B4Artists runtime. The evidence confirms that the prior validation improvement did not survive a subject-disjoint holdout: position is 7.25% worse than the frozen v3 control, with additional velocity, acceleration and cohort failures.

Next learned-motion work must address the documented data/support and root-context gaps with a new preregistered experiment. It must retain the holdout as locked evidence, keep model selection separate from it, and still require actual BoneForge/Rigify control-rig application, cancellation/recovery, editable output, independent animator review and the matched Cascadeur protocol before any learned or parity claim.
