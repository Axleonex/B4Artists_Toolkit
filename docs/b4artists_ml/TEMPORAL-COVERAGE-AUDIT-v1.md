# Training-only temporal coverage audit

The cached training partition has31 clips from13 catalog groups,465.865 seconds of motion and1456 unique intervals. The2912 windows duplicate each interval with/without context; window count is not independent motion count. Thirteen normalized rest shapes are represented; catalog groups are not established independent actors.

Coordinate checks passed for every training clip: world position/rotation round trips, normalized feature/label invariance under a proper arbitrary rigid transform and uniform scale, and physical initializer agreement with semantic priority positions. Maximum error was3.56e-14. This does not prove arbitrary rig compatibility or nonuniform-scale support.

| Raw training-position error (body units) | Value |
|---|---:|
| Procedural Hermite |0.173318|
| v16 full-training learned model |0.179071|
| v16 group-excluded learned model |0.210184|
| Label-access four-term C0 oracle |0.020465|
| Label-access four-term C1 oracle |0.017725|

The oracle fits hidden answers and is never available for inference or promotion. It shows substantial headroom within the existing temporal basis. The fitting gap exists even before group transfer; blindly enlarging the basis or merely counting more overlapping windows is not justified. Fold3 has22.4% of excluded windows with at least one feature beyond the training normalization clipping range; this is shift evidence, not a calibrated out-of-distribution threshold.

Next: the prospectively fixed v17 experiment solves the existing network's last layer analytically at three declared regularizations using matching training-only fold hidden features. This tests optimizer/readout underfit without new data or changing old experiments. Generalization, exact physical projection, real-rig behavior and original motion-quality gates remain mandatory. Validation is already exposed research data and must never be described as blind confirmation.

Evidence: training/b4artists_ml/results/temporal-coverage-audit-v1.json. Previous turn classification: progress (exact-package presentation qualification saved). Full goal remains active, round29 until the next recorded evaluation.
