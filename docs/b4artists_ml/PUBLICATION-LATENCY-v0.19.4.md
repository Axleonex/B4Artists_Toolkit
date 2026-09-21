# Publication latency - experimental 0.19.4

Whole-body Motion now validates anchor data once at the synchronous publication boundary and reuses that snapshot while creating and smoothing the candidate. Public workflow and smoothing calls still perform their own anchor validation. The internal path contains no timer or user yield, so the snapshot cannot become stale between its consumers.

Private temporal generation now returns its detached, validated sample buffer through a one-use ownership packet. Publication consumes the packet once and still rescans every frame, control, finite value, rotation representation and authored priority against the live source rig before it creates an action. A deliberately corrupted packet was rejected before action mutation, with exact source and inventory recovery.

In a six-run balanced comparison against the archived 0.19.3 implementation, anchor decoding/validation calls fell from three to one. Median publication time on the preserved default-Rigify reach/hold fixture fell from 207.6 ms to 153.3 ms, a 26.17% reduction. All 48,944 dense evaluated curve samples, all keys and all metadata matched exactly. Source action, pose, rig modes, anchors and data inventory recovered in every run.

The exact changed runtime passes 417 native checks across 43 suites. The exact 0.19.4 archive passes 13 offline workflows and 9,813 dense contact checks with outbound networking and process launch denied. Tests complete assertions before the installed host's known `ucrtbase.dll` shutdown access violation; clean host exit remains unqualified. The package was not installed, committed or pushed.

This evidence covers one headless publication workflow on one machine. It does not establish interactive queue latency, broad hardware performance, animation quality, independent animator usability, learned-motion quality, full physics, quadrupeds or Cascadeur parity. The original goal remains active.

Evidence: `anchor-snapshot-publication-v3/report.json`, `packet-production-full-v1-regression.json`, `packet-adversarial-target-v1-regression.json`, `packet-package-v1.json`, and `package-test-v0.19.4.json`.
