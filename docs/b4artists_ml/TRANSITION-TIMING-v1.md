# Per-Transition Timing v1

Status: implemented and verified on development source; not packaged.

## Animator workflow

Choose **Pose Blending**. Every saved pose after the first now has a **Timing** button. Open it to enable **Override Global Timing**, choose Uniform, Ease In / Out, Ease In, or Ease Out, and set a signed Breakdown Bias. The destination pose owns the override: editing frame 11 changes only the transition arriving at frame 11. Intervals without an override continue to use the global Timing and Breakdown Bias controls.

The first saved pose has no incoming transition and therefore has no Timing button. Recapturing a destination pose preserves its timing override. Reusing that pose at another frame transfers the pose only and starts the new interval with global timing. Per-transition controls are hidden for Whole-body Motion because projected samples own their timing.

## Storage and preview boundaries

An optional `incoming_timing` record is serialized inside the destination anchor payload. Saved values are bounded and validated before anchor or candidate mutation. Invalid, oversized, deeply nested, ambiguous, first-anchor, active-workflow, NLA, and kept-motion states fail without editing the source Action. A deterministic candidate records every interval's effective easing, bias, destination frame, and override state in `b4ml_transition_timing` metadata.

Projected samples reject active per-transition overrides. A saved `incoming_timing: null` is neutral and does not block projection. Projected candidates remove inherited global and per-transition deterministic timing metadata.

## Verification

- Focused Bforartists tests: 9/9. They cover independent multi-interval timing, global fallback, authored endpoints, candidate metadata, invalid and corrupt data, bounded hostile UI/recapture decoding, neutral null records, recapture/reuse ownership, active-workflow and projection rejection, source recovery, operator execution, and save/reload. Report: `training/b4artists_ml/results/transition-timing-v1.json`.
- Affected regression: 152/152 across 20 suites on one frozen 44-file runtime set. Report: `training/b4artists_ml/results/transition-timing-affected-v1-regression.json`.
- Foreground Bforartists journey: visible `Timing*` state, native Undo/Redo, destination-owned midpoint behavior, Discard, and bounded source Action structure recovery passed. Report: `docs/b4artists_ml/transition-timing-ui-v1.json`.
- Screenshot: `training/b4artists_ml/cache/transition-timing-ui-v1.png`.

Every host assertion and evidence write completed. The Bforartists Alpha processes then followed the known `ucrtbase.dll` shutdown-fault path, so clean process exit is not claimed.

## Claim boundary

This is deterministic animator-authored timing assistance. It does not learn timing, infer motion intent or style, modify priority-pose frames, establish independent usability, or satisfy the learned-inbetweening and Cascadeur-comparison requirements.
