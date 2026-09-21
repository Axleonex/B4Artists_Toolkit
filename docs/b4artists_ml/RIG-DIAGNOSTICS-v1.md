# Rig Mapping Diagnostics v1

Status: implemented on development 0.33 source; not packaged.

## Animator workflow

`Inspect / Refresh Rig Mapping` creates a read-only snapshot for the selected armature or its bound mesh. The panel reports the detected profile, rig family and mapping schema, semantic-role coverage, mapped-control and directly-writable counts, excluded structural-bone categories, passed or blocked workflow preflights, missing roles, adapter warnings, optional semantic role-to-bone mappings, and the state of development 0.33 manual corrections.

The snapshot is produced only when the animator presses the button. Panel redraws decode the saved JSON report and do not repeatedly inspect the rig. Press the button again after changing the rig, constraints, transforms, NLA setup, or control spaces.

Preflight results are based on the same read-only adapter checks used by the corresponding workflow. Humanoid whole-body posing checks active ownership, playback, the writable body mapping, supported transform space, and a nondegenerate 17-joint body frame. Quadruped whole-body posing checks active ownership, playback, the quadruped binding, required native IK mode, and writable controls. Automatic capture checks current preview state, NLA compatibility, mapped animator controls, unlocked channels, and exclusion of generated structural bones. Pose Blending has its own guards for active previews, NLA, a retained motion layer, and at least two valid, compatible anchors; manually selected anchors on an unrecognized rig remain eligible. A passed preflight is current structural and operational evidence; the actual operation retains its final validation and rollback. The probes create no preview session, change no rig mode, write no control, and make no animation edit.

Unknown rigs remain unknown. Their missing semantic roles are listed and the panel does not infer compatibility from names alone. Version-2 saved reports are bounded and cross-checked for exact workflow identities, family/schema relationships, logical counts, role uniqueness, applicability, correction-state consistency, and string/list sizes. Active overrides are listed; invalid/stale correction data blocks dependent preflights and is reported without breaking panel drawing. See `MAPPING-CORRECTIONS-v1.md`.

## Verification

Final focused evidence passes 8/8 tests. It covers:

- BoneForge controls, generated Rigify Default, and an independently authored Unity Humanoid FBX with complete 14-role humanoid mapping and a ready whole-body workflow.
- Generated Rigify Cat with complete 19-role quadruped mapping and its existing whole-body workflow ready.
- Zero and corrupt anchors, manually selected anchors on an unrecognized rig, a retained-motion-result blocker, fully locked controls, active previews, a degenerate recognized body frame, and a nonuniform-scale blocker with actionable text and no inspection mutation.
- An unrecognized rig that reports every missing role without claiming support.
- The Inspect operator, rendered mapping rows, and defensive rejection of wrong types, impossible counts, duplicate roles/workflows, invalid applicability, unknown keys, oversized total payloads, deeply nested JSON, and oversized text.
- Before/after state comparison proving the probes are read-only.

The existing preview lifecycle passes 10/10 tests on the same source, including cancel, save/reload, unregister recovery, source-action preservation, and generated Rigify capture. The base regression passes 33/33. Together the focused and lifecycle suites provide 18 directly affected tests; the base result is reported separately.

The foreground `rig-diagnostics-v7` journey generated Rigify Default, opened the diagnostics snapshot, showed Pose Blending blocked until two compatible anchors exist, confirmed the whole-body preflight, completed the timer-driven solve, restored the previous preview with Escape, and completed Undo/Redo and Keep while restoring source modes. Visual inspection confirms that the expanded panel presents the mapping summary, blocked reason, and passed preflights without obscuring their meaning.

Evidence hashes:

- `training/b4artists_ml/results/rig-diagnostics-v1.json`: `c6382901f50165a39f228fd4299e769facace70999d66d3364ed0f732de54aee`
- `docs/b4artists_ml/body-preview-test-v0.32.0.json`: `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4`
- `docs/b4artists_ml/body-preview-ui-vrig-diagnostics-v7.json`: `69d21aed7808e581b7435166438d8f8c8e80de4169af1754f960d8f3f1a5fc3e`
- `training/b4artists_ml/cache/body-preview-ui-vrig-diagnostics-v7.png`: `54fbb8e75c626446cc14ac3c59e375ee7d6a4e1f53f79a4d6944f08d1b5d5611`

All assertions and evidence reports complete inside Bforartists before the installed Blender 5.2 Alpha host reaches its known `ucrtbase.dll` shutdown fault. This is not a clean-process-exit claim.

## Routing record

The coding assignment declared `b4artists_ml/rig_diagnostics.py`, `b4artists_ml/ui.py`, both affected tests, this document, and the delivery-order ledger. A refined plan separated diagnostics into its own module so panel drawing could consume a cached, validated snapshot. Prime routing was attempted for both plans and returned before lane selection because the configured execution target requires the allowlisted `desktop-prime-ssh` route to `NUCBOX_M6ULTRA`. Consequently `actual_lane`, `actual_lane_reason`, and a per-dispatch policy fingerprint were absent and are not inferred. A later documentation-integration route could not launch its managed Python child. The static native policy's bounded serial fallback was used within the declared project scope, with no parallel workers, no escalation of scope, and no commit, package, or publication action.

Verification commands were the focused diagnostics suite, the 10-test preview lifecycle suite, the 33-test base suite, AST parsing of all changed Python files, and the foreground generated-Rigify-Default journey. All in-process assertions passed. The parent remains the sole integrator and completion authority.

The final Code Evaluator classification selected phase scope at S3 and returned `verdict=PASS` with policy fingerprint `95e923fbec07b91a6667e116f90d86466b6f41252b0d2a111a268010a45bd808`. It remained classification-only because runtime evidence identity and freshness were unverified, so no adaptive reviewer was invoked. Serial semantic review found two rounds of accuracy and validation gaps; the implementation and tests were corrected after each round. The final serial review returned PASS with no actionable blocker or warning.

## Claim boundary

Rig diagnostics improve transparency and actionable compatibility feedback. They are deterministic adapter inspection, not machine learning, learned posing, learned inbetweening, physics, or evidence of Cascadeur parity. Wider production rigs and clean host shutdown remain unverified. Experimental 0.32.0 remains the latest package; no 0.33 archive has been produced.
