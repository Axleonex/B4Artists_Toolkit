# Publication latency - experimental 0.19.3

Whole-body Motion now leaves an owned scalar FCurve unchanged when every generated-span key has exactly the same value. A constant linear segment and the previously generated harmonic Bezier segment evaluate to the same constant function, so calculating and publishing those handles adds work without changing the motion. Complete quaternion-component, sample-time, sign, finite-value, editability and source-recovery checks still run before the action is published.

On the preserved default-Rigify reach/hold fixture, 224 of 300 owned curves and 4,704 of 6,300 owned keys were exactly constant. A serial ABBA comparison against the archived 0.19.2 function reduced the median blocking publication update from 413.7 ms to 275.4 ms, a 33.44% reduction. Median full generation changed by -0.24%, which is neutral at this measurement scale.

All 48,944 dense curve samples per comparison matched exactly, all key coordinates matched, and full metadata matched on every nonconstant curve. The 224 constant curves retain their original linear metadata instead of receiving redundant Bezier handles. Source actions, pose, rig modes, anchors and data inventory recovered exactly in every run.

The current source passes 415 native checks across 43 suites. The exact 0.19.3 archive passes 13 offline workflows and 9,813 dense contact checks with outbound networking and process launch denied. Tests complete their assertions before the installed host's known `ucrtbase.dll` shutdown access violation; clean host exit remains unqualified. The package was not installed, committed or pushed.

This evidence covers one headless publication workflow on one machine. It does not establish interactive queue latency, broad hardware performance, animation quality, independent animator usability, learned-motion quality, full physics, quadrupeds or Cascadeur parity. The original goal remains active.

Evidence: `constant-curve-publication-v2/report.json`, `constant-skip-production-full-v1-regression.json`, `constant-curve-package-v1.json`, and `package-test-v0.19.3.json`.
