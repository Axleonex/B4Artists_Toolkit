# Temporal Root-Context Candidate v1

## Status

Complete as a controlled research experiment on 2026-09-13. The candidate combines the existing motion-relative/root-context representation with explicit gravity direction. It was selected only on the frozen validation split and then evaluated once on the locked subject-disjoint holdout. It failed the acceptance gates and was not promoted, packaged, or connected to the B4Artists runtime.

## Provenance

- Protocol: `training/b4artists_ml/root_context_protocol_v1.json`, SHA-256 `219437b0b156e48d8937a68129477d88929175f53953d5812cd5bc3e1ac0f2c7`.
- Feature/model implementation: `training/b4artists_ml/root_context_model.py`, SHA-256 `c0cd1d8f4e912fb4b0ea43c5d983ee7f886310d30058a283d7c930a618e43062`.
- Validation trainer: `training/b4artists_ml/train_root_context_motion_v1.py`, SHA-256 `4a6c417408a0a7cc13a266c5c2be4565fd51e61f8cbf835720ad303b2bc07c24`.
- Holdout evaluator: `training/b4artists_ml/evaluate_root_context_holdout_v1.py`, SHA-256 `46cfe04f91bf93a8e512c442be5aebe271f381827cdbbbe0b1c964e7330d7f39`.
- Holdout receipt: `training/b4artists_ml/results/root-context-holdout-v1.json`, SHA-256 `30ed60a9f6719e89fa73b10a01f90455afd5a840102ecdac7796d46cf52b12c5`.
- Selected candidate: `motion_relative_gravity_2.0`, SHA-256 `82ed53d7e47af5f1b7a493b5b1c94ab110b8a8b190eb01a8bd1217f218a1cec7`.
- Selection receipt records `selection_split: validation`, `observed_development_loaded: false`, and the locked holdout protocol hash.

The experiment used the existing cached motion and four preregistered gravity-feature weights. No new data, dependencies, paid compute, runtime model, or package was introduced.

## Results

The selected candidate was compared on the locked subject-16/35 holdout across 192 windows and 3,776 query frames.

| Metric | Root-context candidate | v3 control | Candidate/control ratio | Gate |
|---|---:|---:|---:|---|
| Position | 0.1608291085 | 0.1610876200 | 1.0670480241 | Fail; position must improve by 5% |
| Rotation | 0.1716022787 | 0.1748186160 | 1.0045302075 | Pass; maximum 1.02 |
| Velocity | 1.1999832151 | 1.1794033784 | 1.0895200541 | Fail; maximum 1.05 |
| Acceleration | 18.4125914910 | 18.1250185656 | 1.0637095189 | Fail; maximum 1.05 |
| True edge length | 3.3785e-16 | 3.3714e-16 | — | Pass |

The maximum cohort position ratio is `4.8949091630`; the cohort gate fails. Endpoint position (`3.6637359813e-15`), endpoint rotation (`1.2212453271e-15`) and structural edge preservation remain within their gates. The holdout process took 3.1589456 seconds on Python 3.14.3 / NumPy 2.4.4 with four OpenBLAS threads.

The candidate's position is only 0.16% better than the v3 control and its temporal derivative errors are worse. The earlier motion-relative-only candidate remains slightly better on position (`0.1607876697`) but has the same derivative and cohort failure pattern. Neither candidate is acceptable learned temporal motion.

## Decision boundary

The result is `COMPLETE_GATES_FAILED`. The candidate remains research-only; no model is bundled, no learned influence is exposed, and no claim is made about actual BoneForge/Rigify control-rig output, animator usability, production generalization, or Cascadeur parity.

The next learned experiment must address the persistent root-path and derivative/cohort failures through a preregistered data/support or representation change while retaining both the subject-disjoint holdout and the existing validation-only selection boundary. Actual-rig learned preview integration remains downstream of a model that passes these gates.
