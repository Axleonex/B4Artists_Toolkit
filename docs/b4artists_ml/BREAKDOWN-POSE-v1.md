# Breakdown Pose v1

Status: implemented and verified on development source; not packaged.

## Animator workflow

Choose **Pose Blending**, move the playhead strictly between two saved poses, and click **Create Breakdown Pose**. The dialog starts at the playhead's natural interval fraction. Moving **Pose Blend** toward zero favors the prior pose; moving it toward one favors the following pose. Confirming creates a normal editable priority-pose anchor at the current frame without changing either neighboring anchor or the source Action.

Enable **Selected Controls Only** to apply the explicit slider only to selected captured controls. Every unselected control remains at its exact pre-insertion preview pose, including global easing/bias or the destination pose's timing override and transition holds. This makes local corrections possible without an unintended whole-body timing change.

The new anchor begins a new outgoing interval and therefore has no inherited incoming-timing override. The original following pose retains its destination-owned timing record. Endpoint blends are valid: zero creates a held copy of the prior pose and one creates a held copy of the following pose at the new frame.

## Storage and safety boundaries

The operation stores a complete schema-compatible pose anchor with mode-native quaternion, Euler, or axis-angle rotation data. It rejects Whole-body Motion, existing-anchor frames, frames outside adjacent poses, invalid blends, empty selected-control requests, active animation workflows, retained motion layers, NLA, excessive anchor counts, and oversized payloads before source mutation.

The command is native Undo/Redo compatible. Saved files retain the created anchor. Preview and Discard continue to use the existing reversible copied-candidate workflow, and the source Action remains structurally unchanged.

## Verification

- Focused Bforartists tests: 8/8. Coverage includes adjacent-pose lookup, natural fraction, full-body and selected-control insertion, effective global and destination-owned timing preservation, native rotation representations, endpoint holds, atomic rejection, operator execution, and save/reload. Report: `training/b4artists_ml/results/breakdown-pose-v1.json`.
- Affected regression: 170/170 across 22 suites on one frozen 44-file runtime set. Report: `training/b4artists_ml/results/breakdown-pose-affected-v1-regression.json`.
- Foreground Bforartists journey: visible dialog initialized to 30%, 75% full-control insertion at frame 4, native Undo/Redo, exact 7.5 preview, Discard, and bounded source Action recovery passed. Report: `docs/b4artists_ml/breakdown-pose-ui-v1.json`.
- Screenshot: `training/b4artists_ml/cache/breakdown-pose-ui-v1.png`.
- Independent serial review found one timing-preservation blocker. The implementation and tests were corrected, and the final verdict is PASS with no remaining finding.

Every host assertion and evidence write completed. The Bforartists Alpha processes then followed the known `ucrtbase.dll` shutdown-fault path, so clean process exit is not claimed.

## Claim boundary

This is deterministic animator-controlled interpolation assistance. It does not learn poses or timing, infer intent or style, generate physical motion, establish independent animator usability, or satisfy learned-inbetweening and Cascadeur-comparison requirements.
