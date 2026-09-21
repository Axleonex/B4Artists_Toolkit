# Shipped pose-model reproduction, 0.14.0

The two currently distributed pose models were rebuilt from locally cached, hash-verified inputs in an isolated output directory. Both reproduced the distributed NPZ files byte for byte in experiment shipped-model-reproduction-v3. Their existing observed confirmation checks passed again. This reproduces prior evidence; it is not a new blind evaluation, new weights, or an accepted temporal motion model.

| Artifact | Reproduced SHA-256 |
|---|---|
| limb_prior_v1.npz | 59704e21ce7185697d48a62df60455aefaee8b7580f65496877d6bb39c8f073d |
| context_pose_mlp_v1.npz | 919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96 |

Verified environment: Windows 11 26200, Ryzen 7 5800XT / 16 logical processors, Python 3.14.3, NumPy 2.4.4, linked scipy-openblas 0.3.31.188.0. OPENBLAS_NUM_THREADS and OMP_NUM_THREADS were unset in the passing run. The loaded BLAS library reported 16 threads through its runtime query. The exact compiler/build information is in shipped-model-reproduction-environment-v1.json.

Forced four-thread and one-thread runs did not reproduce the original arrays exactly. Both remain failed strict reproducibility trials (v1 and v2); no tolerance was relaxed. The four-thread limb coefficient differences were at most 3.46e-14; contextual output weights differed by up to 0.000739. Thread settings therefore belong to the training provenance, even when package inference uses an unchanged frozen checksum. The host performance harness's four-thread setting is a separate inference/rig evaluation condition.

Run training/b4artists_ml/reproduce_shipped_models.py from the repository root with the verified Python/NumPy environment and default 16-thread BLAS configuration. B4ML_REPRO_TAG selects a new, unused output label. The driver refuses to overwrite an existing evidence directory, verifies the five required manifests and all 46 referenced local clips (59,173,240 unique raw bytes), copies only those inputs into an isolated workspace, and denies Python networking/process-launch calls. It never downloads missing data or replaces shipped weights.

The original unshipped limb V1 reference model is a checksum-recorded input for the historical confirmation baselines. This run retrains the two shipped models and reevaluates their frozen confirmation protocols; it does not retrain every historical baseline. On this machine, limb training took 6.01 seconds, contextual training 12.79 seconds, and the confirmation stages 0.55 and 0.31 seconds. These are research pipeline timings, not animator latency.

Evidence: training/b4artists_ml/results/shipped-model-reproduction-v3.json; its hash-indexed outputs under cache/shipped-model-reproduction-v3; the environment report; and retained v1/v2 failures. No raw motion files enter the installable package. The historical contextual prior-pose regression and linear-baseline advantage remain unresolved. Independent animator assessment and Cascadeur comparison remain absent.
