# Frozen-model projection diagnosis

The four sequence models are already worse than the strongest procedural control before geometric projection. Projection slightly reduces their position error. It is not turning an otherwise passing positional predictor into a failing one in this comparison. Weakening physical edge or priority checks is therefore not supported by this evidence.

| Model | Raw position error / best raw control | Projected position error / best projected control |
|---|---:|---:|
| direct-20260909 | 1.161 | 1.150 |
| direct-20260910 | 1.169 | 1.154 |
| diffusion-20260909 | 1.256 | 1.231 |
| diffusion-20260910 | 1.227 | 1.210 |

All 768 original development windows, all four frozen models and all three controls were included. Saved projected arrays were checksum-verified and their partition metrics reproduced exactly. No weights, projection settings, data splits or acceptance gates changed. Raw metrics do not establish physical validity or qualify a runtime backend.

Together with the training-only diagnostic, this shows a learned improvement on training examples and a failure to improve the development examples, rather than a complete failure to learn or a projection-only failure. It does not isolate data coverage, conditioning or model inductive bias as the cause.

The shared encoder already removes initial root orientation: its basis is the initial root rotation relative to rest, applied to the anatomical reference. Adding another initial-heading canonicalization would duplicate existing behavior and is not the next change. The current condition still lacks explicit contact/style intent and physical context. Those must be designed from actual authored workflows, including how gravity/support coordinates are transformed when the initial root is tilted. This is a requirements gap, not a proved explanation for the present position errors.

Next ML work should establish a bounded generalization and conditioning hypothesis before any new fit or data acquisition. Retain the failed configurations and the original sealed confirmation set. Continue the working standalone tool without bundling these unqualified temporal weights.

Evidence: training/b4artists_ml/results/sequence-projection-diagnosis-v1/report.json and its frozen plan, plus rig_observations.py encode(), sequence-coverage-audit-v1.json and sequence-training-diagnosis-v1/report.json.
