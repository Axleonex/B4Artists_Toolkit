# Transition Window v1

Status: implemented and verified on development source; not packaged.

## Animator workflow

Choose **Pose Blending**, then open **Timing** beside any saved destination pose. **Departure Hold** keeps the departing pose unchanged for the chosen fraction of that interval. **Arrival Hold** reaches the destination early and keeps it unchanged through the remainder. The active motion between those holds uses the same destination-owned easing and Breakdown Bias controls already exposed by Per-Transition Timing.

Both holds are normalized to the current interval, so moving an anchor changes their frame duration without changing their saved proportion. Their sum may not exceed 90%, leaving at least 10% of the interval for motion. Authored endpoint poses and frame numbers remain exact. Intervals without an override keep the full motion window and global timing.

The first saved pose has no incoming transition. Removing the first pose clears timing from the new first pose. Files created before this correction can contain a dormant first-pose record; inserting an earlier captured or reused pose strips that record before it can silently become active. Recapture keeps valid destination timing, while pose reuse copies only pose data.

## Storage and preview boundaries

`departure_hold` and `arrival_hold` extend the optional destination-owned `incoming_timing` record. Older two-field easing/bias records remain readable and upgrade to zero holds on recapture. Values are finite, bounded, and validated before mutation. Invalid or oversized data, ambiguous anchors, active workflows, NLA, retained motion, and projected Whole-body Motion fail without editing the source Action.

The deterministic candidate stores the effective holds with each interval in `b4ml_transition_timing`. Per-transition controls remain hidden for Whole-body Motion because its projected samples own their timing.

## Verification

- Focused Bforartists tests: 10/10. Coverage includes monotonic windows, exact endpoints, independent intervals, global fallback, timing composition, invalid values, float-property boundary tolerance, source preservation, operator execution, save/reload, two-field record upgrade, removal normalization, persisted dormant records, exact frame-tolerance handling, capture/reuse ownership, and projection rejection. Report: `training/b4artists_ml/results/transition-window-v1.json`.
- Affected regression: 162/162 across 21 suites on one frozen 44-file runtime set. Report: `training/b4artists_ml/results/transition-window-affected-v1-regression.json`.
- Foreground Bforartists journey: visible Departure/Arrival controls, native Undo/Redo, destination-owned preview behavior, Discard, and bounded source Action recovery passed. Report: `docs/b4artists_ml/transition-window-ui-v1.json`.
- Screenshot: `training/b4artists_ml/cache/transition-window-ui-v1.png`.

Every host assertion and evidence write completed. The Bforartists Alpha processes then followed the known `ucrtbase.dll` shutdown-fault path, so clean process exit is not claimed.

## Claim boundary

This is deterministic animator-authored timing assistance. It does not learn timing, infer motion intent or style, move priority-pose frames, establish independent usability, or satisfy learned-inbetweening and Cascadeur-comparison requirements.
