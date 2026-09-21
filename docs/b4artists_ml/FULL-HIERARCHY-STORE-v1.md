# Full-hierarchy train store v1

Status: structural and access contracts pass. This is train-only research infrastructure, not a promoted learned runtime or product-quality claim.

## Result

The store encodes all 1,840 already acquired CMU training clips from 85 subjects: 773,836 sampled frames and 7.158742 source hours. It retains the 23-joint ancestor hierarchy required to reconstruct the 17 rig-neutral semantic controls.

The Git-ignored 294,845,968-byte cache contains:

- Source-space root translation.
- Sign-continuous local WXYZ quaternions for all 23 retained joints.
- Per-clip normalized offsets and source scale.
- Rest reference axes and rest pelvis orientation.

Linear and angular velocities are derived from stored consecutive frames and the exact clip interval when a window is requested. Sparse authored masks are also generated per window. Only the 17 semantic joints can be marked as animator-authored; the six retained helper joints remain latent. This avoids another dynamic copy of velocities and masks while preserving deterministic training inputs.

Weak motion tags are carried from descriptions and existing style tags for future auditing. They are explicitly not intent ground truth.

## Whole-corpus build checks

Every source file was SHA-256 reverified before decoding. Every frame was reconstructed from the stored float32 root/local representation through forward kinematics:

| Check | Maximum error |
|---|---:|
| Semantic position | `8.19e-7` normalized units |
| Semantic rotation matrix | `1.88e-7` |
| True retained edge length | `8.79e-8` normalized units |

All 23-joint quaternion streams are sign-continuous. The minimum adjacent quaternion dot product is positive (`4.30e-5`).

## Access contracts

Representative 32-frame windows from all 85 subjects pass memory-map, normalization, velocity, authored-mask, and semantic round-trip checks:

| Check | Result |
|---|---:|
| Representative subject windows | 85/85 |
| Semantic position round trip | `5.14e-7` maximum error |
| Semantic rotation round trip | `1.63e-7` maximum error |
| Translation/scale invariance | `3.56e-15` maximum error |
| Quaternion-sign velocity invariance | exact |
| Helper joints marked authored | 0 |
| Invalid-input cases rejected | 6/6 |

Evidence is stored in `training/b4artists_ml/results/full-hierarchy-store-v1/report.json` and `training/b4artists_ml/results/full-hierarchy-store-contract-v1/report.json`. The reports embed hashes for the plan, code, layouts, and numeric files.

## Boundary

No development or confirmation motion was read. No data was downloaded, no model was fitted, and runtime 0.19.5 was not changed. The cache is not bundled with the add-on.

The next gate is a versioned contact, support/scene, intent/style, and sparse-control schema with frozen task cohorts. Another learned fit remains prohibited until those inputs and their ablations are declared prospectively.
