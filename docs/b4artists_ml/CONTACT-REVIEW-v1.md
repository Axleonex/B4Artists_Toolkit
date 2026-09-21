# Contact review controls — 0.32 source slice

Status: integrated and source-tested on the experimental 0.31.0 base. The separate cleanup source slice is now integrated in `CLEANUP-v1.md`; neither slice is a packaged 0.32 release.

## Animator workflow

Both Humanoid Animation Contacts and Four-Paw Contacts now show compatible proposed, accepted and rejected counts. The animator can accept or reject every compatible proposal at once, or move cyclically to the previous or next proposed interval. Navigation selects the stored contact and moves the playhead to its exact start, including fractional frames. Each selected proposal exposes its score, provenance and evidence text.

Bulk review changes only compatible `PROPOSED` records. It preserves existing `ACCEPTED` and `REJECTED` records, and it ignores rows from the other rig family. Accepting enables the proposal; rejecting disables it. With no compatible proposal, the operator reports an error without changing contact or animation data.

These controls change review metadata and the review playhead only. They do not write action curves, replace actions, solve contacts or claim learned behavior.

## Evidence

The focused native suite passes three tests covering mixed-state humanoid review, quadruped family filtering, fractional cyclic navigation, empty-proposal failure, source/candidate signatures and operator undo registration. The affected regression passes 30 tests across five suites: the new review suite, humanoid suggestions, quadruped suggestions, humanoid correction and quadruped correction.

The affected aggregate has no failures, errors or skips, one runtime hash set and no current-source hash mismatch. Its SHA-256 is `e2ade4a1a790911d8a2f37b5dfbd0b27de43af6ba5ea6627aa403a7b2e548046`. Compact evidence is in `training/b4artists_ml/results/contact-review-v1-integrated.json`.

The foreground v4 Undo/Redo journey passes on BoneForge humanoid and generated Rigify cat fixtures. Undo restores every review state and enabled flag; Redo restores the family-filtered bulk acceptance. Two humanoid or four quadruped proposals change while the deliberately foreign-family proposal, candidate curves and source curves remain unchanged. The aggregate SHA-256 is `c78e9e6fcd2b8103a87a7a1bb936f5d32a28617c2831518fa6bd04be44ba9efd`; compact evidence is in `training/b4artists_ml/results/contact-review-ui-v4-integrated.json`.

The actual operator declares Blender's `UNDO` option. Because a timer-driven `bpy.ops` call does not synthesize the normal UI transaction boundary, the foreground verifier explicitly pushes the completed operator state before calling the real editor Undo and Redo operations. This verifies the metadata transaction and its serialization through Blender's undo stack; pointer placement and subjective usability remain unverified. Failed v1-v3 harness attempts are preserved in the integrated record.

The installed Bforartists 5.1.0 / Blender 5.2 Alpha host still exits with the independently isolated `ucrtbase.dll` shutdown crash after writing passing results. Clean shutdown is not claimed.

## Review and execution routing

The Code Router was invoked through its configured WSL entry point with exact source/test ownership and semantic assertions. It returned `REMOTE_EXECUTOR_REQUIRED` before lane selection because this desktop routes execution to the NucBox, whose executor cannot access the X: workspace. Consequently `actual_lane` and `actual_lane_reason` are absent and are not inferred.

The active local policy reports owner-authorized production with execution initial 2 / ceiling 8 and reviewer maxima S0=0, S1=1, S2=2, S3=4 and S4=4 through October 11, 2026. Native verification failed closed on both Windows and WSL because the host signing key was unavailable to each process. Policy state, expiry, source and implementation hashes, grant reference and the Codex `workspace` identity otherwise matched. No adaptive workers or reviewers were dispatched.

The deterministic Code Evaluator selected S2 in classification-only mode for the 254-line source/test delta. Serial inspection found no additional defect after the tests passed. Career, temperament and shadow-countercheck overlays remain inactive for this result because their signed authority did not validate.

## Remaining 0.32 work

- Versioning, exact packaging and the complete frozen-source/package regression after the remaining workflow closes.

The copied-candidate cleanup items formerly listed here are integrated and evidenced in `CLEANUP-v1.md`.

Ghost Tool and Anim Assist remain unchanged. No commit, merge, push or package publication occurred.
