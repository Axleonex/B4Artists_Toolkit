# Curve smoothing latency - experimental 0.19.5

Whole-body Motion now calculates all interior monotone cubic tangents in vectorized NumPy operations. The scalar and vectorized implementations use the same harmonic-mean formula, endpoint rules, validation, and constant-curve handling.

The optimization was first checked across 2,000 randomized numerical cases and six invalid-input cases. The production implementation then passed the complete native suite, including a randomized scalar-reference test, contact constraints, temporal preview, imported humanoids, learned inference, physics refinement, and source recovery.

In a six-run balanced comparison against exact archive 0.19.4, median smoothing time on the preserved default-Rigify reach/hold fixture fell from 108.7 ms to 48.4 ms, a 55.45% reduction. Median total publication time fell from 189.9 ms to 136.9 ms, a 27.92% reduction. All 48,944 dense evaluated curve samples, all keys, handles and metadata matched exactly. Source action, pose, rig modes, anchors and data inventory recovered in every run.

The exact changed runtime passes 418 native checks across 43 suites. The exact 0.19.5 archive passes 13 offline workflows and 9,813 dense contact checks with outbound networking and process launch denied. Tests complete assertions before the installed host's known `ucrtbase.dll` shutdown access violation; clean host exit remains unqualified. The package was not installed, committed or pushed.

This evidence covers one headless publication workflow on one machine. It does not establish interactive queue latency, broad hardware performance, animation quality, independent animator usability, learned-motion quality, full physics, quadrupeds or Cascadeur parity. The original goal remains active.

Evidence: `vectorized-tangents-v1/report.json`, `vectorized-tangent-publication-v1/report.json`, `vectorized-tangent-production-full-v1-regression.json`, `vectorized-tangent-package-v1.json`, and `package-test-v0.19.5.json`.
