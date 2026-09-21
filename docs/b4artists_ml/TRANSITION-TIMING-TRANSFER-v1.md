# Transition Timing Transfer v1

Status: implemented and verified on development source; not packaged.

## Animator workflow

In **Pose Blending**, each saved destination pose after the first now shows Copy and Paste timing buttons beside **Timing**. Copy stores that interval's easing, Breakdown Bias, Departure Hold, and Arrival Hold in a small rig-local clipboard. Paste applies the stored values as an explicit override for the chosen destination interval.

If the copied interval already owns an override, the clipboard records it exactly. If it uses global timing, Copy snapshots the current global easing and bias with zero holds. Later global edits therefore do not change the copied result. The clipboard survives save/reload on that armature and can be overwritten by another Copy.

Paste changes only the target destination's `incoming_timing` record. It does not change the source interval, the captured poses, frames, other anchors, rig pose, or source Action. Native Undo removes the paste and Redo restores it.

## Validation boundaries

Copy and Paste require Pose Blending, at least two valid anchors, a destination after the first, an idle workflow, no retained motion layer, and no NLA. Frames, payloads, clipboard schema, source provenance, easing, bias, and normalized holds are validated before mutation. Empty, corrupt, recursive, oversized, non-finite, missing, ambiguous, first-anchor, and Whole-body Motion requests fail closed.

The clipboard is intentionally local to one armature. Cross-rig timing libraries and whole-interval pose copying remain separate future workflows.

## Verification

- Focused Bforartists tests: 6/6. Coverage includes exact override transfer, stable global snapshots, destination-only replacement, hostile clipboard/frame rejection, Whole-body and active-workflow guards, operator execution, source preservation, and save/reload. Report: `training/b4artists_ml/results/transition-timing-transfer-v1.json`.
- Affected regression: 176/176 across 23 suites on one frozen 44-file runtime set. Report: `training/b4artists_ml/results/transition-timing-transfer-affected-v1-regression.json`.
- Foreground Bforartists journey: visible enabled Copy/Paste controls, frame 11 to frame 21 transfer, native Undo/Redo, identical interval metadata and preview timing, and bounded source Action recovery passed. Report: `docs/b4artists_ml/transition-timing-transfer-ui-v1.json`.
- Screenshot: `training/b4artists_ml/cache/transition-timing-transfer-ui-v1.png`.
- Independent serial review found one Whole-body backend-guard blocker. It was fixed and the final verdict is PASS with no remaining finding.

Every host assertion and evidence write completed. The Bforartists Alpha processes then followed the known `ucrtbase.dll` shutdown-fault path, so clean process exit is not claimed.

## Claim boundary

This is deterministic animator-authored timing reuse. It does not copy pose intervals, learn timing, infer intent or style, generate physical motion, establish independent usability, or satisfy learned-inbetweening and Cascadeur-comparison requirements.
